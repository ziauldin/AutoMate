import os
import logging
import uuid
import json
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func
# Your modules
from app.llm.diagnose_llm import DiagnoseLLM
from app.recommend.recommend import recommend_products
from app.auth.google import router as auth_router, get_current_user, UserInfo
from app.database import get_db, engine, Base
from app.models import ChatSession, Message
# Load environment variables
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
# Initialize FastAPI
app = FastAPI(title="Car Diagnostics API")
# Session middleware (for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "change-me-in-production"),
    max_age=3600,
)
# CORS settings
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8500",
    "http://127.0.0.1:8500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include authentication routes
app.include_router(auth_router)
# Static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# Initialize your LLM
diagnose_llm = DiagnoseLLM()
# Pydantic schemas
class CarDetails(BaseModel):
    manufacturer: str
    model: str
    year: int

class ChatRequest(BaseModel):
    session_id: str
    message: str

class TextSizeRequest(BaseModel):
    session_id: str
    size: str

# Create tables at startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

# Root endpoint
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Start a new chat session
@app.post("/api/session")
async def create_new_session(
    car_details: CarDetails,
    request: Request,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        session_id = str(uuid.uuid4())
        db_session = ChatSession(
            id=session_id,
            user_id=user.id,
            manufacturer=car_details.manufacturer,
            model=car_details.model,
            year=car_details.year,
        )
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        # Add initial system message with car details
        system_msg = Message(
            session_id=session_id,
            role="system",
            content=f"Vehicle: {car_details.year} {car_details.manufacturer} {car_details.model}",
            timestamp=datetime.now(timezone.utc).astimezone(timezone.utc).replace(tzinfo=None)
        )
        db.add(system_msg)
        # Add welcome message
        welcome_msg = Message(
            session_id=session_id,
            role="assistant",
            content=f"Hello! I'm ready to help with your {car_details.year} {car_details.manufacturer} {car_details.model}. What issues are you experiencing?",
            timestamp=datetime.now(timezone.utc).astimezone(timezone.utc).replace(tzinfo=None)
        )
        db.add(welcome_msg)
        await db.commit()
        logger.info(f"Created session {session_id} for {car_details.year} {car_details.manufacturer} {car_details.model}")
        return {"session_id": session_id, "car_details": car_details}
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/api/chat")
async def chat(
    chat_req: ChatRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Load session
        res = await db.execute(select(ChatSession).where(ChatSession.id == chat_req.session_id))
        session = res.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        # Get the conversation history for this session
        msg_res = await db.execute(
            select(Message).where(Message.session_id == session.id).order_by(Message.timestamp)
        )
        history_messages = msg_res.scalars().all()
        # Prepare message history
        messages = []
        # Add historical messages
        for msg in history_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        # Add the new user message
        messages.append({
            "role": "user",
            "content": chat_req.message
        })
        # Persist user message to database
        user_msg = Message(
            session_id=session.id,
            role="user",
            content=chat_req.message,
            timestamp=datetime.now(timezone.utc).astimezone(timezone.utc).replace(tzinfo=None),
        )
        db.add(user_msg)
        await db.flush()
        # Call DiagnoseLLM with the full message history and session context
        diagnosis = await diagnose_llm.get_diagnosis(messages, session)
        # Get recommendations based on the diagnosis
        products = recommend_products(diagnosis, top_k=3)
        # Prepare assistant message content
        assist_content = diagnosis
        if products:
            assist_content += "\n\n**Recommended Products:**\n"
            for product in products:
                assist_content += f"1. {product['title']} by {product['manufacturer']} (${product['price']})\n  URL: {product['url']}\n"
        # Persist assistant message
        assist_msg = Message(
            session_id=session.id,
            role="assistant",
            content=assist_content,
            timestamp=datetime.now(timezone.utc).astimezone(timezone.utc).replace(tzinfo=None),
            products=json.dumps(products) if products else None,
        )
        db.add(assist_msg)
        await db.commit()
        return {"message": assist_content, "products": products}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Set text size preference
@app.post("/api/set-text-size")
async def set_text_size(
    req: TextSizeRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        res = await db.execute(select(ChatSession).where(ChatSession.id == req.session_id))
        session = res.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        session.text_size = req.size
        await db.commit()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set text-size error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get list of sessions (history)
@app.get("/api/history")
async def get_history(
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        res = await db.execute(
            select(ChatSession).where(ChatSession.user_id == user.id).order_by(desc(ChatSession.created_at))
        )
        sessions = res.scalars().all()
        history = []
        for sess in sessions:
            # Last message
            last_res = await db.execute(
                select(Message).where(Message.session_id == sess.id).order_by(desc(Message.timestamp)).limit(1)
            )
            last = last_res.scalars().first()
            # Count messages
            message_count = await db.scalar(
                select(func.count()).select_from(Message).where(Message.session_id == sess.id)
            )
            history.append({
                "id": sess.id,
                "car_details": {"manufacturer": sess.manufacturer, "model": sess.model, "year": sess.year},
                "created_at": sess.created_at.isoformat(),
                "last_message": last.content if last else "",
                "message_count": message_count,
            })
        return {"sessions": history}
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific session's full history
@app.get("/api/history/{session_id}")
async def get_session_history(
    session_id: str,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        res = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = res.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        msg_res = await db.execute(
            select(Message).where(Message.session_id == session.id).order_by(Message.timestamp)
        )
        messages = msg_res.scalars().all()
        return {
            "id": session.id,
            "car_details": {"manufacturer": session.manufacturer, "model": session.model, "year": session.year},
            "created_at": session.created_at.isoformat(),
            "text_size": session.text_size,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "products": json.loads(m.products) if m.products else None
                }
                for m in messages
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Clear all history for a user
@app.post("/api/clear-history")
async def clear_history(
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        res = await db.execute(select(ChatSession).where(ChatSession.user_id == user.id))
        sessions = res.scalars().all()
        for sess in sessions:
            await db.delete(sess)
        await db.commit()
        return {"success": True}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Image upload endpoint
@app.post("/api/upload-image")
async def upload_image(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        res = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = res.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        os.makedirs("static/uploads", exist_ok=True)
        path = f"static/uploads/{session_id}_{file.filename}"
        with open(path, "wb") as f:
            f.write(await file.read())
        return {"success": True, "file_url": f"/{path}"}
    except Exception as e:
        logger.error(f"Upload image error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

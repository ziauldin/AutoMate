import os
import sys]
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

import spacy
import nest_asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.models.db_models import ChatLog, Product
from app.llm.diagnose_llm import get_llm_diagnosis
import uvicorn
# App & Templating
app = FastAPI()
nest_asyncio.apply()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# spaCy
nlp = spacy.load("en_core_web_sm")

# Schema
class DiagnoseInput(BaseModel):
    issue: str

class RecommendInput(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/diagnose")
async def diagnose_vehicle(input: DiagnoseInput):
    db: Session = SessionLocal()
    try:
        diagnosis = get_llm_diagnosis(input.issue)

        # Fetch related products
        keywords = diagnosis.lower().split()
        matched_products = db.query(Product).filter(
            Product.title.ilike(f"%{keywords[0]}%")
        ).limit(5).all()

        product_total = sum([float(p.price) for p in matched_products if p.price and str(p.price).isdigit()])
        estimated_cost = product_total + 2000  # Labor cost estimate

        chat = ChatLog(
            user_input=input.issue,
            diagnosis=diagnosis,
            model_used="gemma-2b"
        )
        db.add(chat)
        db.commit()

        return {
            "translated": input.issue,
            "diagnosis": diagnosis,
            "estimated_cost": f"{int(estimated_cost)}",
            "products": [
                {
                    "title": p.title,
                    "price": p.price,
                    "url": p.url,
                    "manufacturer": p.manufacturer
                } for p in matched_products
            ]
        }

    finally:
        db.close()

@app.post("/recommend")
async def recommend_parts(input: RecommendInput):
    db: Session = SessionLocal()
    try:
        results = db.query(Product).filter(
            Product.title.ilike(f"%{input.query}%")
        ).limit(5).all()

        return {
            "results": [
                {
                    "title": p.title,
                    "price": p.price,
                    "url": p.url,
                    "manufacturer": p.manufacturer
                } for p in results
            ]
        }
    finally:
        db.close()

# Optional for local testing
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=7860, reload=True)

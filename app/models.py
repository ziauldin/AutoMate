import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
class Product(Base):
    __tablename__ = "products"
    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title        = Column(String, nullable=False)
    details      = Column(Text,   nullable=True)
    manufacturer = Column(String, nullable=True)
    price        = Column(Integer,  nullable=False)
    url          = Column(String, nullable=True)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    text_size = Column(String, default="xxlarge")
    
    # Relationship to Message
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.timestamp")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    car_image = Column(String, nullable=True)
    products = Column(Text, nullable=True)  # JSON string of product recommendations
    
    # Relationship to ChatSession
    session = relationship("ChatSession", back_populates="messages")
import os
import asyncio
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./cro_analyzer.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class WebsiteAnalysis(Base):
    __tablename__ = "website_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False, index=True)
    overall_score = Column(Integer, nullable=False)
    
    # Category scores
    product_page_score = Column(Integer, default=0)
    cart_page_score = Column(Integer, default=0)
    mobile_score = Column(Integer, default=0)
    trust_signals_score = Column(Integer, default=0)
    coupons_score = Column(Integer, default=0)
    delivery_score = Column(Integer, default=0)
    
    # JSON data
    html_elements = Column(JSON)
    ai_insights = Column(JSON)
    recommendations = Column(JSON)
    models_used = Column(JSON)
    
    # Metadata
    analysis_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
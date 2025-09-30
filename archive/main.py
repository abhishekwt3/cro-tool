#!/usr/bin/env python3
"""
CRO Analyzer - Python FastAPI Backend
AI-Powered Conversion Rate Optimization Analysis
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import init_db
from app.models import CROAnalysisRequest, CROAnalysisResponse
from app.services.analysis_engine import CROAnalysisEngine
from app.services.cache_service import CacheService
from app.vision.vision_manager import VisionManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
analysis_engine = None
cache_service = None
vision_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global analysis_engine, cache_service, vision_manager
    
    logger.info("🚀 Starting CRO Analyzer Backend...")
    
    # Initialize database
    await init_db()
    
    # Initialize services
    cache_service = CacheService()
    vision_manager = VisionManager()
    analysis_engine = CROAnalysisEngine(cache_service, vision_manager)
    
    # Initialize AI models
    await vision_manager.initialize_models()
    
    logger.info("✅ Backend initialized successfully!")
    logger.info(f"📊 Enabled AI models: {vision_manager.get_enabled_models()}")
    
    yield
    
    # Cleanup
    if cache_service:
        await cache_service.close()
    logger.info("👋 Backend shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="CRO Analyzer API",
    description="AI-Powered Conversion Rate Optimization Analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "CRO Analyzer Backend",
        "version": "2.0.0",
        "status": "healthy",
        "enabled_models": vision_manager.get_enabled_models() if vision_manager else []
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    models_status = {}
    if vision_manager:
        models_status = await vision_manager.get_models_status()
    
    return {
        "status": "healthy",
        "models": models_status,
        "database": "sqlite",
        "cache": "redis" if cache_service and cache_service.is_connected() else "memory"
    }

@app.get("/api/models")
async def get_enabled_models():
    """Get list of enabled AI models"""
    if not vision_manager:
        return {"enabled_models": [], "total": 0}
    
    models = vision_manager.get_enabled_models()
    status = await vision_manager.get_models_status()
    
    return {
        "enabled_models": models,
        "total_models": len(models),
        "models_status": status,
        "message": "To enable/disable models, edit app/vision/vision_manager.py"
    }

@app.post("/api/analyze", response_model=CROAnalysisResponse)
async def analyze_website(request: CROAnalysisRequest):
    """Analyze website for CRO optimization"""
    try:
        # Convert Pydantic HttpUrl to string
        url_str = str(request.url)
        logger.info(f"🔍 Starting analysis for: {url_str}")
        
        if not analysis_engine:
            raise HTTPException(status_code=500, detail="Analysis engine not initialized")
        
        # Run analysis with string URL
        result = await analysis_engine.analyze_website(
            url=url_str,
            client_name=request.client_name
        )
        
        logger.info(f"✅ Analysis completed for {url_str} - Score: {result.overall_score}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Analysis failed for {str(request.url)}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.websocket("/api/analyze/ws")
async def analyze_website_realtime(websocket: WebSocket):
    """Real-time website analysis with progress updates"""
    await websocket.accept()
    
    try:
        # Get URL from query params
        url = websocket.query_params.get("url")
        if not url:
            await websocket.send_json({"error": "URL parameter required"})
            return
        
        logger.info(f"🔄 Starting real-time analysis for: {url}")
        
        # Send progress updates
        await websocket.send_json({
            "status": "started",
            "message": "Initializing analysis...",
            "progress": 10
        })
        
        await websocket.send_json({
            "status": "capturing",
            "message": "Capturing website screenshot...",
            "progress": 30
        })
        
        await websocket.send_json({
            "status": "extracting",
            "message": "Extracting HTML elements...",
            "progress": 50
        })
        
        await websocket.send_json({
            "status": "analyzing",
            "message": f"Running AI analysis with {len(vision_manager.get_enabled_models())} models...",
            "progress": 70
        })
        
        # Run actual analysis (URL is already a string from query params)
        result = await analysis_engine.analyze_website(url)
        
        await websocket.send_json({
            "status": "complete",
            "message": "Analysis completed successfully!",
            "progress": 100,
            "report": result.model_dump(),  # Updated for Pydantic v2
            "models_used": result.models_used
        })
        
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket analysis failed: {str(e)}")
        await websocket.send_json({
            "status": "error",
            "error": str(e)
        })

@app.get("/api/reports")
async def get_reports(url: str = None):
    """Get analysis reports for a URL"""
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter required")
    
    # TODO: Implement database query for historical reports
    return {"reports": [], "message": "Historical reports feature coming soon"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
#!/usr/bin/env python3
"""
Enhanced CRO Analyzer - Python FastAPI Backend
AI-Powered (Gemini) + Framework-Based Conversion Rate Optimization Analysis
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
from app.services.cache_service import CacheService

# Import enhanced components directly (no fallback)
from enhanced_vision_manager import EnhancedVisionManager
from enhanced_analysis_engine import EnhancedCROAnalysisEngine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
analysis_engine = None
cache_service = None
vision_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize enhanced services on startup"""
    global analysis_engine, cache_service, vision_manager
    
    logger.info("🚀 Starting Enhanced CRO Analyzer Backend...")
    logger.info("🤖 AI Model: Gemini 2.5 Pro Vision")
    logger.info("📊 Framework: 5-Point CRO Analysis")
    
    # Initialize database
    await init_db()
    
    # Initialize services
    cache_service = CacheService()
    vision_manager = EnhancedVisionManager()
    analysis_engine = EnhancedCROAnalysisEngine(cache_service, vision_manager)
    
    # Initialize AI models and framework
    await vision_manager.initialize_models()
    
    enabled_methods = vision_manager.get_enabled_models()
    logger.info("✅ Backend initialized successfully!")
    logger.info(f"📊 Enabled analysis methods: {enabled_methods}")
    logger.info("🎯 CRO Framework: Navigation | Display | Information | Technical | Psychological")
    
    yield
    
    # Cleanup
    if cache_service:
        await cache_service.close()
    if analysis_engine:
        await analysis_engine.close()
    logger.info("👋 Backend shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Enhanced CRO Analyzer API",
    description="AI-Powered (Gemini) + Framework-Based Conversion Rate Optimization Analysis",
    version="3.0.0",
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
    """Enhanced health check endpoint"""
    return {
        "message": "Enhanced CRO Analyzer Backend",
        "version": "3.0.0",
        "status": "healthy",
        "features": [
            "Gemini 2.5 Pro Vision Analysis",
            "5-Point CRO Framework",
            "Screenshot Analysis",
            "HTML Element Detection",
            "Mobile Optimization Check"
        ],
        "enabled_methods": vision_manager.get_enabled_models() if vision_manager else [],
        "framework_categories": ["navigation", "display", "information", "technical", "psychological"]
    }

@app.get("/health")
async def enhanced_health_check():
    """Detailed health check with framework status"""
    models_status = {}
    if vision_manager:
        models_status = await vision_manager.get_models_status()
    
    return {
        "status": "healthy",
        "enhanced_features": True,
        "models": models_status,
        "database": "sqlite",
        "cache": "redis" if cache_service and cache_service.is_connected() else "memory",
        "framework_enabled": True,
        "total_analysis_methods": len(vision_manager.get_enabled_models()) if vision_manager else 0
    }

@app.get("/api/models")
async def get_enabled_models():
    """Get detailed list of enabled analysis methods"""
    if not vision_manager:
        return {"enabled_methods": [], "total": 0}
    
    methods = vision_manager.get_enabled_models()
    status = await vision_manager.get_models_status()
    
    return {
        "enabled_methods": methods,
        "total_methods": len(methods),
        "enhanced_features": True,
        "methods_status": status,
        "framework_integration": "active",
        "framework_categories": {
            "navigation": "Breadcrumbs, navigation depth, menu complexity",
            "display": "Fonts, whitespace, element spacing, visual hierarchy",
            "information": "Product descriptions, images, offers, content completeness",
            "technical": "Page speed, mobile optimization, performance metrics",
            "psychological": "Trust signals, return policy, FAQ, color consistency"
        }
    }

@app.post("/api/analyze", response_model=CROAnalysisResponse)
async def analyze_website_enhanced(request: CROAnalysisRequest):
    """Enhanced website analysis with Gemini + Framework"""
    try:
        url_str = str(request.url)
        logger.info(f"🔍 Starting enhanced analysis for: {url_str}")
        
        if not analysis_engine:
            raise HTTPException(status_code=500, detail="Analysis engine not initialized")
        
        # Run analysis
        result = await analysis_engine.analyze_website(
            url=url_str,
            client_name=request.client_name
        )
        
        logger.info(f"✅ Analysis completed for {url_str}")
        logger.info(f"📊 Overall Score: {result.overall_score}")
        logger.info(f"🎯 Methods Used: {result.models_used}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Analysis failed for {str(request.url)}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.websocket("/api/analyze/ws")
async def analyze_website_realtime(websocket: WebSocket):
    """Real-time website analysis with detailed progress"""
    await websocket.accept()
    
    try:
        # Get URL from query params
        url = websocket.query_params.get("url")
        if not url:
            await websocket.send_json({"error": "URL parameter required"})
            return
        
        logger.info(f"🔄 Starting real-time analysis for: {url}")
        
        # Progress updates
        await websocket.send_json({
            "status": "started",
            "message": "Initializing CRO analysis with Gemini AI...",
            "progress": 5,
            "current_step": "initialization"
        })
        
        await websocket.send_json({
            "status": "framework_setup",
            "message": "Setting up 5-Point CRO framework analysis...",
            "progress": 15,
            "current_step": "framework"
        })
        
        await websocket.send_json({
            "status": "capturing",
            "message": "Capturing website screenshots...",
            "progress": 25,
            "current_step": "screenshots"
        })
        
        await websocket.send_json({
            "status": "scraping",
            "message": "Extracting HTML elements...",
            "progress": 45,
            "current_step": "scraping"
        })
        
        await websocket.send_json({
            "status": "framework_analysis",
            "message": "Analyzing navigation, display, information, technical, and psychological factors...",
            "progress": 65,
            "current_step": "framework_analysis"
        })
        
        await websocket.send_json({
            "status": "ai_analysis",
            "message": "Running Gemini Pro Vision analysis...",
            "progress": 80,
            "current_step": "ai_analysis"
        })
        
        await websocket.send_json({
            "status": "combining",
            "message": "Combining Framework + AI insights...",
            "progress": 90,
            "current_step": "combining"
        })
        
        # Run actual analysis
        result = await analysis_engine.analyze_website(url)
        
        await websocket.send_json({
            "status": "complete",
            "message": f"Analysis completed! Score: {result.overall_score}/100",
            "progress": 100,
            "current_step": "complete",
            "report": result.model_dump(),
            "analysis_summary": {
                "overall_score": result.overall_score,
                "methods_used": result.models_used,
                "recommendations_count": len(result.recommendations),
                "enhanced_features": True
            }
        })
        
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket analysis failed: {str(e)}")
        await websocket.send_json({
            "status": "error",
            "error": str(e),
            "message": "Analysis failed"
        })

@app.get("/api/framework/categories")
async def get_framework_categories():
    """Get detailed information about framework categories"""
    return {
        "framework_version": "1.0",
        "categories": {
            "navigation": {
                "description": "Navigation complexity and user path analysis",
                "metrics": ["breadcrumbs", "navigation_depth", "menu_complexity"],
                "impact": "Affects user flow and bounce rate"
            },
            "display": {
                "description": "Visual design and layout optimization",
                "metrics": ["font_count", "whitespace", "element_spacing", "color_consistency"],
                "impact": "Influences visual hierarchy and user engagement"
            },
            "information": {
                "description": "Content completeness and product information",
                "metrics": ["product_descriptions", "image_count", "offers", "title_clarity"],
                "impact": "Builds trust and reduces purchase hesitation"
            },
            "technical": {
                "description": "Performance and mobile optimization",
                "metrics": ["page_speed", "mobile_responsiveness", "image_optimization"],
                "impact": "Affects user experience and SEO rankings"
            },
            "psychological": {
                "description": "Trust signals and user psychology",
                "metrics": ["trust_badges", "return_policy", "faq", "social_proof"],
                "impact": "Reduces anxiety and increases conversion confidence"
            }
        },
        "scoring": {
            "range": "0-100 per category",
            "interpretation": {
                "90-100": "Excellent - Best practices implemented",
                "80-89": "Good - Minor improvements needed",
                "70-79": "Average - Several optimization opportunities",
                "60-69": "Below Average - Significant improvements required",
                "0-59": "Poor - Major issues that need immediate attention"
            }
        }
    }

@app.get("/api/framework/status")
async def get_framework_status():
    """Get framework analysis status"""
    return {
        "framework_enabled": True,
        "categories": ["navigation", "display", "information", "technical", "psychological"],
        "version": "1.0",
        "integration_status": "active",
        "ai_model": "Gemini 2.5 Pro Vision"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Enhanced CRO Analyzer Backend...")
    print("📊 Features: 5-Point Framework + Gemini Pro Vision")
    print("🎯 Framework Categories: Navigation | Display | Information | Technical | Psychological")
    print("🤖 AI Model: Gemini 2.5 Pro Vision")
    
    uvicorn.run(
        "enhanced_main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
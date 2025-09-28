#!/usr/bin/env python3
"""
Enhanced CRO Analyzer - Python FastAPI Backend
AI-Powered + Framework-Based Conversion Rate Optimization Analysis
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from typing import Optional

from app.database import init_db
from app.enhanced_models import (
    CROAnalysisRequest, CROAnalysisResponse, EnhancedAnalysisRequest,
    FrameworkOnlyResponse, HealthCheckResponse, ModelStatus
)
from app.services.enhanced_analysis_engine import EnhancedCROAnalysisEngine
from app.services.cache_service import CacheService
from app.vision.enhanced_vision_manager import EnhancedVisionManager

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
    
    # Initialize database
    await init_db()
    
    # Initialize enhanced services
    cache_service = CacheService()
    vision_manager = EnhancedVisionManager()
    analysis_engine = EnhancedCROAnalysisEngine(cache_service, vision_manager)
    
    # Initialize AI models and framework
    await vision_manager.initialize_models()
    
    enabled_methods = vision_manager.get_enabled_models()
    logger.info("✅ Enhanced backend initialized successfully!")
    logger.info(f"📊 Enabled analysis methods: {enabled_methods}")
    logger.info("🎯 CRO Framework Integration: Active")
    logger.info("📋 5-Point Framework: Navigation | Display | Information | Technical | Psychological")
    
    yield
    
    # Cleanup
    if cache_service:
        await cache_service.close()
    if analysis_engine:
        await analysis_engine.close()
    logger.info("👋 Enhanced backend shutdown complete")

# Create enhanced FastAPI app
app = FastAPI(
    title="Enhanced CRO Analyzer API",
    description="AI-Powered + Framework-Based Conversion Rate Optimization Analysis",
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
            "CRO Framework Analysis (5-Point)",
            "Claude Vision AI",
            "YOLOv8 Computer Vision",
            "Combined Insights Engine"
        ],
        "enabled_methods": vision_manager.get_enabled_models() if vision_manager else [],
        "framework_categories": ["navigation", "display", "information", "technical", "psychological"]
    }

@app.get("/health", response_model=HealthCheckResponse)
async def enhanced_health_check():
    """Detailed health check with framework status"""
    models_status = {}
    if vision_manager:
        models_status = await vision_manager.get_models_status()
    
    # Convert to ModelStatus objects
    model_statuses = {}
    for name, status in models_status.items():
        model_statuses[name] = ModelStatus(**status)
    
    return HealthCheckResponse(
        status="healthy",
        models=model_statuses,
        database="sqlite",
        cache="redis" if cache_service and cache_service.is_connected() else "memory",
        framework_enabled=True,
        total_analysis_methods=len(vision_manager.get_enabled_models()) if vision_manager else 0
    )

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
        "methods_status": status,
        "framework_integration": "active",
        "framework_categories": {
            "navigation": "Breadcrumbs, navigation depth, menu complexity",
            "display": "Fonts, whitespace, element spacing, visual hierarchy",
            "information": "Product descriptions, images, offers, content completeness",
            "technical": "Page speed, mobile optimization, performance metrics",
            "psychological": "Trust signals, return policy, FAQ, color consistency"
        },
        "configuration": {
            "file": "app/vision/vision_manager.py",
            "message": "To enable/disable models, edit ENABLE_* variables"
        }
    }

@app.post("/api/analyze", response_model=CROAnalysisResponse)
async def analyze_website_enhanced(request: CROAnalysisRequest):
    """Enhanced website analysis with framework integration"""
    try:
        url_str = str(request.url)
        logger.info(f"🔍 Starting enhanced analysis for: {url_str}")
        
        if not analysis_engine:
            raise HTTPException(status_code=500, detail="Enhanced analysis engine not initialized")
        
        # Run enhanced analysis
        result = await analysis_engine.analyze_website(
            url=url_str,
            client_name=request.client_name
        )
        
        logger.info(f"✅ Enhanced analysis completed for {url_str}")
        logger.info(f"📊 Overall Score: {result.overall_score}")
        logger.info(f"🎯 Methods Used: {result.models_used}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced analysis failed for {str(request.url)}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")

@app.post("/api/analyze/comprehensive", response_model=CROAnalysisResponse)
async def analyze_website_comprehensive(request: EnhancedAnalysisRequest):
    """Comprehensive analysis with configurable options"""
    try:
        url_str = str(request.url)
        logger.info(f"🔍 Starting comprehensive analysis for: {url_str}")
        logger.info(f"⚙️  Analysis type: {request.analysis_type}")
        
        if not analysis_engine:
            raise HTTPException(status_code=500, detail="Analysis engine not initialized")
        
        # TODO: Implement analysis type filtering based on request.analysis_type
        # For now, run full analysis
        result = await analysis_engine.analyze_website(
            url=url_str,
            client_name=request.client_name
        )
        
        logger.info(f"✅ Comprehensive analysis completed for {url_str}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Comprehensive analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.websocket("/api/analyze/ws")
async def analyze_website_realtime_enhanced(websocket: WebSocket):
    """Enhanced real-time website analysis with detailed progress"""
    await websocket.accept()
    
    try:
        # Get URL from query params
        url = websocket.query_params.get("url")
        if not url:
            await websocket.send_json({"error": "URL parameter required"})
            return
        
        logger.info(f"🔄 Starting enhanced real-time analysis for: {url}")
        
        # Enhanced progress updates
        await websocket.send_json({
            "status": "started",
            "message": "Initializing enhanced CRO analysis...",
            "progress": 5,
            "current_step": "initialization"
        })
        
        await websocket.send_json({
            "status": "framework_setup",
            "message": "Setting up CRO framework analysis...",
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
            "message": "Extracting HTML elements and running framework analysis...",
            "progress": 45,
            "current_step": "scraping"
        })
        
        await websocket.send_json({
            "status": "framework_analysis",
            "message": "Analyzing navigation, display, information, technical, and psychological factors...",
            "progress": 65,
            "current_step": "framework_analysis"
        })
        
        enabled_methods = vision_manager.get_enabled_models()
        await websocket.send_json({
            "status": "ai_analysis",
            "message": f"Running AI analysis with {len(enabled_methods)} methods: {', '.join(enabled_methods)}",
            "progress": 80,
            "current_step": "ai_analysis"
        })
        
        await websocket.send_json({
            "status": "combining",
            "message": "Combining framework and AI insights...",
            "progress": 90,
            "current_step": "combining"
        })
        
        # Run actual enhanced analysis
        result = await analysis_engine.analyze_website(url)
        
        await websocket.send_json({
            "status": "complete",
            "message": f"Enhanced analysis completed! Score: {result.overall_score}/100",
            "progress": 100,
            "current_step": "complete",
            "report": result.model_dump(),
            "analysis_summary": {
                "overall_score": result.overall_score,
                "methods_used": result.models_used,
                "recommendations_count": len(result.recommendations),
                "framework_categories": len([cat for cat in ["navigation", "display", "information", "technical", "psychological"] 
                                           if cat in result.visual_analysis.category_scores])
            }
        })
        
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"Enhanced WebSocket analysis failed: {str(e)}")
        await websocket.send_json({
            "status": "error",
            "error": str(e),
            "message": "Enhanced analysis failed"
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

@app.get("/api/reports")
async def get_reports(url: Optional[str] = Query(None)):
    """Get analysis reports (placeholder for future implementation)"""
    if not url:
        return {
            "reports": [],
            "message": "Historical reports feature coming soon",
            "note": "Enhanced reports will include framework analysis trends"
        }
    
    # TODO: Implement historical report retrieval
    return {
        "url": url,
        "reports": [],
        "message": f"No historical reports found for {url}",
        "suggestion": "Run a new analysis to generate a report"
    }

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary (placeholder)"""
    return {
        "message": "Analytics feature coming soon",
        "planned_features": [
            "Framework category trends",
            "Common issues across sites",
            "Improvement recommendations effectiveness",
            "Industry benchmarking"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Enhanced startup message
    print("🚀 Starting Enhanced CRO Analyzer Backend...")
    print("📊 Features: Framework Analysis + AI Models")
    print("🎯 Framework: 5-Point CRO Analysis")
    print("🤖 AI Models: Claude Vision + YOLOv8")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
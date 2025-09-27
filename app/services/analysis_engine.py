"""Main analysis engine for CRO website analysis"""

import uuid
import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker

from app.models import CROAnalysisResponse, CategoryScores
from app.services.cache_service import CacheService
from app.services.screenshot_service import ScreenshotService
from app.services.scraping_service import ScrapingService
from app.vision.vision_manager import VisionManager
from app.database import async_session, WebsiteAnalysis

logger = logging.getLogger(__name__)

class CROAnalysisEngine:
    """Main engine for running CRO analysis"""
    
    def __init__(self, cache_service: CacheService, vision_manager: VisionManager):
        self.cache_service = cache_service
        self.vision_manager = vision_manager
        self.screenshot_service = ScreenshotService()
        self.scraping_service = ScrapingService()
        
    async def analyze_website(self, url: str, client_name: str = None) -> CROAnalysisResponse:
        """Run complete CRO analysis on a website"""
        logger.info(f"🔍 Starting CRO analysis for: {url}")
        
        # Check cache first
        cached_result = await self.cache_service.get_cached_analysis(url)
        if cached_result:
            logger.info(f"📦 Returning cached analysis for: {url}")
            return cached_result
        
        # Initialize services
        await self._initialize_services()
        
        # Run data collection in parallel
        screenshot_task = asyncio.create_task(self._capture_screenshots(url))
        html_task = asyncio.create_task(self._extract_html_elements(url))
        
        # Wait for both tasks
        screenshot_data, html_data = await asyncio.gather(
            screenshot_task, html_task, return_exceptions=True
        )
        
        # Handle errors gracefully
        if isinstance(screenshot_data, Exception):
            logger.error(f"Screenshot capture failed: {screenshot_data}")
            screenshot_data = (None, None)
        
        if isinstance(html_data, Exception):
            logger.error(f"HTML extraction failed: {html_data}")
            from app.models import CROData
            html_data = CROData()
        
        # Run AI analysis
        if screenshot_data and screenshot_data[0]:  # Desktop screenshot
            ai_insights = await self.vision_manager.analyze_with_all_models(
                screenshot_data[0], html_data
            )
        else:
            ai_insights = await self.vision_manager.analyze_with_all_models(
                b'', html_data  # Empty screenshot
            )
        
        # Generate final report
        report = CROAnalysisResponse(
            id=str(uuid.uuid4()),
            url=url,
            overall_score=ai_insights.overall_score,
            category_scores=CategoryScores(**ai_insights.category_scores),
            visual_analysis=ai_insights,
            element_analysis=html_data,
            recommendations=ai_insights.recommendations,
            models_used=self.vision_manager.get_enabled_models(),
            analysis_date=datetime.utcnow()
        )
        
        # Cache and store results
        await self.cache_service.cache_analysis(url, report)
        await self._store_analysis(report)
        
        logger.info(f"✅ Analysis completed for {url} - Score: {report.overall_score}")
        return report
    
    async def _initialize_services(self):
        """Initialize services if not already done"""
        try:
            await self.screenshot_service.initialize()
            await self.scraping_service.initialize()
            await self.cache_service.initialize()
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
    
    async def _capture_screenshots(self, url: str):
        """Capture website screenshots"""
        try:
            return await self.screenshot_service.capture_website(url)
        except Exception as e:
            logger.error(f"Screenshot capture failed for {url}: {e}")
            return None, None
    
    async def _extract_html_elements(self, url: str):
        """Extract HTML/DOM elements"""
        try:
            return await self.scraping_service.extract_cro_elements(url)
        except Exception as e:
            logger.error(f"HTML extraction failed for {url}: {e}")
            from app.models import CROData
            return CROData()  # Return empty data
    
    async def _store_analysis(self, report: CROAnalysisResponse):
        """Store analysis in database"""
        try:
            async with async_session() as session:
                analysis = WebsiteAnalysis(
                    url=report.url,
                    overall_score=report.overall_score,
                    product_page_score=report.category_scores.product_page,
                    cart_page_score=report.category_scores.cart_page,
                    mobile_score=report.category_scores.mobile,
                    trust_signals_score=report.category_scores.trust_signals,
                    coupons_score=report.category_scores.coupons,
                    delivery_score=report.category_scores.delivery,
                    html_elements=report.element_analysis.model_dump(),  # Updated for Pydantic v2
                    ai_insights=report.visual_analysis.model_dump(),     # Updated for Pydantic v2
                    recommendations=[rec.model_dump() for rec in report.recommendations],  # Updated for Pydantic v2
                    models_used=report.models_used,
                    analysis_date=report.analysis_date
                )
                
                session.add(analysis)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to store analysis: {e}")
    
    async def close(self):
        """Close all services"""
        await self.screenshot_service.close()
        await self.scraping_service.close()
        await self.cache_service.close()
        await self.vision_manager.close()
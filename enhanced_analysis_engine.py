"""Enhanced Analysis Engine with CRO Framework Integration"""

import uuid
import asyncio
import logging
from datetime import datetime
from typing import Tuple

from app.models import CROAnalysisResponse, CategoryScores, AIInsights, CROData
from app.services.cache_service import CacheService
from app.services.screenshot_service import ScreenshotService
from enhanced_scraping_service import EnhancedScrapingService
from enhanced_vision_manager import EnhancedVisionManager
from app.database import async_session, WebsiteAnalysis

logger = logging.getLogger(__name__)

class EnhancedCROAnalysisEngine:
    """Enhanced CRO Analysis Engine with Framework Integration"""
    
    def __init__(self, cache_service: CacheService, vision_manager: EnhancedVisionManager):
        self.cache_service = cache_service
        self.vision_manager = vision_manager
        self.screenshot_service = ScreenshotService()
        self.scraping_service = EnhancedScrapingService()
        
    async def analyze_website(self, url: str, client_name: str = None) -> CROAnalysisResponse:
        """Run enhanced CRO analysis with framework integration"""
        logger.info(f"🔍 Starting enhanced CRO analysis for: {url}")
        
        # Check cache first
        cached_result = await self.cache_service.get_cached_analysis(url)
        if cached_result:
            logger.info(f"📦 Returning cached analysis for: {url}")
            return cached_result
        
        # Initialize services
        await self._initialize_services()
        
        # Run enhanced data collection
        screenshot_data, html_and_framework_data = await self._run_enhanced_collection(url)
        
        # Unpack the enhanced data
        html_data, framework_insights = html_and_framework_data
        
        # Run AI analysis with framework integration
        if screenshot_data and screenshot_data[0]:  # Desktop screenshot
            combined_insights = await self.vision_manager.analyze_with_all_models_and_framework(
                screenshot_data[0], html_data, framework_insights
            )
        else:
            combined_insights = await self.vision_manager.analyze_with_all_models_and_framework(
                b'', html_data, framework_insights
            )
        
        # Generate enhanced report
        report = await self._generate_enhanced_report(url, combined_insights, html_data)
        
        # Cache and store results
        await self.cache_service.cache_analysis(url, report)
        await self._store_enhanced_analysis(report, framework_insights)
        
        logger.info(f"✅ Enhanced analysis completed for {url}")
        logger.info(f"📊 Overall Score: {report.overall_score}")
        logger.info(f"📋 Generated {len(report.recommendations)} recommendations")
        logger.info(f"🎯 Analysis methods used: {report.models_used}")
        
        return report
    
    async def _run_enhanced_collection(self, url: str) -> Tuple[Tuple, Tuple[CROData, AIInsights]]:
        """Run enhanced data collection with framework analysis"""
        
        # Run screenshot capture and enhanced scraping in parallel
        screenshot_task = asyncio.create_task(self._capture_screenshots(url))
        scraping_task = asyncio.create_task(self._extract_enhanced_elements(url))
        
        # Wait for both tasks
        screenshot_data, html_and_framework_data = await asyncio.gather(
            screenshot_task, scraping_task, return_exceptions=True
        )
        
        # Handle errors gracefully
        if isinstance(screenshot_data, Exception):
            logger.error(f"Screenshot capture failed: {screenshot_data}")
            screenshot_data = (None, None)
        
        if isinstance(html_and_framework_data, Exception):
            logger.error(f"Enhanced extraction failed: {html_and_framework_data}")
            html_and_framework_data = (CROData(), AIInsights())
        
        return screenshot_data, html_and_framework_data
    
    async def _extract_enhanced_elements(self, url: str) -> Tuple[CROData, AIInsights]:
        """Extract elements with framework analysis"""
        try:
            return await self.scraping_service.extract_cro_elements_with_framework(url)
        except Exception as e:
            logger.error(f"Enhanced HTML extraction failed for {url}: {e}")
            return CROData(), AIInsights()
    
    async def _generate_enhanced_report(self, url: str, insights: AIInsights, html_data: CROData) -> CROAnalysisResponse:
        """Generate enhanced CRO analysis report"""
        
        # Map framework categories to legacy categories for compatibility
        legacy_scores = self._map_to_legacy_scores(insights.category_scores)
        
        # Prioritize and limit recommendations
        prioritized_recommendations = self._prioritize_recommendations(insights.recommendations)
        
        # Generate analysis metadata
        analysis_metadata = self._generate_analysis_metadata(insights)
        
        report = CROAnalysisResponse(
            id=str(uuid.uuid4()),
            url=url,
            overall_score=insights.overall_score,
            category_scores=CategoryScores(**legacy_scores),
            visual_analysis=insights,
            element_analysis=html_data,
            recommendations=prioritized_recommendations,
            models_used=self.vision_manager.get_enabled_models(),
            analysis_date=datetime.utcnow()
        )
        
        return report
    
    def _map_to_legacy_scores(self, category_scores: dict) -> dict:
        """Map framework categories to legacy categories for compatibility"""
        
        # Default legacy scores
        legacy_scores = {
            "product_page": 75,
            "cart_page": 75,
            "mobile": 75,
            "trust_signals": 75,
            "coupons": 75,
            "delivery": 75
        }
        
        # Map framework scores to legacy categories
        if "information" in category_scores:
            legacy_scores["product_page"] = category_scores["information"]
        
        if "psychological" in category_scores:
            legacy_scores["trust_signals"] = category_scores["psychological"]
        
        if "technical" in category_scores:
            legacy_scores["mobile"] = category_scores["technical"]
        
        if "navigation" in category_scores:
            # Navigation affects multiple areas
            legacy_scores["cart_page"] = (legacy_scores["cart_page"] + category_scores["navigation"]) // 2
        
        if "display" in category_scores:
            # Display affects visual presentation
            for category in ["product_page", "cart_page"]:
                legacy_scores[category] = (legacy_scores[category] + category_scores["display"]) // 2
        
        # Preserve any existing legacy scores
        for category, score in category_scores.items():
            if category in legacy_scores:
                legacy_scores[category] = score
        
        return legacy_scores
    
    def _prioritize_recommendations(self, recommendations: list) -> list:
        """Prioritize and limit recommendations"""
        
        # Sort by priority: high -> medium -> low
        priority_order = {"high": 1, "medium": 2, "low": 3}
        
        sorted_recs = sorted(
            recommendations,
            key=lambda r: (priority_order.get(r.priority, 4), r.category)
        )
        
        # Limit to top 15 recommendations to avoid overwhelming users
        return sorted_recs[:15]
    
    def _generate_analysis_metadata(self, insights: AIInsights) -> dict:
        """Generate metadata about the analysis"""
        metadata = {
            "framework_categories_analyzed": [],
            "ai_models_used": [],
            "total_issues_found": len(insights.visual_issues) + len(insights.mobile_issues),
            "high_priority_recommendations": len([r for r in insights.recommendations if r.priority == "high"]),
            "coverage_score": 0
        }
        
        # Identify framework categories
        framework_categories = ["navigation", "display", "information", "technical", "psychological"]
        for category in framework_categories:
            if category in insights.category_scores:
                metadata["framework_categories_analyzed"].append(category)
        
        # Calculate coverage score
        metadata["coverage_score"] = len(metadata["framework_categories_analyzed"]) * 20  # 20% per category
        
        # Identify AI models used
        if insights.claude_analysis:
            metadata["ai_models_used"].append("Claude Vision")
        if insights.yolo_analysis:
            metadata["ai_models_used"].append("YOLOv8")
        
        return metadata
    
    async def _store_enhanced_analysis(self, report: CROAnalysisResponse, framework_insights: AIInsights):
        """Store enhanced analysis in database"""
        try:
            async with async_session() as session:
                # Create enhanced analysis record
                analysis = WebsiteAnalysis(
                    url=report.url,
                    overall_score=report.overall_score,
                    product_page_score=report.category_scores.product_page,
                    cart_page_score=report.category_scores.cart_page,
                    mobile_score=report.category_scores.mobile,
                    trust_signals_score=report.category_scores.trust_signals,
                    coupons_score=report.category_scores.coupons,
                    delivery_score=report.category_scores.delivery,
                    html_elements=report.element_analysis.model_dump(),
                    ai_insights=report.visual_analysis.model_dump(),
                    recommendations=[rec.model_dump() for rec in report.recommendations],
                    models_used=report.models_used,
                    analysis_date=report.analysis_date
                )
                
                session.add(analysis)
                await session.commit()
                
                logger.info(f"💾 Enhanced analysis stored for {report.url}")
                
        except Exception as e:
            logger.error(f"Failed to store enhanced analysis: {e}")
    
    # Keep existing helper methods for compatibility
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
    
    async def close(self):
        """Close all services"""
        await self.screenshot_service.close()
        await self.scraping_service.close()
        await self.cache_service.close()
        await self.vision_manager.close()
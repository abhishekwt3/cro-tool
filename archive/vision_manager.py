"""Vision Manager - Easy AI Model Switching"""

import logging
from typing import List, Dict, Any
import asyncio

from app.models import AIInsights, CROData
from archive.claude_model import ClaudeVisionModel
from app.vision.yolo_model import YOLOVisionModel

logger = logging.getLogger(__name__)

# ====================================================================
# 🎛️ VISION MODEL CONFIGURATION - ENABLE/DISABLE MODELS HERE
# ====================================================================

# Enable/Disable Models by changing these values
ENABLE_CLAUDE_VISION = False   # Set to False to disable Claude
ENABLE_YOLO_VISION = True     # Set to False to disable YOLOv8

# Alternative: Comment/uncomment these lines instead
# ENABLE_CLAUDE_VISION = False  # Claude disabled
# ENABLE_YOLO_VISION = False    # YOLOv8 disabled

# ====================================================================

class VisionManager:
    """Manages multiple AI vision models for CRO analysis"""
    
    def __init__(self):
        self.models = []
        self.claude_model = None
        self.yolo_model = None
        
    async def initialize_models(self):
        """Initialize enabled AI models"""
        logger.info("🤖 Initializing AI vision models...")
        
        # Initialize Claude Vision Model
        if ENABLE_CLAUDE_VISION:
            try:
                self.claude_model = ClaudeVisionModel()
                await self.claude_model.initialize()
                if self.claude_model.is_enabled():
                    self.models.append(self.claude_model)
                    logger.info("✅ Claude Vision Model enabled")
                else:
                    logger.warning("⚠️  Claude Vision Model disabled (no API key)")
            except Exception as e:
                logger.error(f"❌ Claude Vision Model failed to initialize: {e}")
        else:
            logger.info("🚫 Claude Vision Model disabled by configuration")
        
        # Initialize YOLOv8 Vision Model
        if ENABLE_YOLO_VISION:
            try:
                self.yolo_model = YOLOVisionModel()
                await self.yolo_model.initialize()
                self.models.append(self.yolo_model)
                logger.info("✅ YOLOv8 Vision Model enabled")
            except Exception as e:
                logger.error(f"❌ YOLOv8 Vision Model failed to initialize: {e}")
        else:
            logger.info("🚫 YOLOv8 Vision Model disabled by configuration")
        
        # ====================================================================
        # 🔧 ADD MORE AI MODELS HERE
        # ====================================================================
        
        # Example: Add GPT-4 Vision, BLIP, or other models
        # if ENABLE_GPT4_VISION:
        #     self.gpt4_model = GPT4VisionModel()
        #     await self.gpt4_model.initialize()
        #     self.models.append(self.gpt4_model)
        
        logger.info(f"🎯 Vision Manager initialized with {len(self.models)} models: {self.get_enabled_models()}")
    
    async def analyze_with_all_models(self, screenshot: bytes, html_data: CROData) -> AIInsights:
        """Run analysis with all enabled models"""
        if not self.models:
            return self._get_fallback_analysis(html_data)
        
        # Run all models concurrently
        tasks = []
        for model in self.models:
            task = asyncio.create_task(model.analyze_screenshot(screenshot, html_data))
            tasks.append(task)
        
        # Collect results
        results = []
        for task in tasks:
            try:
                result = await task
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Model analysis failed: {e}")
        
        if not results:
            return self._get_fallback_analysis(html_data)
        
        # Combine results from multiple models
        return self._combine_insights(results)
    
    def _combine_insights(self, insights_list: List[AIInsights]) -> AIInsights:
        """Combine insights from multiple AI models"""
        if len(insights_list) == 1:
            return insights_list[0]
        
        # Initialize combined insights
        combined = AIInsights()
        
        # Average the scores
        score_totals = {}
        score_counts = {}
        
        for insights in insights_list:
            combined.overall_score += insights.overall_score
            
            for category, score in insights.category_scores.items():
                if category not in score_totals:
                    score_totals[category] = 0
                    score_counts[category] = 0
                score_totals[category] += score
                score_counts[category] += 1
        
        # Calculate averages
        combined.overall_score = combined.overall_score // len(insights_list)
        for category, total in score_totals.items():
            combined.category_scores[category] = total // score_counts[category]
        
        # Combine recommendations (remove duplicates)
        seen_recommendations = set()
        for insights in insights_list:
            for rec in insights.recommendations:
                rec_key = f"{rec.category}:{rec.issue}"
                if rec_key not in seen_recommendations:
                    seen_recommendations.add(rec_key)
                    combined.recommendations.append(rec)
        
        # Combine issues (remove duplicates)
        combined.visual_issues = list(set([
            issue for insights in insights_list for issue in insights.visual_issues
        ]))
        combined.mobile_issues = list(set([
            issue for insights in insights_list for issue in insights.mobile_issues
        ]))
        
        # Add model-specific results
        for insights in insights_list:
            if insights.claude_analysis:
                combined.claude_analysis = insights.claude_analysis
            if insights.yolo_analysis:
                combined.yolo_analysis = insights.yolo_analysis
        
        logger.info(f"🔄 Combined insights from {len(insights_list)} models")
        return combined
    
    def _get_fallback_analysis(self, html_data: CROData) -> AIInsights:
        """Fallback analysis when no AI models are available"""
        recommendations = []
        
        # Generate basic recommendations from HTML data
        if not html_data.trust_signals:
            recommendations.append({
                "category": "trust_signals",
                "priority": "high",
                "issue": "No trust signals detected",
                "solution": "Add security badges, testimonials, or guarantees",
                "impact": "Could increase conversions by 10-15%",
                "source": "fallback"
            })
        
        if len(html_data.cta_buttons) < 2:
            recommendations.append({
                "category": "cta_buttons",
                "priority": "high",
                "issue": "Insufficient call-to-action buttons",
                "solution": "Add more prominent CTA buttons",
                "impact": "Could increase conversions by 8-12%",
                "source": "fallback"
            })
        
        return AIInsights(
            overall_score=70,
            category_scores={
                "product_page": 65,
                "cart_page": 70,
                "mobile": 60,
                "trust_signals": 70,
                "coupons": 55,
                "delivery": 75
            },
            recommendations=recommendations,
            visual_issues=["No AI models enabled for visual analysis"],
            mobile_issues=["Enable AI models for mobile-specific insights"]
        )
    
    def get_enabled_models(self) -> List[str]:
        """Get list of enabled model names"""
        return [model.get_model_name() for model in self.models]
    
    async def get_models_status(self) -> Dict[str, Any]:
        """Get detailed status of all models"""
        status = {
            "claude_vision": {
                "enabled": ENABLE_CLAUDE_VISION,
                "initialized": self.claude_model is not None,
                "ready": self.claude_model.is_enabled() if self.claude_model else False
            },
            "yolo_vision": {
                "enabled": ENABLE_YOLO_VISION,
                "initialized": self.yolo_model is not None,
                "ready": self.yolo_model.is_enabled() if self.yolo_model else False
            }
        }
        return status
    
    async def close(self):
        """Close all models"""
        for model in self.models:
            if hasattr(model, 'close'):
                await model.close()
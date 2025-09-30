"""Enhanced Vision Manager with CRO Framework Integration - FIXED VERSION"""

import logging
from typing import List, Dict, Any
import asyncio

from app.models import AIInsights, CROData, Recommendation

# Import the fixed Gemini model
try:
    from fixed_gemini_vision_model import GeminiVisionModel
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        from gemini_vision_model import GeminiVisionModel
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False

# Try to import Claude
try:
    from app.vision.claude_model import ClaudeVisionModel
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

logger = logging.getLogger(__name__)

# ====================================================================
# 🎛️ VISION MODEL CONFIGURATION - ENABLE/DISABLE MODELS HERE
# ====================================================================

# Enable/Disable Models by changing these values
ENABLE_CLAUDE_VISION = False      # Set to False to disable Claude
ENABLE_GEMINI_VISION = True       # 🚀 NEW: Google Gemini Pro Vision
ENABLE_FRAMEWORK_ANALYSIS = True  # CRO Framework Analysis

# Legacy YOLO support (deprecated in favor of Gemini)
ENABLE_YOLO_VISION = False        # Disabled - replaced by Gemini

# ====================================================================

class EnhancedVisionManager:
    """Enhanced Vision Manager with CRO Framework Integration"""
    
    def __init__(self):
        self.models = []
        self.claude_model = None
        self.gemini_model = None
        self.framework_enabled = ENABLE_FRAMEWORK_ANALYSIS
        
    async def initialize_models(self):
        """Initialize enabled AI models"""
        logger.info("🤖 Initializing enhanced AI vision models...")
        
        # Initialize Claude Vision Model
        if ENABLE_CLAUDE_VISION and CLAUDE_AVAILABLE:
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
            if ENABLE_CLAUDE_VISION and not CLAUDE_AVAILABLE:
                logger.warning("⚠️  Claude Vision enabled but not available")
            else:
                logger.info("🚫 Claude Vision Model disabled by configuration")
        
        # Initialize Gemini Pro Vision Model
        if ENABLE_GEMINI_VISION and GEMINI_AVAILABLE:
            try:
                self.gemini_model = GeminiVisionModel()
                await self.gemini_model.initialize()
                if self.gemini_model.is_enabled():
                    self.models.append(self.gemini_model)
                    logger.info("✅ Gemini Pro Vision Model enabled")
                else:
                    logger.warning("⚠️  Gemini Pro Vision Model disabled (no API key)")
            except Exception as e:
                logger.error(f"❌ Gemini Pro Vision Model failed to initialize: {e}")
        else:
            if ENABLE_GEMINI_VISION and not GEMINI_AVAILABLE:
                logger.warning("⚠️  Gemini Vision enabled but not available")
            else:
                logger.info("🚫 Gemini Pro Vision Model disabled by configuration")
        
        # Legacy YOLO Support Warning
        if ENABLE_YOLO_VISION:
            logger.warning("⚠️  YOLO Vision is deprecated. Using Gemini Pro Vision for better CRO analysis.")
        
        # Framework Analysis
        if ENABLE_FRAMEWORK_ANALYSIS:
            logger.info("✅ CRO Framework Analysis enabled")
        else:
            logger.info("🚫 CRO Framework Analysis disabled")
        
        logger.info(f"🎯 Enhanced Vision Manager initialized with {len(self.models)} AI models + Framework Analysis")
        logger.info(f"🚀 Active Models: {[model.get_model_name() for model in self.models]}")
    
    async def analyze_with_all_models_and_framework(
        self, 
        screenshot: bytes, 
        html_data: CROData, 
        framework_insights: AIInsights = None
    ) -> AIInsights:
        """Run analysis with all enabled models and framework"""
        
        all_insights = []
        
        # Add framework insights if available
        if framework_insights and self.framework_enabled:
            all_insights.append(framework_insights)
            logger.info("📊 Framework analysis included")
        
        # Run AI model analysis if we have models
        if self.models:
            # Run all models concurrently
            tasks = []
            for model in self.models:
                task = asyncio.create_task(model.analyze_screenshot(screenshot, html_data))
                tasks.append(task)
            
            # Collect results
            for task in tasks:
                try:
                    result = await task
                    if result:
                        all_insights.append(result)
                except Exception as e:
                    logger.error(f"Model analysis failed: {e}")
        
        # If no insights available, return fallback
        if not all_insights:
            return self._get_enhanced_fallback_analysis(html_data)
        
        # Combine all insights (framework + AI models)
        return self._combine_enhanced_insights(all_insights, html_data)
    
    def _combine_enhanced_insights(self, insights_list: List[AIInsights], html_data: CROData) -> AIInsights:
        """Enhanced insight combination with framework priority"""
        if len(insights_list) == 1:
            return insights_list[0]
        
        # Initialize combined insights
        combined = AIInsights()
        
        # Separate framework insights from AI model insights
        framework_insights = None
        ai_insights = []
        
        for insights in insights_list:
            # Check if this is framework insights (has navigation, display, etc. categories)
            if any(category in insights.category_scores for category in ["navigation", "display", "information", "technical", "psychological"]):
                framework_insights = insights
            else:
                ai_insights.append(insights)
        
        # Use framework as base if available, otherwise combine AI insights
        if framework_insights:
            combined = framework_insights
            logger.info("🎯 Using framework analysis as base")
            
            # Enhance with AI insights
            if ai_insights:
                self._enhance_framework_with_ai(combined, ai_insights)
        else:
            # Fall back to traditional AI combination
            combined = self._combine_ai_insights(ai_insights)
        
        # Generate meta-insights about the analysis quality
        combined = self._add_meta_insights(combined, len(insights_list))
        
        logger.info(f"🔄 Combined insights from {len(insights_list)} sources (Framework + AI)")
        return combined
    
    def _enhance_framework_with_ai(self, framework_insights: AIInsights, ai_insights: List[AIInsights]):
        """Enhance framework insights with AI model results"""
        
        # Add AI-specific analyses to framework insights
        for ai_insight in ai_insights:
            # Preserve Claude analysis
            if hasattr(ai_insight, 'claude_analysis') and ai_insight.claude_analysis:
                framework_insights.claude_analysis = ai_insight.claude_analysis
            
            # Legacy YOLO support (if somehow still present)
            if hasattr(ai_insight, 'yolo_analysis') and ai_insight.yolo_analysis:
                framework_insights.yolo_analysis = ai_insight.yolo_analysis
            
            # Merge visual and mobile issues
            framework_insights.visual_issues.extend(ai_insight.visual_issues)
            framework_insights.mobile_issues.extend(ai_insight.mobile_issues)
            
            # Add AI recommendations with lower priority if framework already has recommendations
            for rec in ai_insight.recommendations:
                # Check if framework already covers this category
                framework_categories = [r.category for r in framework_insights.recommendations]
                if rec.category not in framework_categories:
                    framework_insights.recommendations.append(rec)
                elif rec.priority == "high":  # Keep high-priority AI recommendations
                    framework_insights.recommendations.append(rec)
        
        # Remove duplicates
        framework_insights.visual_issues = list(set(framework_insights.visual_issues))
        framework_insights.mobile_issues = list(set(framework_insights.mobile_issues))
    
    def _combine_ai_insights(self, ai_insights: List[AIInsights]) -> AIInsights:
        """Combine AI insights when no framework is available"""
        if not ai_insights:
            return AIInsights()
        
        if len(ai_insights) == 1:
            return ai_insights[0]
        
        # Traditional AI combining logic
        combined = AIInsights()
        
        # Average the scores
        score_totals = {}
        score_counts = {}
        
        for insights in ai_insights:
            combined.overall_score += insights.overall_score
            
            for category, score in insights.category_scores.items():
                if category not in score_totals:
                    score_totals[category] = 0
                    score_counts[category] = 0
                score_totals[category] += score
                score_counts[category] += 1
        
        # Calculate averages
        combined.overall_score = combined.overall_score // len(ai_insights)
        for category, total in score_totals.items():
            combined.category_scores[category] = total // score_counts[category]
        
        # Combine recommendations (remove duplicates)
        seen_recommendations = set()
        for insights in ai_insights:
            for rec in insights.recommendations:
                rec_key = f"{rec.category}:{rec.issue}"
                if rec_key not in seen_recommendations:
                    seen_recommendations.add(rec_key)
                    combined.recommendations.append(rec)
        
        # Combine issues (remove duplicates)
        combined.visual_issues = list(set([
            issue for insights in ai_insights for issue in insights.visual_issues
        ]))
        combined.mobile_issues = list(set([
            issue for insights in ai_insights for issue in insights.mobile_issues
        ]))
        
        # Add model-specific results
        for insights in ai_insights:
            if hasattr(insights, 'claude_analysis') and insights.claude_analysis:
                combined.claude_analysis = insights.claude_analysis
            if hasattr(insights, 'yolo_analysis') and insights.yolo_analysis:
                combined.yolo_analysis = insights.yolo_analysis
        
        return combined
    
    def _add_meta_insights(self, insights: AIInsights, analysis_count: int) -> AIInsights:
        """Add meta-insights about analysis quality and coverage"""
        
        # Add analysis quality indicators
        if analysis_count >= 3:  # Framework + 2 AI models
            insights.visual_issues.insert(0, f"Comprehensive analysis using {analysis_count} methods")
        elif analysis_count == 2:
            insights.visual_issues.insert(0, f"Dual analysis using {analysis_count} methods")
        
        # Add coverage indicators
        if "navigation" in insights.category_scores:
            insights.visual_issues.append("✅ Navigation structure analyzed")
        if "display" in insights.category_scores:
            insights.visual_issues.append("✅ Visual design elements checked")
        if "information" in insights.category_scores:
            insights.visual_issues.append("✅ Content completeness verified")
        if "technical" in insights.category_scores:
            insights.visual_issues.append("✅ Technical performance assessed")
        if "psychological" in insights.category_scores:
            insights.visual_issues.append("✅ User psychology factors evaluated")
        
        # Add AI model indicators
        if hasattr(insights, 'claude_analysis') and insights.claude_analysis:
            insights.visual_issues.append("🤖 Claude Vision analysis included")
        
        # Check for Gemini in visual_issues (since we add it there)
        if any("Gemini Pro Vision" in issue for issue in insights.visual_issues):
            insights.visual_issues.append("🚀 Gemini Pro Vision analysis included")
        
        return insights
    
    def _get_enhanced_fallback_analysis(self, html_data: CROData) -> AIInsights:
        """Enhanced fallback analysis when no models are available"""
        recommendations = []
        
        # Framework-based fallback recommendations
        if not html_data.trust_signals:
            recommendations.append(Recommendation(
                category="psychological",
                priority="high",
                issue="No trust signals detected",
                solution="Add security badges, testimonials, or guarantees above the fold",
                impact="Could increase conversions by 15-20%",
                source="framework_fallback"
            ))
        
        if len(html_data.cta_buttons) < 2:
            recommendations.append(Recommendation(
                category="information",
                priority="high", 
                issue="Insufficient call-to-action buttons",
                solution="Add more prominent CTA buttons with action-oriented text",
                impact="Could increase conversions by 10-15%",
                source="framework_fallback"
            ))
        
        if len(html_data.product_images) < 2:
            recommendations.append(Recommendation(
                category="information",
                priority="medium",
                issue="Limited product images",
                solution="Add multiple high-quality product images with alt text",
                impact="Could improve engagement by 8-12%",
                source="framework_fallback"
            ))
        
        # AI model recommendations
        recommendations.append(Recommendation(
            category="system",
            priority="medium",
            issue="AI analysis unavailable",
            solution="Enable Claude Vision and/or Gemini Pro Vision for comprehensive insights",
            impact="Could provide advanced UI analysis and CRO recommendations",
            source="framework_fallback"
        ))
        
        return AIInsights(
            overall_score=70,
            category_scores={
                "navigation": 65,
                "display": 70, 
                "information": 60,
                "technical": 75,
                "psychological": 70,
                # Legacy categories for compatibility
                "product_page": 65,
                "cart_page": 70,
                "mobile": 65,
                "trust_signals": 70,
                "coupons": 55,
                "delivery": 75
            },
            recommendations=recommendations,
            visual_issues=["Framework analysis disabled - enable for comprehensive insights"],
            mobile_issues=["Enable framework analysis for mobile-specific assessment"]
        )
    
    def get_enabled_models(self) -> List[str]:
        """Get list of enabled analysis methods"""
        methods = [model.get_model_name() for model in self.models]
        
        if self.framework_enabled:
            methods.append("CRO Framework Analysis")
        
        # Add note about deprecated YOLO if someone tries to enable it
        if ENABLE_YOLO_VISION:
            methods.append("YOLOv8 (Deprecated - Use Gemini)")
        
        return methods
    
    async def get_models_status(self) -> Dict[str, Any]:
        """Get detailed status of all analysis methods"""
        status = {
            "claude_vision": {
                "enabled": ENABLE_CLAUDE_VISION,
                "initialized": self.claude_model is not None,
                "ready": self.claude_model.is_enabled() if self.claude_model else False,
                "description": "Advanced design and UX analysis"
            },
            "gemini_vision": {
                "enabled": ENABLE_GEMINI_VISION,
                "initialized": self.gemini_model is not None,
                "ready": self.gemini_model.is_enabled() if self.gemini_model else False,
                "description": "AI-powered UI element detection and CRO analysis"
            },
            "framework_analysis": {
                "enabled": ENABLE_FRAMEWORK_ANALYSIS,
                "initialized": True,
                "ready": self.framework_enabled,
                "categories": ["navigation", "display", "information", "technical", "psychological"],
                "description": "5-point CRO framework analysis"
            }
        }
        
        # Add legacy YOLO status if somehow still relevant
        if ENABLE_YOLO_VISION:
            status["yolo_vision_legacy"] = {
                "enabled": False,
                "initialized": False,
                "ready": False,
                "description": "Deprecated - replaced by Gemini Pro Vision"
            }
        
        return status
    
    async def close(self):
        """Close all models"""
        for model in self.models:
            if hasattr(model, 'close'):
                await model.close()
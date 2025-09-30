"""Gemini Pro Vision Model for UI Element Detection and CRO Analysis"""

import os
import time
import logging
import asyncio
import base64
from typing import List, Optional, Dict, Any
import json
import re

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. Run: pip install google-generativeai")

from app.models import AIInsights, CROData, Recommendation, ElementPosition

logger = logging.getLogger(__name__)

class GeminiResults:
    """Results from Gemini Vision analysis"""
    def __init__(self):
        self.ui_elements_detected: int = 0
        self.cta_buttons_found: int = 0
        self.trust_signals_found: int = 0
        self.navigation_issues: List[str] = []
        self.mobile_issues: List[str] = []
        self.processing_time: float = 0.0
        self.confidence_score: float = 0.0
        self.raw_analysis: str = ""

class GeminiVisionModel:
    """Gemini Pro Vision model for comprehensive UI and CRO analysis"""
    
    def __init__(self):
        self.api_key = "AIzaSyBd6NBDPjbNgsQenbkD182b17Zjf9XKkBk"
        self.model = None
        self.enabled = False
    
    async def initialize(self):
        """Initialize Gemini Pro Vision model"""
        if not GEMINI_AVAILABLE:
            logger.error("❌ Gemini SDK not available. Install with: pip install google-generativeai")
            self.enabled = False
            return
            
        if not self.api_key:
            logger.warning("⚠️  Gemini API key not provided. Set GEMINI_API_KEY environment variable")
            self.enabled = False
            return
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Test the model with a simple request
            await asyncio.to_thread(self._test_model)
            
            self.enabled = True
            logger.info("✅ Gemini Pro Vision model initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini Pro Vision: {e}")
            self.enabled = False
    
    def _test_model(self):
        """Test model availability"""
        # Simple test to verify the model is working
        try:
            # Create a simple test (this is synchronous)
            response = self.model.generate_content("Test")
            return True
        except Exception as e:
            raise Exception(f"Gemini model test failed: {e}")
    
    async def analyze_screenshot(self, screenshot: bytes, html_data: CROData) -> AIInsights:
        """Analyze screenshot using Gemini Pro Vision for CRO insights"""
        if not self.enabled:
            return self._get_mock_analysis()
        
        start_time = time.time()
        
        try:
            # Convert screenshot to base64 for Gemini
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            # Generate comprehensive CRO analysis prompt
            prompt = self._generate_cro_analysis_prompt(html_data)
            
            # Prepare image data for Gemini
            image_data = {
                "mime_type": "image/png",
                "data": screenshot_b64
            }
            
            # Call Gemini API asynchronously
            response = await asyncio.to_thread(
                self.model.generate_content,
                [prompt, image_data]
            )
            
            # Parse the response
            insights = await self._parse_gemini_response(response.text, html_data)
            
            # Add Gemini-specific analysis results
            gemini_results = GeminiResults()
            gemini_results.processing_time = time.time() - start_time
            gemini_results.raw_analysis = response.text
            gemini_results = self._extract_gemini_metrics(response.text, gemini_results)
            
            # Add to insights
            insights.gemini_analysis = gemini_results
            
            # Mark recommendations as from Gemini
            for rec in insights.recommendations:
                rec.source = "gemini"
            
            logger.info(f"🤖 Gemini analyzed UI in {gemini_results.processing_time:.2f}s")
            logger.info(f"📊 Found {gemini_results.ui_elements_detected} UI elements, {gemini_results.cta_buttons_found} CTAs")
            
            return insights
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._get_mock_analysis()
    
    def _generate_cro_analysis_prompt(self, html_data: CROData) -> str:
        """Generate comprehensive CRO analysis prompt for Gemini"""
        
        html_context = f"""
HTML Analysis Context:
- CTA Buttons detected: {len(html_data.cta_buttons)}
- Trust Signals found: {len(html_data.trust_signals)}
- Forms present: {len(html_data.forms)}
- Product Images: {len(html_data.product_images)}
- Coupon Fields: {len(html_data.coupon_fields)}
- Delivery Info: {len(html_data.delivery_info)}
"""
        
        prompt = f"""You are a Conversion Rate Optimization expert analyzing this website screenshot. 

{html_context}

Please analyze this website screenshot for conversion optimization and provide your analysis in the following JSON format:

{{
  "overall_score": 85,
  "category_scores": {{
    "navigation": 78,
    "display": 85,
    "information": 80,
    "technical": 90,
    "psychological": 87
  }},
  "ui_elements_detected": {{
    "total_elements": 25,
    "cta_buttons": 4,
    "trust_signals": 2,
    "navigation_items": 8,
    "forms": 1,
    "product_images": 6
  }},
  "recommendations": [
    {{
      "category": "navigation",
      "priority": "high",
      "issue": "Missing breadcrumb navigation",
      "solution": "Add breadcrumb trail to improve user orientation",
      "impact": "Could reduce bounce rate by 5-10%"
    }}
  ],
  "visual_issues": [
    "Primary CTA button lacks visual prominence",
    "Trust badges are not visible above the fold"
  ],
  "mobile_issues": [
    "Touch targets appear too small for mobile users",
    "Navigation menu may be difficult to access on mobile"
  ],
  "detailed_analysis": {{
    "navigation_assessment": "Clear assessment of navigation structure",
    "visual_hierarchy": "Analysis of visual design and hierarchy",
    "content_quality": "Review of content completeness and clarity",
    "technical_observations": "Performance and technical considerations visible",
    "trust_factors": "Analysis of trust signals and credibility elements"
  }}
}}

Focus on these 5 key areas for CRO analysis:

1. **NAVIGATION** (Score 0-100):
   - Are breadcrumbs present and clear?
   - Is the main navigation intuitive and not overwhelming?
   - Can users easily understand where they are and where they can go?
   - Rate navigation clarity and user flow

2. **DISPLAY/VISUAL DESIGN** (Score 0-100):
   - Is there good visual hierarchy with clear headings?
   - Are fonts consistent and readable?
   - Is whitespace used effectively (not too crowded or too sparse)?
   - Do colors support the conversion goals?
   - Are key elements (CTAs, product info) visually prominent?

3. **INFORMATION ARCHITECTURE** (Score 0-100):
   - Is product information complete and compelling?
   - Are there sufficient high-quality product images?
   - Is the value proposition clear?
   - Are offers, discounts, or incentives prominently displayed?
   - Is important information easy to find?

4. **TECHNICAL/MOBILE** (Score 0-100):
   - Does the layout appear mobile-optimized?
   - Are touch targets appropriately sized for mobile?
   - Do you see any performance issues (slow-loading images, etc.)?
   - Is the responsive design working well?

5. **PSYCHOLOGICAL/TRUST** (Score 0-100):
   - Are trust signals (security badges, testimonials, guarantees) visible?
   - Is there social proof (reviews, ratings, customer count)?
   - Are return policies or guarantees prominently displayed?
   - Does the overall design inspire confidence?
   - Are there clear contact methods or support options?

Provide specific, actionable recommendations with priority levels (high/medium/low) and estimated impact. Focus on what you can actually see in the screenshot and how it affects conversion potential.

Be specific about UI elements you can identify - buttons, forms, images, navigation, trust badges, etc. If something is missing that should be there for good CRO, mention it as a recommendation.

Return only the JSON response, no additional text."""

        return prompt
    
    async def _parse_gemini_response(self, response_text: str, html_data: CROData) -> AIInsights:
        """Parse Gemini's JSON response into AIInsights"""
        try:
            # Extract JSON from response (Gemini might include extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in Gemini response")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Convert recommendations
            recommendations = []
            for rec_data in data.get('recommendations', []):
                recommendations.append(Recommendation(
                    category=rec_data.get('category', 'general'),
                    priority=rec_data.get('priority', 'medium'),
                    issue=rec_data.get('issue', ''),
                    solution=rec_data.get('solution', ''),
                    impact=rec_data.get('impact', ''),
                    source="gemini"
                ))
            
            # Create AIInsights object
            insights = AIInsights(
                overall_score=data.get('overall_score', 75),
                category_scores=data.get('category_scores', {}),
                recommendations=recommendations,
                visual_issues=data.get('visual_issues', []),
                mobile_issues=data.get('mobile_issues', [])
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}...")
            return self._get_fallback_analysis_from_text(response_text)
    
    def _get_fallback_analysis_from_text(self, response_text: str) -> AIInsights:
        """Extract insights from text response when JSON parsing fails"""
        
        # Basic text analysis for fallback
        recommendations = []
        visual_issues = []
        mobile_issues = []
        
        lines = response_text.split('\n')
        current_category = "general"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for recommendation patterns
            if any(word in line.lower() for word in ['recommend', 'should', 'could', 'improve']):
                recommendations.append(Recommendation(
                    category=current_category,
                    priority="medium",
                    issue="Identified improvement opportunity",
                    solution=line,
                    impact="Could improve conversion rate",
                    source="gemini"
                ))
            
            # Look for issue patterns
            if any(word in line.lower() for word in ['issue', 'problem', 'missing', 'unclear']):
                if 'mobile' in line.lower():
                    mobile_issues.append(line)
                else:
                    visual_issues.append(line)
        
        return AIInsights(
            overall_score=70,  # Conservative fallback score
            category_scores={
                "navigation": 70,
                "display": 70,
                "information": 70,
                "technical": 70,
                "psychological": 70
            },
            recommendations=recommendations[:5],  # Limit recommendations
            visual_issues=visual_issues[:5],
            mobile_issues=mobile_issues[:3]
        )
    
    def _extract_gemini_metrics(self, response_text: str, gemini_results: GeminiResults) -> GeminiResults:
        """Extract metrics from Gemini response for reporting"""
        try:
            # Try to parse JSON for metrics
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                ui_elements = data.get('ui_elements_detected', {})
                
                gemini_results.ui_elements_detected = ui_elements.get('total_elements', 0)
                gemini_results.cta_buttons_found = ui_elements.get('cta_buttons', 0)
                gemini_results.trust_signals_found = ui_elements.get('trust_signals', 0)
                gemini_results.confidence_score = data.get('overall_score', 0) / 100.0
                
        except Exception:
            # Fallback to text analysis
            gemini_results.ui_elements_detected = len(re.findall(r'button|element|form', response_text, re.IGNORECASE))
            gemini_results.cta_buttons_found = len(re.findall(r'cta|call.to.action|button', response_text, re.IGNORECASE))
            gemini_results.trust_signals_found = len(re.findall(r'trust|badge|security|testimonial', response_text, re.IGNORECASE))
            gemini_results.confidence_score = 0.75  # Default confidence
        
        return gemini_results
    
    def _get_mock_analysis(self) -> AIInsights:
        """Mock analysis when Gemini is not available"""
        return AIInsights(
            overall_score=75,
            category_scores={
                "navigation": 75,
                "display": 78,
                "information": 72,
                "technical": 80,
                "psychological": 73
            },
            recommendations=[
                Recommendation(
                    category="system",
                    priority="high",
                    issue="Gemini Pro Vision not available",
                    solution="Configure GEMINI_API_KEY for advanced UI analysis",
                    impact="Would provide AI-powered CRO insights and UI element detection",
                    source="gemini"
                )
            ],
            visual_issues=["Gemini analysis unavailable - install google-generativeai package"],
            mobile_issues=["Gemini mobile analysis requires API configuration"],
        )
    
    def is_enabled(self) -> bool:
        """Check if Gemini model is enabled"""
        return self.enabled
    
    def get_model_name(self) -> str:
        """Get model name"""
        return "Gemini Pro Vision"
"""Claude Vision Model for CRO Analysis"""

import os
import time
import logging
import asyncio
from typing import Optional, List
import anthropic
import base64

from app.models import AIInsights, CROData, ClaudeAnalysis, Recommendation

logger = logging.getLogger(__name__)

class ClaudeVisionModel:
    """Claude Vision API integration for CRO analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.client = None
        self.enabled = False
    
    async def initialize(self):
        """Initialize Claude API client"""
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.enabled = True
                logger.info("✅ Claude API client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Claude client: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️  Claude API key not provided")
            self.enabled = False
    
    async def analyze_screenshot(self, screenshot: bytes, html_data: CROData) -> AIInsights:
        """Analyze screenshot using Claude Vision"""
        if not self.enabled:
            return self._get_mock_analysis()
        
        start_time = time.time()
        
        try:
            prompt = self._generate_prompt(html_data)
            
            # Encode screenshot
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            # Call Claude API
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            # Parse response
            insights = self._parse_response(response.content[0].text)
            
            # Add Claude-specific analysis
            insights.claude_analysis = ClaudeAnalysis(
                textual_insights=self._extract_insights(response.content[0].text),
                design_suggestions=self._extract_design_suggestions(response.content[0].text),
                ux_recommendations=self._extract_ux_recommendations(response.content[0].text),
                conversion_issues=self._extract_conversion_issues(response.content[0].text),
                processing_time=time.time() - start_time
            )
            
            # Mark recommendations as from Claude
            for rec in insights.recommendations:
                rec.source = "claude"
            
            return insights
            
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return self._get_mock_analysis()
    
    def _generate_prompt(self, html_data: CROData) -> str:
        """Generate analysis prompt for Claude"""
        return f"""Analyze this website screenshot for conversion rate optimization. I've provided HTML element data below.

HTML Elements Found:
- Trust Signals: {len(html_data.trust_signals)}
- CTA Buttons: {len(html_data.cta_buttons)}
- Forms: {len(html_data.forms)}
- Cart Elements: {len(html_data.cart_elements)}
- Product Images: {len(html_data.product_images)}
- Coupon Fields: {len(html_data.coupon_fields)}
- Delivery Info: {len(html_data.delivery_info)}

Please provide a JSON response with this structure:
{{
  "overall_score": 85,
  "category_scores": {{
    "product_page": 78,
    "cart_page": 82,
    "mobile": 75,
    "trust_signals": 90,
    "coupons": 65,
    "delivery": 88
  }},
  "recommendations": [
    {{
      "category": "trust_signals",
      "priority": "high",
      "issue": "Security badges not visible above the fold",
      "solution": "Move SSL certificates and payment badges to header area",
      "impact": "Could increase conversions by 8-12%"
    }}
  ],
  "visual_issues": ["Button colors blend with background", "Text hierarchy unclear"],
  "mobile_issues": ["Touch targets too small", "Navigation hidden"]
}}

Focus on:
1. **Visual Hierarchy**: Is the most important content prominent?
2. **Trust Signals**: Are security badges, testimonials visible?
3. **CTA Optimization**: Are buttons prominent and persuasive?
4. **Mobile Experience**: Is the layout mobile-friendly?
5. **Color Psychology**: Do colors support conversion goals?
6. **Content Clarity**: Is the value proposition clear?
7. **Friction Points**: Any barriers to conversion?

Provide specific, actionable recommendations with priority levels."""
    
    def _parse_response(self, response_text: str) -> AIInsights:
        """Parse Claude's JSON response"""
        import json
        import re
        
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            # Convert to AIInsights
            recommendations = []
            for rec_data in data.get('recommendations', []):
                recommendations.append(Recommendation(**rec_data))
            
            return AIInsights(
                overall_score=data.get('overall_score', 75),
                category_scores=data.get('category_scores', {}),
                recommendations=recommendations,
                visual_issues=data.get('visual_issues', []),
                mobile_issues=data.get('mobile_issues', [])
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return self._get_mock_analysis()
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extract key insights from Claude's response"""
        insights = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['insight', 'notice', 'observe']):
                if len(line) > 10:
                    insights.append(line)
        
        return insights[:5]  # Limit to 5 insights
    
    def _extract_design_suggestions(self, text: str) -> List[str]:
        """Extract design suggestions from response"""
        suggestions = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['design', 'visual', 'color', 'layout']):
                if len(line) > 10:
                    suggestions.append(line.strip())
        
        return suggestions[:5]
    
    def _extract_ux_recommendations(self, text: str) -> List[str]:
        """Extract UX recommendations"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['user', 'navigation', 'experience', 'usability']):
                if len(line) > 10:
                    recommendations.append(line.strip())
        
        return recommendations[:5]
    
    def _extract_conversion_issues(self, text: str) -> List[str]:
        """Extract conversion issues"""
        issues = []
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['conversion', 'cta', 'button', 'trust']):
                if len(line) > 10:
                    issues.append(line.strip())
        
        return issues[:5]
    
    def _get_mock_analysis(self) -> AIInsights:
        """Mock analysis when Claude is not available"""
        return AIInsights(
            overall_score=78,
            category_scores={
                "product_page": 75,
                "cart_page": 82,
                "mobile": 70,
                "trust_signals": 85,
                "coupons": 60,
                "delivery": 88
            },
            recommendations=[
                Recommendation(
                    category="trust_signals",
                    priority="high",
                    issue="Claude Vision analysis unavailable",
                    solution="Configure Claude API key for detailed visual analysis",
                    impact="Would provide human-like design insights",
                    source="claude"
                )
            ],
            visual_issues=["Claude analysis not available"],
            mobile_issues=["Enable Claude for mobile UX insights"],
            claude_analysis=ClaudeAnalysis(
                textual_insights=["Mock analysis - Claude API not configured"],
                design_suggestions=["Add Claude API key for design insights"],
                ux_recommendations=["Configure Claude for UX analysis"],
                conversion_issues=["Claude unavailable for conversion analysis"],
                processing_time=0.1
            )
        )
    
    def is_enabled(self) -> bool:
        """Check if Claude model is enabled"""
        return self.enabled
    
    def get_model_name(self) -> str:
        """Get model name"""
        return "Claude Vision"
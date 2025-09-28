"""Enhanced Web scraping service with CRO framework integration"""

import asyncio
import logging
import re
from typing import List, Tuple
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from app.models import CROData, CROElement, TrustSignal, CTAButton, ElementPosition, AIInsights
from app.framework.enhanced_cro_framework import EnhancedCROFramework

logger = logging.getLogger(__name__)

class EnhancedScrapingService:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.framework = EnhancedCROFramework()
    
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            logger.info("✅ Enhanced scraping service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced scraping service: {e}")
            raise
    
    async def extract_cro_elements_with_framework(self, url: str) -> Tuple[CROData, AIInsights]:
        """Extract CRO elements and run framework analysis"""
        if not self.browser:
            await self.initialize()
        
        try:
            page = await self.browser.new_page()
            
            # Set a real user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            })
            
            # Navigate to page
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Get page content
            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract traditional CRO elements
            cro_data = await self._extract_traditional_elements(soup)
            
            # Run framework analysis
            framework_results = await self.framework.analyze_page_framework(page, soup, url)
            
            # Convert framework results to insights
            framework_insights = self.framework.get_framework_insights(framework_results)
            
            await page.close()
            
            logger.info(f"🔍 Enhanced analysis completed for {url}")
            logger.info(f"📊 Framework score: {framework_insights.overall_score}")
            logger.info(f"📋 Generated {len(framework_insights.recommendations)} framework recommendations")
            
            return cro_data, framework_insights
            
        except Exception as e:
            logger.error(f"Enhanced scraping failed for {url}: {e}")
            return CROData(), AIInsights()
    
    async def _extract_traditional_elements(self, soup: BeautifulSoup) -> CROData:
        """Extract traditional CRO elements (existing functionality)"""
        cro_data = CROData()
        
        # Trust signals
        cro_data.trust_signals = await self._extract_trust_signals(soup)
        
        # CTA buttons  
        cro_data.cta_buttons = await self._extract_cta_buttons(soup)
        
        # Forms
        cro_data.forms = await self._extract_forms(soup)
        
        # Cart elements
        cro_data.cart_elements = await self._extract_cart_elements(soup)
        
        # Product images
        cro_data.product_images = await self._extract_product_images(soup)
        
        # Coupon fields
        cro_data.coupon_fields = await self._extract_coupon_fields(soup)
        
        # Delivery info
        cro_data.delivery_info = await self._extract_delivery_info(soup)
        
        return cro_data
    
    # Enhanced trust signals with framework insights
    async def _extract_trust_signals(self, soup: BeautifulSoup) -> List[TrustSignal]:
        """Extract trust signals with enhanced detection"""
        trust_signals = []
        
        # Expanded trust signal selectors
        trust_selectors = [
            '.trust-badge', '.security-badge', '.ssl-badge', '.verified-badge',
            '.guarantee', '.testimonial', '.review', '.rating',
            '[class*="trust"]', '[class*="security"]', '[class*="verified"]',
            '[class*="guarantee"]', '[class*="testimonial"]', '[class*="ssl"]',
            # Framework-specific trust indicators
            '.money-back', '.satisfaction', '.certified', '.award',
            '[alt*="trust"]', '[alt*="security"]', '[alt*="verified"]'
        ]
        
        for selector in trust_selectors:
            elements = soup.select(selector)
            for element in elements:
                trust_type = self._detect_enhanced_trust_type(element)
                effectiveness = self._calculate_enhanced_trust_effectiveness(element)
                
                trust_signals.append(TrustSignal(
                    type=trust_type,
                    text=element.get_text(strip=True)[:200],
                    position=ElementPosition(x=0, y=0, width=100, height=50),
                    visible=self._is_element_visible(element),
                    effectiveness=effectiveness
                ))
        
        # Also check for trust-related text patterns
        trust_text_patterns = [
            r'money.{0,10}back.{0,10}guarantee',
            r'100%.{0,10}satisfaction',
            r'secure.{0,10}checkout',
            r'verified.{0,10}by',
            r'trusted.{0,10}by',
            r'ssl.{0,10}secured?'
        ]
        
        page_text = soup.get_text().lower()
        for pattern in trust_text_patterns:
            if re.search(pattern, page_text):
                trust_signals.append(TrustSignal(
                    type="text_guarantee",
                    text=f"Trust signal found in text: {pattern}",
                    position=ElementPosition(x=0, y=0, width=200, height=30),
                    visible=True,
                    effectiveness=75
                ))
        
        return trust_signals
    
    # Enhanced CTA button analysis
    async def _extract_cta_buttons(self, soup: BeautifulSoup) -> List[CTAButton]:
        """Extract CTA buttons with enhanced persuasiveness analysis"""
        cta_buttons = []
        
        # Expanded button selectors
        button_selectors = [
            'button', '.btn', '.cta', '.call-to-action',
            'input[type="submit"]', 'input[type="button"]',
            '.add-to-cart', '.buy-now', '.purchase', '.order-now',
            '.get-started', '.sign-up', '.subscribe', '.download',
            '[class*="button"]', '[class*="btn"]', '[role="button"]',
            'a[class*="cta"]', 'a[class*="button"]'
        ]
        
        for selector in button_selectors:
            elements = soup.select(selector)
            for element in elements:
                button_text = element.get_text(strip=True)
                if button_text and len(button_text) < 50:  # Valid button text
                    
                    cta_buttons.append(CTAButton(
                        text=button_text,
                        color=self._extract_color(element),
                        size=self._get_enhanced_button_size(element),
                        position=ElementPosition(x=0, y=0, width=100, height=40),
                        prominent=self._is_prominent_button(element),
                        persuasiveness=self._calculate_enhanced_persuasiveness(button_text)
                    ))
        
        return cta_buttons
    
    # Enhanced form analysis
    async def _extract_forms(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract forms with complexity analysis"""
        forms = []
        
        form_elements = soup.find_all('form')
        for form in form_elements:
            fields = form.find_all(['input', 'select', 'textarea'])
            field_count = len(fields)
            
            # Analyze form complexity
            required_fields = len([f for f in fields if f.get('required')])
            optional_fields = field_count - required_fields
            
            # Check for labels
            labels = form.find_all('label')
            has_proper_labels = len(labels) >= field_count * 0.7  # 70% of fields have labels
            
            forms.append(CROElement(
                type="form",
                text=f"Form: {field_count} fields ({required_fields} required)",
                position=ElementPosition(x=0, y=0, width=300, height=200),
                attributes={
                    "action": form.get("action", ""),
                    "method": form.get("method", "GET"),
                    "field_count": str(field_count),
                    "required_fields": str(required_fields),
                    "has_labels": str(has_proper_labels)
                },
                visible=self._is_element_visible(form),
                score=self._calculate_enhanced_form_score(form, field_count, has_proper_labels)
            ))
        
        return forms
    
    # Enhanced product images with alt text analysis
    async def _extract_product_images(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract product images with accessibility analysis"""
        product_images = []
        
        # Enhanced image selectors
        image_selectors = [
            '.product-image img', '.product-photo img', '.gallery img',
            '[class*="product"] img', '.image-gallery img',
            '.product-slider img', '.product-carousel img',
            '.main-image img', '.featured-image img'
        ]
        
        for selector in image_selectors:
            images = soup.select(selector)
            for img in images:
                alt_text = img.get("alt", "")
                src = img.get("src", "")
                
                product_images.append(CROElement(
                    type="product_image",
                    text=alt_text or "Image without alt text",
                    position=ElementPosition(x=0, y=0, width=300, height=300),
                    attributes={
                        "src": src,
                        "alt": alt_text,
                        "has_alt": str(bool(alt_text)),
                        "is_lazy": str('lazy' in img.get('loading', ''))
                    },
                    visible=self._is_element_visible(img),
                    score=self._calculate_enhanced_image_score(img, alt_text, src)
                ))
        
        return product_images
    
    # Enhanced helper methods
    def _detect_enhanced_trust_type(self, element) -> str:
        """Enhanced trust signal type detection"""
        text = element.get_text().lower()
        classes = str(element.get("class", [])).lower()
        alt = element.get("alt", "").lower()
        
        # More specific trust signal detection
        if any(keyword in text + classes + alt for keyword in ["ssl", "secure", "encrypted"]):
            return "ssl_security"
        elif any(keyword in text + classes + alt for keyword in ["money back", "guarantee", "refund"]):
            return "money_back_guarantee"
        elif any(keyword in text + classes + alt for keyword in ["testimonial", "review", "rating"]):
            return "customer_testimonial"
        elif any(keyword in text + classes + alt for keyword in ["verified", "certified", "approved"]):
            return "verification_badge"
        elif any(keyword in text + classes + alt for keyword in ["award", "winner", "best"]):
            return "award_badge"
        elif any(keyword in text + classes + alt for keyword in ["paypal", "visa", "mastercard", "payment"]):
            return "payment_security"
        return "general_trust"
    
    def _calculate_enhanced_trust_effectiveness(self, element) -> int:
        """Enhanced trust signal effectiveness calculation"""
        score = 60
        
        # Visibility bonus
        if self._is_element_visible(element):
            score += 15
        
        # Position bonus (header/top area)
        classes = str(element.get("class", [])).lower()
        if any(keyword in classes for keyword in ["header", "top", "banner"]):
            score += 10
        
        # Brand recognition bonus
        text = element.get_text().lower()
        trusted_brands = ["norton", "mcafee", "verisign", "paypal", "visa", "mastercard", "ssl", "google"]
        for brand in trusted_brands:
            if brand in text:
                score += 15
                break
        
        # Image vs text bonus
        if element.name == 'img':
            score += 5  # Images are more credible than text
        
        return min(score, 100)
    
    def _calculate_enhanced_persuasiveness(self, text: str) -> int:
        """Enhanced button persuasiveness scoring"""
        score = 50
        text_lower = text.lower()
        
        # High-impact action words
        high_impact_words = ["buy", "get", "save", "free", "now", "today", "instant", "immediate"]
        medium_impact_words = ["add", "shop", "order", "purchase", "subscribe", "join", "start"]
        urgency_words = ["limited", "exclusive", "hurry", "last chance", "ending soon"]
        
        for word in high_impact_words:
            if word in text_lower:
                score += 12
        
        for word in medium_impact_words:
            if word in text_lower:
                score += 7
        
        for word in urgency_words:
            if word in text_lower:
                score += 15
        
        # Length penalty
        if len(text) > 25:
            score -= 10
        
        # Specific high-converting phrases
        if any(phrase in text_lower for phrase in ["add to cart", "buy now", "get started", "free trial"]):
            score += 10
        
        return min(score, 100)
    
    def _get_enhanced_button_size(self, element) -> str:
        """Enhanced button size detection"""
        classes = str(element.get("class", [])).lower()
        style = element.get("style", "").lower()
        
        if any(keyword in classes + style for keyword in ["large", "big", "xl", "jumbo"]):
            return "large"
        elif any(keyword in classes + style for keyword in ["small", "mini", "xs", "tiny"]):
            return "small"
        elif any(keyword in classes + style for keyword in ["medium", "md"]):
            return "medium"
        
        # Check for specific CSS properties
        if "padding" in style:
            return "medium"
        
        return "medium"
    
    def _calculate_enhanced_form_score(self, form, field_count: int, has_proper_labels: bool) -> int:
        """Enhanced form optimization scoring"""
        score = 70
        
        # Field count penalty
        if field_count > 7:
            score -= (field_count - 7) * 3  # Penalize each extra field
        elif field_count <= 3:
            score += 10  # Bonus for simple forms
        
        # Label bonus
        if has_proper_labels:
            score += 15
        
        # Required field analysis
        required_fields = form.find_all(attrs={"required": True})
        if len(required_fields) > field_count * 0.8:  # Too many required fields
            score -= 10
        
        # Error handling check
        error_elements = form.select('.error, .invalid, [class*="error"]')
        if error_elements:
            score += 5  # Has error handling
        
        # Progress indicator check
        progress_elements = form.select('.progress, .step, [class*="progress"]')
        if progress_elements and field_count > 5:
            score += 10  # Has progress indicator for long forms
        
        return max(0, min(score, 100))
    
    def _calculate_enhanced_image_score(self, img, alt_text: str, src: str) -> int:
        """Enhanced image optimization scoring"""
        score = 50
        
        # Alt text bonus
        if alt_text:
            score += 25
            if len(alt_text) > 10:  # Descriptive alt text
                score += 10
        
        # Image format analysis
        if any(ext in src.lower() for ext in ['.webp', '.avif']):
            score += 10  # Modern formats
        elif any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
            score += 5   # Standard formats
        
        # Lazy loading bonus
        if img.get('loading') == 'lazy':
            score += 5
        
        # Responsive image bonus
        if img.get('srcset') or img.get('sizes'):
            score += 10
        
        return min(score, 100)
    
    # Helper methods (keeping existing ones)
    def _is_element_visible(self, element) -> bool:
        """Check if element is visible"""
        style = element.get("style", "")
        return "display:none" not in style and "visibility:hidden" not in style
    
    def _extract_color(self, element) -> str:
        """Extract color from element"""
        style = element.get("style", "")
        color_match = re.search(r'(?:background-)?color:\s*([^;]+)', style)
        return color_match.group(1).strip() if color_match else "default"
    
    def _is_prominent_button(self, element) -> bool:
        """Check if button is prominent"""
        classes = str(element.get("class", [])).lower()
        return any(keyword in classes for keyword in ["primary", "main", "prominent", "hero", "cta"])
    
    # Placeholder methods for other extractions (keeping existing logic)
    async def _extract_cart_elements(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract shopping cart elements"""
        # Keep existing implementation
        return []
    
    async def _extract_coupon_fields(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract coupon/promo code fields"""
        # Keep existing implementation  
        return []
    
    async def _extract_delivery_info(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract delivery and shipping information"""
        # Keep existing implementation
        return []
    
    async def close(self):
        """Close browser and playwright"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
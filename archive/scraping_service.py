"""Web scraping service for HTML element extraction"""

import asyncio
import logging
import re
from typing import List
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from app.models import CROData, CROElement, TrustSignal, CTAButton, ElementPosition

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self):
        self.playwright = None
        self.browser = None
    
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',  # Avoid bot detection
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            logger.info("✅ Scraping service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize scraping service: {e}")
            raise
    
    async def extract_cro_elements(self, url: str) -> CROData:
        """Extract CRO elements from website"""
        if not self.browser:
            await self.initialize()
        
        try:
            page = await self.browser.new_page()
            
            # Set a real user agent to avoid bot detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            })
            
            # More lenient navigation - use domcontentloaded instead of networkidle
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)  # Increased timeout
            await page.wait_for_timeout(2000)  # Wait for some dynamic content
            
            # Get page content
            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract different types of elements
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
            
            await page.close()
            
            logger.info(f"🔍 Extracted CRO elements from {url}: "
                       f"{len(cro_data.trust_signals)} trust signals, "
                       f"{len(cro_data.cta_buttons)} CTA buttons, "
                       f"{len(cro_data.forms)} forms")
            
            return cro_data
            
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return CROData()  # Return empty data on failure
    
    async def _extract_trust_signals(self, soup: BeautifulSoup) -> List[TrustSignal]:
        """Extract trust signals like security badges, testimonials"""
        trust_signals = []
        
        # Security badges and trust seals
        trust_selectors = [
            '.trust-badge', '.security-badge', '.ssl-badge',
            '.guarantee', '.testimonial', '.review',
            '[class*="trust"]', '[class*="security"]', '[class*="verified"]'
        ]
        
        for selector in trust_selectors:
            elements = soup.select(selector)
            for element in elements:
                trust_signals.append(TrustSignal(
                    type=self._detect_trust_type(element),
                    text=element.get_text(strip=True)[:200],
                    position=ElementPosition(x=0, y=0, width=100, height=50),
                    visible=self._is_element_visible(element),
                    effectiveness=self._calculate_trust_effectiveness(element)
                ))
        
        return trust_signals
    
    async def _extract_cta_buttons(self, soup: BeautifulSoup) -> List[CTAButton]:
        """Extract call-to-action buttons"""
        cta_buttons = []
        
        # Button selectors
        button_selectors = [
            'button', '.btn', '.cta', 'input[type="submit"]',
            '.add-to-cart', '.buy-now', '.purchase', '[class*="button"]'
        ]
        
        for selector in button_selectors:
            elements = soup.select(selector)
            for element in elements:
                cta_buttons.append(CTAButton(
                    text=element.get_text(strip=True)[:100],
                    color=self._extract_color(element),
                    size=self._get_button_size(element),
                    position=ElementPosition(x=0, y=0, width=100, height=40),
                    prominent=self._is_prominent_button(element),
                    persuasiveness=self._calculate_persuasiveness(element.get_text(strip=True))
                ))
        
        return cta_buttons
    
    async def _extract_forms(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract forms"""
        forms = []
        
        form_elements = soup.find_all('form')
        for form in form_elements:
            forms.append(CROElement(
                type="form",
                text=f"Form with {len(form.find_all(['input', 'select', 'textarea']))} fields",
                position=ElementPosition(x=0, y=0, width=300, height=200),
                attributes={
                    "action": form.get("action", ""),
                    "method": form.get("method", "GET"),
                    "field_count": str(len(form.find_all(['input', 'select', 'textarea'])))
                },
                visible=self._is_element_visible(form),
                score=self._calculate_form_score(form)
            ))
        
        return forms
    
    async def _extract_cart_elements(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract shopping cart elements"""
        cart_elements = []
        
        cart_selectors = ['.cart', '.shopping-cart', '.basket', '#cart']
        
        for selector in cart_selectors:
            elements = soup.select(selector)
            for element in elements:
                cart_elements.append(CROElement(
                    type="cart",
                    text=element.get_text(strip=True)[:200],
                    position=ElementPosition(x=0, y=0, width=300, height=200),
                    attributes={"class": str(element.get("class", []))},
                    visible=self._is_element_visible(element),
                    score=self._calculate_cart_score(element)
                ))
        
        return cart_elements
    
    async def _extract_product_images(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract product images"""
        product_images = []
        
        # Product image selectors
        image_selectors = [
            '.product-image img', '.product-photo img', 
            '[class*="product"] img', '.gallery img'
        ]
        
        for selector in image_selectors:
            elements = soup.select(selector)
            for img in elements:
                product_images.append(CROElement(
                    type="product_image",
                    text=img.get("alt", ""),
                    position=ElementPosition(x=0, y=0, width=300, height=300),
                    attributes={
                        "src": img.get("src", ""),
                        "alt": img.get("alt", "")
                    },
                    visible=self._is_element_visible(img),
                    score=self._calculate_image_score(img)
                ))
        
        return product_images
    
    async def _extract_coupon_fields(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract coupon/promo code fields"""
        coupon_fields = []
        
        # Coupon field selectors
        coupon_inputs = soup.find_all('input', {'name': re.compile(r'coupon|promo|discount', re.I)})
        coupon_classes = soup.select('[class*="coupon"], [class*="promo"], [class*="discount"]')
        
        all_coupon_elements = coupon_inputs + coupon_classes
        
        for element in all_coupon_elements:
            coupon_fields.append(CROElement(
                type="coupon_field",
                text=element.get("placeholder", "Coupon field"),
                position=ElementPosition(x=0, y=0, width=200, height=40),
                attributes={
                    "name": element.get("name", ""),
                    "placeholder": element.get("placeholder", ""),
                    "type": element.get("type", "")
                },
                visible=self._is_element_visible(element),
                score=self._calculate_coupon_visibility(element)
            ))
        
        return coupon_fields
    
    async def _extract_delivery_info(self, soup: BeautifulSoup) -> List[CROElement]:
        """Extract delivery and shipping information"""
        delivery_info = []
        
        delivery_selectors = [
            '.delivery', '.shipping', '.free-shipping', 
            '[class*="delivery"]', '[class*="shipping"]'
        ]
        
        for selector in delivery_selectors:
            elements = soup.select(selector)
            for element in elements:
                delivery_info.append(CROElement(
                    type="delivery_info",
                    text=element.get_text(strip=True)[:200],
                    position=ElementPosition(x=0, y=0, width=200, height=50),
                    attributes={"class": str(element.get("class", []))},
                    visible=self._is_element_visible(element),
                    score=self._calculate_delivery_score(element)
                ))
        
        return delivery_info
    
    # Helper methods
    def _detect_trust_type(self, element) -> str:
        """Detect type of trust signal"""
        text = element.get_text().lower()
        classes = str(element.get("class", [])).lower()
        
        if "ssl" in text or "ssl" in classes:
            return "ssl_certificate"
        elif "guarantee" in text or "money back" in text:
            return "money_back_guarantee"
        elif "testimonial" in text or "review" in text:
            return "customer_testimonial"
        elif "secure" in text or "verified" in text:
            return "security_badge"
        return "general_trust"
    
    def _is_element_visible(self, element) -> bool:
        """Check if element is visible"""
        style = element.get("style", "")
        return "display:none" not in style and "visibility:hidden" not in style
    
    def _extract_color(self, element) -> str:
        """Extract color from element"""
        style = element.get("style", "")
        color_match = re.search(r'(?:background-)?color:\s*([^;]+)', style)
        return color_match.group(1).strip() if color_match else "default"
    
    def _get_button_size(self, element) -> str:
        """Determine button size"""
        classes = str(element.get("class", [])).lower()
        if "large" in classes or "big" in classes:
            return "large"
        elif "small" in classes or "mini" in classes:
            return "small"
        return "medium"
    
    def _is_prominent_button(self, element) -> bool:
        """Check if button is prominent"""
        classes = str(element.get("class", [])).lower()
        return any(keyword in classes for keyword in ["primary", "main", "prominent", "hero"])
    
    def _calculate_persuasiveness(self, text: str) -> int:
        """Calculate persuasiveness score of button text"""
        score = 50
        text_lower = text.lower()
        
        positive_words = ["buy", "get", "save", "free", "now", "today", "limited", "exclusive"]
        action_words = ["add", "shop", "order", "purchase", "subscribe"]
        
        for word in positive_words:
            if word in text_lower:
                score += 10
        
        for word in action_words:
            if word in text_lower:
                score += 5
        
        return min(score, 100)
    
    def _calculate_trust_effectiveness(self, element) -> int:
        """Calculate trust signal effectiveness"""
        score = 60
        if self._is_element_visible(element):
            score += 20
        
        text = element.get_text().lower()
        trust_brands = ["norton", "mcafee", "verisign", "paypal", "visa", "mastercard"]
        
        for brand in trust_brands:
            if brand in text:
                score += 10
                break
        
        return min(score, 100)
    
    def _calculate_form_score(self, form) -> int:
        """Calculate form optimization score"""
        score = 70
        fields = form.find_all(['input', 'select', 'textarea'])
        field_count = len(fields)
        
        if field_count > 5:
            score -= (field_count - 5) * 5
        
        labels = form.find_all('label')
        if labels:
            score += 10
        
        return max(0, min(score, 100))
    
    def _calculate_cart_score(self, element) -> int:
        """Calculate cart optimization score"""
        score = 60
        text = element.get_text().lower()
        
        if any(keyword in text for keyword in ["$", "price", "total"]):
            score += 15
        if any(keyword in text for keyword in ["checkout", "buy"]):
            score += 15
        if any(keyword in text for keyword in ["quantity", "qty"]):
            score += 10
        
        return score
    
    def _calculate_image_score(self, img) -> int:
        """Calculate image optimization score"""
        score = 50
        
        if img.get("alt"):
            score += 20
        
        src = img.get("src", "")
        if any(keyword in src for keyword in ["large", "hd", "high"]):
            score += 15
        
        return score
    
    def _calculate_coupon_visibility(self, element) -> int:
        """Calculate coupon field visibility score"""
        score = 40
        classes = str(element.get("class", [])).lower()
        
        if any(keyword in classes for keyword in ["visible", "prominent"]):
            score += 30
        
        if self._is_element_visible(element):
            score += 20
        
        return score
    
    def _calculate_delivery_score(self, element) -> int:
        """Calculate delivery info score"""
        score = 60
        text = element.get_text().lower()
        
        if any(keyword in text for keyword in ["day", "hour"]):
            score += 20
        if "free" in text:
            score += 15
        if any(keyword in text for keyword in ["express", "fast", "next"]):
            score += 10
        
        return score
    
    async def close(self):
        """Close browser and playwright"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
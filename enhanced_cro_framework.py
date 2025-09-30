"""Enhanced CRO Analysis Engine implementing the 5-point framework"""

import re
import asyncio
import logging
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup
from playwright.async_api import Page
from urllib.parse import urlparse

from app.models import CROData, CROElement, TrustSignal, CTAButton, ElementPosition, AIInsights, Recommendation

logger = logging.getLogger(__name__)

class EnhancedCROFramework:
    """Implementation of the 5-point CRO framework"""
    
    def __init__(self):
        self.analysis_results = {}
    
    async def analyze_page_framework(self, page: Page, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Run complete framework analysis"""
        
        # Run all 5 framework analyses
        navigation_analysis = await self._analyze_navigation(soup, url)
        display_analysis = await self._analyze_display(soup)
        information_analysis = await self._analyze_information(soup)
        technical_analysis = await self._analyze_technical(page, url)
        psychological_analysis = await self._analyze_psychological(soup)
        
        # Combine results
        framework_results = {
            "navigation": navigation_analysis,
            "display": display_analysis,
            "information": information_analysis,
            "technical": technical_analysis,
            "psychological": psychological_analysis,
            "overall_framework_score": self._calculate_framework_score([
                navigation_analysis, display_analysis, information_analysis,
                technical_analysis, psychological_analysis
            ])
        }
        
        return framework_results
    
    async def _analyze_navigation(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """1. NAVIGATIONAL: Check navigation complexity and breadcrumbs"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Check for breadcrumbs
        breadcrumb_selectors = [
            '.breadcrumb', '.breadcrumbs', '[class*="breadcrumb"]',
            'nav[aria-label*="breadcrumb"]', '.navigation-path'
        ]
        
        breadcrumbs_found = any(soup.select(selector) for selector in breadcrumb_selectors)
        analysis["metrics"]["has_breadcrumbs"] = breadcrumbs_found
        
        if not breadcrumbs_found:
            analysis["score"] -= 20
            analysis["issues"].append("No breadcrumb navigation found")
            analysis["recommendations"].append({
                "category": "navigation",
                "priority": "medium",
                "issue": "Missing breadcrumb navigation",
                "solution": "Add breadcrumb navigation to help users understand their location",
                "impact": "Could reduce bounce rate by 5-10%"
            })
        
        # Count navigation menu items (too many = complex)
        nav_items = soup.select('nav a, .menu a, .navigation a, header a')
        nav_count = len([item for item in nav_items if item.get_text(strip=True)])
        analysis["metrics"]["navigation_links"] = nav_count
        
        if nav_count > 15:
            analysis["score"] -= 15
            analysis["issues"].append(f"Too many navigation links ({nav_count})")
            analysis["recommendations"].append({
                "category": "navigation", 
                "priority": "medium",
                "issue": f"Navigation has {nav_count} links",
                "solution": "Simplify navigation to 7-12 main links, use dropdown menus",
                "impact": "Could improve user experience and reduce cognitive load"
            })
        
        # Check page depth (URL segments)
        url_path = urlparse(url).path
        path_depth = len([segment for segment in url_path.split('/') if segment])
        analysis["metrics"]["page_depth"] = path_depth
        
        if path_depth > 4:
            analysis["score"] -= 10
            analysis["issues"].append(f"Page is {path_depth} levels deep")
            analysis["recommendations"].append({
                "category": "navigation",
                "priority": "low", 
                "issue": f"Page depth is {path_depth} levels",
                "solution": "Restructure site architecture to reduce page depth",
                "impact": "Could improve SEO and user navigation"
            })
        
        return analysis
    
    async def _analyze_display(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """2. DISPLAY: Check whitespace, fonts, element spacing"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Font analysis - count unique font families
        font_families = set()
        style_elements = soup.find_all(['style'])
        
        for style in style_elements:
            if style.string:
                font_matches = re.findall(r'font-family:\s*([^;]+)', style.string, re.IGNORECASE)
                for match in font_matches:
                    # Clean up font names
                    fonts = [f.strip().strip('"\'') for f in match.split(',')]
                    font_families.update(fonts[:2])  # Take first 2 fonts from stack
        
        # Also check inline styles
        elements_with_fonts = soup.find_all(attrs={"style": re.compile(r'font-family', re.I)})
        for element in elements_with_fonts:
            style = element.get('style', '')
            font_match = re.search(r'font-family:\s*([^;]+)', style, re.IGNORECASE)
            if font_match:
                fonts = [f.strip().strip('"\'') for f in font_match.group(1).split(',')]
                font_families.update(fonts[:2])
        
        # Remove generic fonts
        generic_fonts = {'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui'}
        unique_fonts = font_families - generic_fonts
        
        font_count = len(unique_fonts)
        analysis["metrics"]["font_count"] = font_count
        analysis["metrics"]["fonts_used"] = list(unique_fonts)
        
        if font_count > 2:
            analysis["score"] -= 20
            analysis["issues"].append(f"Too many fonts used ({font_count})")
            analysis["recommendations"].append({
                "category": "display",
                "priority": "high",
                "issue": f"Using {font_count} different fonts",
                "solution": "Limit to 1-2 font families for consistent design",
                "impact": "Could improve visual hierarchy and brand consistency"
            })
        
        # Check for potential overlapping elements (simplified heuristic)
        positioned_elements = soup.find_all(attrs={"style": re.compile(r'position:\s*(absolute|fixed)', re.I)})
        analysis["metrics"]["positioned_elements"] = len(positioned_elements)
        
        if len(positioned_elements) > 5:
            analysis["score"] -= 15
            analysis["issues"].append("Many absolutely positioned elements detected")
            analysis["recommendations"].append({
                "category": "display",
                "priority": "medium", 
                "issue": "High number of absolutely positioned elements",
                "solution": "Review layout for potential overlapping content",
                "impact": "Could prevent content overlap and improve readability"
            })
        
        # Whitespace analysis - check for empty space indicators
        container_elements = soup.find_all(['div', 'section', 'article'])
        empty_containers = [el for el in container_elements if not el.get_text(strip=True)]
        analysis["metrics"]["empty_containers"] = len(empty_containers)
        
        if len(empty_containers) > 10:
            analysis["score"] -= 10
            analysis["issues"].append("Many empty containers (potential whitespace issues)")
        
        return analysis
    
    async def _analyze_information(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """3. INFORMATIONAL: Check product information completeness"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [], 
            "metrics": {}
        }
        
        # Product title analysis
        title_selectors = [
            'h1', '.product-title', '.product-name', '[class*="title"]'
        ]
        
        product_titles = []
        for selector in title_selectors:
            titles = soup.select(selector)
            product_titles.extend([t.get_text(strip=True) for t in titles if t.get_text(strip=True)])
        
        analysis["metrics"]["product_titles"] = len(product_titles)
        
        # Check title length
        for title in product_titles[:3]:  # Check first 3 titles
            if len(title) > 60:
                analysis["score"] -= 10
                analysis["issues"].append(f"Product title too long ({len(title)} chars)")
                analysis["recommendations"].append({
                    "category": "information",
                    "priority": "medium",
                    "issue": "Product title exceeds 60 characters",
                    "solution": "Shorten product titles to improve readability",
                    "impact": "Could improve user comprehension and SEO"
                })
                break
        
        # Product description analysis
        description_selectors = [
            '.product-description', '.description', '[class*="description"]',
            '.product-details', '.details', '.product-info'
        ]
        
        descriptions = []
        for selector in description_selectors:
            desc_elements = soup.select(selector)
            descriptions.extend([d.get_text(strip=True) for d in desc_elements])
        
        analysis["metrics"]["has_descriptions"] = len(descriptions) > 0
        analysis["metrics"]["description_count"] = len(descriptions)
        
        if not descriptions:
            analysis["score"] -= 25
            analysis["issues"].append("No product descriptions found")
            analysis["recommendations"].append({
                "category": "information",
                "priority": "high",
                "issue": "Missing product descriptions",
                "solution": "Add detailed product descriptions to build trust",
                "impact": "Could increase conversions by 15-20%"
            })
        
        # Product images analysis
        product_image_selectors = [
            '.product-image img', '.product-photo img', '.gallery img',
            '[class*="product"] img', '.image-gallery img'
        ]
        
        product_images = []
        for selector in product_image_selectors:
            images = soup.select(selector)
            product_images.extend(images)
        
        image_count = len(product_images)
        analysis["metrics"]["product_image_count"] = image_count
        
        if image_count < 2:
            analysis["score"] -= 20
            analysis["issues"].append(f"Only {image_count} product image(s) found")
            analysis["recommendations"].append({
                "category": "information",
                "priority": "high",
                "issue": f"Insufficient product images ({image_count})",
                "solution": "Add at least 2-4 high-quality product images",
                "impact": "Could increase conversions by 10-15%"
            })
        
        # Check for offers/coupons information
        offer_selectors = [
            '.offer', '.discount', '.coupon', '.promo', '.sale',
            '[class*="offer"]', '[class*="discount"]', '[class*="coupon"]'
        ]
        
        offers = []
        for selector in offer_selectors:
            offer_elements = soup.select(selector)
            offers.extend(offer_elements)
        
        analysis["metrics"]["has_offers"] = len(offers) > 0
        analysis["metrics"]["offer_count"] = len(offers)
        
        if not offers:
            analysis["score"] -= 15
            analysis["issues"].append("No promotional offers or coupons visible")
            analysis["recommendations"].append({
                "category": "information",
                "priority": "medium",
                "issue": "No visible offers or promotions",
                "solution": "Add promotional offers or discount codes",
                "impact": "Could increase conversions by 8-12%"
            })
        
        return analysis
    
    async def _analyze_technical(self, page: Page, url: str) -> Dict[str, Any]:
        """4. SPEED/TECHNICAL: Check performance and mobile optimization"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        try:
            # Page load performance metrics
            performance = await page.evaluate("""
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    return {
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                        firstPaint: performance.getEntriesByType('paint').find(p => p.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: performance.getEntriesByType('paint').find(p => p.name === 'first-contentful-paint')?.startTime || 0
                    };
                }
            """)
            
            analysis["metrics"]["performance"] = performance
            
            # Check DOM Content Loaded time
            if performance.get('domContentLoaded', 0) > 3000:  # > 3 seconds
                analysis["score"] -= 20
                analysis["issues"].append("Slow DOM content loading")
                analysis["recommendations"].append({
                    "category": "technical",
                    "priority": "high",
                    "issue": "DOM content loads slowly",
                    "solution": "Optimize critical rendering path and reduce blocking resources",
                    "impact": "Could improve user experience and reduce bounce rate"
                })
            
            # Check First Contentful Paint
            if performance.get('firstContentfulPaint', 0) > 2500:  # > 2.5 seconds
                analysis["score"] -= 15
                analysis["issues"].append("Slow first contentful paint")
        
        except Exception as e:
            logger.warning(f"Performance metrics not available: {e}")
            analysis["metrics"]["performance_error"] = str(e)
        
        # Image optimization check
        try:
            images = await page.evaluate("""
                () => {
                    const imgs = Array.from(document.images);
                    return imgs.map(img => ({
                        src: img.src,
                        width: img.naturalWidth,
                        height: img.naturalHeight,
                        fileSize: img.src.length // Rough estimate
                    }));
                }
            """)
            
            large_images = [img for img in images if img['width'] > 2000 or img['height'] > 2000]
            analysis["metrics"]["large_images"] = len(large_images)
            analysis["metrics"]["total_images"] = len(images)
            
            if large_images:
                analysis["score"] -= 10
                analysis["issues"].append(f"{len(large_images)} very large images detected")
                analysis["recommendations"].append({
                    "category": "technical",
                    "priority": "medium",
                    "issue": f"{len(large_images)} images are very large",
                    "solution": "Optimize image sizes and use responsive images",
                    "impact": "Could improve page load speed by 20-30%"
                })
        
        except Exception as e:
            logger.warning(f"Image analysis failed: {e}")
        
        # Mobile viewport check
        try:
            viewport_meta = await page.evaluate("""
                () => {
                    const viewport = document.querySelector('meta[name="viewport"]');
                    return viewport ? viewport.content : null;
                }
            """)
            
            analysis["metrics"]["has_viewport_meta"] = bool(viewport_meta)
            
            if not viewport_meta:
                analysis["score"] -= 20
                analysis["issues"].append("No mobile viewport meta tag")
                analysis["recommendations"].append({
                    "category": "technical",
                    "priority": "high", 
                    "issue": "Missing viewport meta tag",
                    "solution": "Add <meta name='viewport' content='width=device-width, initial-scale=1'>",
                    "impact": "Essential for mobile responsiveness"
                })
        
        except Exception as e:
            logger.warning(f"Viewport check failed: {e}")
        
        return analysis
    
    async def _analyze_psychological(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """5. EASE OF USE/PSYCHOLOGICAL: Check consistency and trust elements"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        # Trust badges analysis
        trust_selectors = [
            '.trust', '.security', '.badge', '.verified', '.guarantee',
            '[class*="trust"]', '[class*="security"]', '[class*="verified"]'
        ]
        
        trust_elements = []
        for selector in trust_selectors:
            elements = soup.select(selector)
            trust_elements.extend(elements)
        
        analysis["metrics"]["trust_badges"] = len(trust_elements)
        
        if len(trust_elements) < 2:
            analysis["score"] -= 20
            analysis["issues"].append("Insufficient trust signals")
            analysis["recommendations"].append({
                "category": "psychological",
                "priority": "high",
                "issue": "Few or no trust badges visible",
                "solution": "Add security badges, testimonials, and guarantees",
                "impact": "Could increase conversions by 12-18%"
            })
        
        # Return policy check
        return_policy_indicators = soup.find_all(text=re.compile(r'return|refund|guarantee', re.I))
        analysis["metrics"]["has_return_policy"] = len(return_policy_indicators) > 0
        
        if not return_policy_indicators:
            analysis["score"] -= 15
            analysis["issues"].append("No clear return policy mentioned")
            analysis["recommendations"].append({
                "category": "psychological",
                "priority": "medium",
                "issue": "Return policy not clearly visible",
                "solution": "Make return policy prominent and easily accessible",
                "impact": "Could reduce purchase hesitation and increase trust"
            })
        
        # FAQ section check
        faq_selectors = [
            '.faq', '.frequently-asked', '[class*="faq"]',
            'h1, h2, h3, h4, h5, h6'  # Check headers for FAQ text
        ]
        
        faq_found = False
        for selector in faq_selectors:
            elements = soup.select(selector)
            for element in elements:
                if re.search(r'faq|frequently.{0,10}asked', element.get_text(), re.I):
                    faq_found = True
                    break
            if faq_found:
                break
        
        analysis["metrics"]["has_faq"] = faq_found
        
        if not faq_found:
            analysis["score"] -= 10
            analysis["issues"].append("No FAQ section found")
            analysis["recommendations"].append({
                "category": "psychological",
                "priority": "medium",
                "issue": "No FAQ section visible",
                "solution": "Add FAQ section to address common concerns",
                "impact": "Could reduce support requests and increase conversions"
            })
        
        # Color consistency analysis (simplified)
        style_elements = soup.find_all(['style'])
        color_usage = []
        
        for style in style_elements:
            if style.string:
                # Extract colors
                color_matches = re.findall(r'color:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\([^)]+\))', style.string)
                color_usage.extend(color_matches)
        
        unique_colors = len(set(color_usage))
        analysis["metrics"]["unique_colors"] = unique_colors
        
        if unique_colors > 8:
            analysis["score"] -= 10
            analysis["issues"].append(f"Many different colors used ({unique_colors})")
            analysis["recommendations"].append({
                "category": "psychological",
                "priority": "low",
                "issue": "Color palette may be too diverse",
                "solution": "Limit color palette to 3-5 main colors for consistency",
                "impact": "Could improve brand consistency and visual appeal"
            })
        
        return analysis
    
    def _calculate_framework_score(self, analyses: List[Dict[str, Any]]) -> int:
        """Calculate overall framework score"""
        if not analyses:
            return 0
        
        total_score = sum(analysis.get('score', 0) for analysis in analyses)
        return total_score // len(analyses)
    
    def generate_framework_recommendations(self, framework_results: Dict[str, Any]) -> List[Recommendation]:
        """Generate recommendations based on framework analysis"""
        recommendations = []
        
        for category, analysis in framework_results.items():
            if category == "overall_framework_score":
                continue
                
            for rec_data in analysis.get('recommendations', []):
                recommendations.append(Recommendation(
                    category=rec_data['category'],
                    priority=rec_data['priority'], 
                    issue=rec_data['issue'],
                    solution=rec_data['solution'],
                    impact=rec_data['impact'],
                    source="framework"
                ))
        
        return recommendations
    
    def get_framework_insights(self, framework_results: Dict[str, Any]) -> AIInsights:
        """Convert framework results to AIInsights format"""
        
        # Calculate category scores based on framework
        category_scores = {
            "navigation": framework_results.get('navigation', {}).get('score', 100),
            "display": framework_results.get('display', {}).get('score', 100),
            "information": framework_results.get('information', {}).get('score', 100),
            "technical": framework_results.get('technical', {}).get('score', 100),
            "psychological": framework_results.get('psychological', {}).get('score', 100)
        }
        
        # Generate visual and mobile issues
        visual_issues = []
        mobile_issues = []
        
        for category, analysis in framework_results.items():
            if category == "overall_framework_score":
                continue
                
            issues = analysis.get('issues', [])
            visual_issues.extend(issues)
            
            if category == "technical":
                mobile_issues.extend([issue for issue in issues if 'mobile' in issue.lower() or 'viewport' in issue.lower()])
        
        recommendations = self.generate_framework_recommendations(framework_results)
        
        return AIInsights(
            overall_score=framework_results.get('overall_framework_score', 100),
            category_scores=category_scores,
            recommendations=recommendations,
            visual_issues=visual_issues[:10],  # Limit to 10 issues
            mobile_issues=mobile_issues[:5]   # Limit to 5 mobile issues
        )
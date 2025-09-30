"""Enhanced CRO Framework with Lighthouse Integration and Detailed Feedback"""

import re
import asyncio
import logging
import json
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from playwright.async_api import Page
from urllib.parse import urlparse

from app.models import (
    CROData, CROElement, TrustSignal, CTAButton, ElementPosition, 
    AIInsights, Recommendation, FrameworkFeedback, LighthouseMetrics
)

logger = logging.getLogger(__name__)

class EnhancedCROFramework:
    """Implementation of the 5-point CRO framework with Lighthouse"""
    
    def __init__(self):
        self.analysis_results = {}
        self.lighthouse_available = self._check_lighthouse_availability()
    
    def _check_lighthouse_availability(self) -> bool:
        """Check if Lighthouse CLI is available"""
        try:
            result = subprocess.run(
                ['lighthouse', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✅ Lighthouse CLI detected")
                return True
        except Exception:
            pass
        
        logger.info("ℹ️  Lighthouse CLI not available - using basic metrics")
        return False
    
    async def analyze_page_framework(self, page: Page, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Run complete framework analysis with feedback"""
        
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
            "metrics": {},
            "strengths": [],
            "improvements": []
        }
        
        # Check for breadcrumbs
        breadcrumb_selectors = [
            '.breadcrumb', '.breadcrumbs', '[class*="breadcrumb"]',
            'nav[aria-label*="breadcrumb"]', '.navigation-path'
        ]
        
        breadcrumbs_found = any(soup.select(selector) for selector in breadcrumb_selectors)
        analysis["metrics"]["has_breadcrumbs"] = breadcrumbs_found
        
        if breadcrumbs_found:
            analysis["strengths"].append("Breadcrumb navigation present - helps users understand their location")
        else:
            analysis["score"] -= 20
            analysis["issues"].append("No breadcrumb navigation found")
            analysis["improvements"].append("Add breadcrumb navigation to improve user orientation")
            analysis["recommendations"].append({
                "category": "navigation",
                "priority": "medium",
                "issue": "Missing breadcrumb navigation",
                "solution": "Add breadcrumb navigation to help users understand their location",
                "impact": "Could reduce bounce rate by 5-10%"
            })
        
        # Count navigation menu items
        nav_items = soup.select('nav a, .menu a, .navigation a, header a')
        nav_count = len([item for item in nav_items if item.get_text(strip=True)])
        analysis["metrics"]["navigation_links"] = nav_count
        
        if nav_count <= 12:
            analysis["strengths"].append(f"Navigation menu is well-sized with {nav_count} links - not overwhelming")
        elif nav_count <= 15:
            analysis["strengths"].append(f"Navigation has {nav_count} links - manageable but could be streamlined")
        else:
            analysis["score"] -= 15
            analysis["issues"].append(f"Too many navigation links ({nav_count})")
            analysis["improvements"].append(f"Reduce navigation from {nav_count} to 10-12 main links")
            analysis["recommendations"].append({
                "category": "navigation", 
                "priority": "medium",
                "issue": f"Navigation has {nav_count} links",
                "solution": "Simplify navigation to 7-12 main links, use dropdown menus for sub-items",
                "impact": "Could improve user experience and reduce cognitive load"
            })
        
        # Check page depth
        url_path = urlparse(url).path
        path_depth = len([segment for segment in url_path.split('/') if segment])
        analysis["metrics"]["page_depth"] = path_depth
        
        if path_depth <= 3:
            analysis["strengths"].append(f"Page depth is {path_depth} levels - easily accessible")
        else:
            analysis["score"] -= 10
            analysis["issues"].append(f"Page is {path_depth} levels deep")
            analysis["improvements"].append(f"Reduce page depth from {path_depth} to 3 levels maximum")
        
        # Generate final strengths/improvements summary
        if analysis["score"] >= 90:
            if len(analysis["strengths"]) < 3:
                analysis["strengths"].append("Navigation structure follows best practices")
        
        return analysis
    
    async def _analyze_display(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """2. DISPLAY: Check whitespace, fonts, element spacing"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [],
            "metrics": {},
            "strengths": [],
            "improvements": []
        }
        
        # Font analysis
        font_families = set()
        style_elements = soup.find_all(['style'])
        
        for style in style_elements:
            if style.string:
                font_matches = re.findall(r'font-family:\s*([^;]+)', style.string, re.IGNORECASE)
                for match in font_matches:
                    fonts = [f.strip().strip('"\'') for f in match.split(',')]
                    font_families.update(fonts[:2])
        
        elements_with_fonts = soup.find_all(attrs={"style": re.compile(r'font-family', re.I)})
        for element in elements_with_fonts:
            style = element.get('style', '')
            font_match = re.search(r'font-family:\s*([^;]+)', style, re.IGNORECASE)
            if font_match:
                fonts = [f.strip().strip('"\'') for f in font_match.group(1).split(',')]
                font_families.update(fonts[:2])
        
        generic_fonts = {'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui'}
        unique_fonts = font_families - generic_fonts
        
        font_count = len(unique_fonts)
        analysis["metrics"]["font_count"] = font_count
        analysis["metrics"]["fonts_used"] = list(unique_fonts)
        
        if font_count <= 2:
            analysis["strengths"].append(f"Font usage is consistent with {font_count} font families - maintains visual coherence")
        else:
            analysis["score"] -= 20
            analysis["issues"].append(f"Too many fonts used ({font_count})")
            analysis["improvements"].append(f"Reduce fonts from {font_count} to 1-2 families for better consistency")
            analysis["recommendations"].append({
                "category": "display",
                "priority": "high",
                "issue": f"Using {font_count} different fonts",
                "solution": "Limit to 1-2 font families for consistent design",
                "impact": "Could improve visual hierarchy and brand consistency"
            })
        
        # Check for positioned elements
        positioned_elements = soup.find_all(attrs={"style": re.compile(r'position:\s*(absolute|fixed)', re.I)})
        analysis["metrics"]["positioned_elements"] = len(positioned_elements)
        
        if len(positioned_elements) <= 3:
            analysis["strengths"].append("Layout uses minimal absolute positioning - good for responsiveness")
        elif len(positioned_elements) <= 5:
            analysis["strengths"].append("Layout has moderate absolute positioning - manageable")
        else:
            analysis["score"] -= 15
            analysis["issues"].append("Many absolutely positioned elements detected")
            analysis["improvements"].append("Reduce absolute positioning to improve mobile compatibility")
        
        # Whitespace analysis
        container_elements = soup.find_all(['div', 'section', 'article'])
        empty_containers = [el for el in container_elements if not el.get_text(strip=True)]
        analysis["metrics"]["empty_containers"] = len(empty_containers)
        
        total_containers = len(container_elements)
        if total_containers > 0:
            whitespace_ratio = len(empty_containers) / total_containers
            if whitespace_ratio < 0.1:
                analysis["strengths"].append("Good content-to-whitespace balance")
            elif whitespace_ratio > 0.2:
                analysis["improvements"].append("Consider optimizing whitespace for better visual balance")
        
        # Color consistency
        style_elements = soup.find_all(['style'])
        color_usage = []
        
        for style in style_elements:
            if style.string:
                color_matches = re.findall(r'color:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\([^)]+\))', style.string)
                color_usage.extend(color_matches)
        
        unique_colors = len(set(color_usage))
        analysis["metrics"]["unique_colors"] = unique_colors
        
        if unique_colors <= 6:
            analysis["strengths"].append(f"Color palette is cohesive with {unique_colors} main colors")
        elif unique_colors <= 8:
            pass  # Acceptable range
        else:
            analysis["score"] -= 10
            analysis["improvements"].append(f"Simplify color palette from {unique_colors} to 4-6 main colors")
        
        return analysis
    
    async def _analyze_information(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """3. INFORMATIONAL: Check product information completeness"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [],
            "metrics": {},
            "strengths": [],
            "improvements": []
        }
        
        # Product title analysis
        title_selectors = ['h1', '.product-title', '.product-name', '[class*="title"]']
        product_titles = []
        for selector in title_selectors:
            titles = soup.select(selector)
            product_titles.extend([t.get_text(strip=True) for t in titles if t.get_text(strip=True)])
        
        analysis["metrics"]["product_titles"] = len(product_titles)
        
        if product_titles:
            avg_title_length = sum(len(t) for t in product_titles[:3]) / min(3, len(product_titles))
            if avg_title_length <= 60:
                analysis["strengths"].append("Product titles are concise and readable")
            else:
                analysis["score"] -= 10
                analysis["improvements"].append("Shorten product titles to under 60 characters for better scannability")
        
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
        
        if descriptions:
            analysis["strengths"].append(f"Product descriptions present ({len(descriptions)} found) - builds trust")
            total_desc_length = sum(len(d) for d in descriptions)
            if total_desc_length >= 200:
                analysis["strengths"].append("Descriptions are detailed and informative")
        else:
            analysis["score"] -= 25
            analysis["issues"].append("No product descriptions found")
            analysis["improvements"].append("Add detailed product descriptions to build trust and inform customers")
            analysis["improvements"].append("Include features, benefits, and specifications in descriptions")
            analysis["recommendations"].append({
                "category": "information",
                "priority": "high",
                "issue": "Missing product descriptions",
                "solution": "Add detailed product descriptions (150-300 words) highlighting features and benefits",
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
        
        if image_count >= 4:
            analysis["strengths"].append(f"Excellent visual content with {image_count} product images")
        elif image_count >= 2:
            analysis["strengths"].append(f"Good visual representation with {image_count} product images")
        else:
            analysis["score"] -= 20
            analysis["issues"].append(f"Only {image_count} product image(s) found")
            analysis["improvements"].append(f"Increase product images from {image_count} to at least 4 high-quality images")
            analysis["improvements"].append("Include multiple angles, close-ups, and lifestyle shots")
        
        # Check for offers/coupons
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
        
        if offers:
            analysis["strengths"].append(f"Promotional offers visible ({len(offers)} found) - incentivizes purchase")
        else:
            analysis["score"] -= 15
            analysis["improvements"].append("Add promotional offers or discount codes to incentivize purchase")
        
        return analysis
    
    async def _analyze_technical(self, page: Page, url: str) -> Dict[str, Any]:
        """4. TECHNICAL: Lighthouse performance analysis"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [],
            "metrics": {},
            "strengths": [],
            "improvements": [],
            "lighthouse_metrics": None
        }
        
        # Try Lighthouse first if available
        if self.lighthouse_available:
            try:
                lighthouse_results = await self._run_lighthouse(url)
                if lighthouse_results:
                    analysis["lighthouse_metrics"] = lighthouse_results
                    analysis = self._analyze_lighthouse_results(analysis, lighthouse_results)
                    return analysis
            except Exception as e:
                logger.warning(f"Lighthouse analysis failed, using fallback: {e}")
        
        # Fallback to Playwright performance metrics
        try:
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
            
            # Analyze DOM Content Loaded
            dcl_time = performance.get('domContentLoaded', 0)
            if dcl_time < 2000:
                analysis["strengths"].append(f"Fast DOM loading ({dcl_time:.0f}ms) - excellent performance")
            elif dcl_time < 3000:
                analysis["strengths"].append(f"Good DOM loading time ({dcl_time:.0f}ms)")
            else:
                analysis["score"] -= 20
                analysis["issues"].append(f"Slow DOM content loading ({dcl_time:.0f}ms)")
                analysis["improvements"].append("Optimize critical rendering path to reduce DOM load time below 3 seconds")
            
            # Analyze First Contentful Paint
            fcp_time = performance.get('firstContentfulPaint', 0)
            if fcp_time < 1800:
                analysis["strengths"].append(f"Excellent First Contentful Paint ({fcp_time:.0f}ms)")
            elif fcp_time < 2500:
                pass  # Acceptable
            else:
                analysis["score"] -= 15
                analysis["issues"].append(f"Slow first contentful paint ({fcp_time:.0f}ms)")
                analysis["improvements"].append("Improve First Contentful Paint by optimizing above-the-fold content")
        
        except Exception as e:
            logger.warning(f"Performance metrics not available: {e}")
        
        # Image optimization check
        try:
            images = await page.evaluate("""
                () => {
                    const imgs = Array.from(document.images);
                    return imgs.map(img => ({
                        src: img.src,
                        width: img.naturalWidth,
                        height: img.naturalHeight
                    }));
                }
            """)
            
            large_images = [img for img in images if img['width'] > 2000 or img['height'] > 2000]
            analysis["metrics"]["large_images"] = len(large_images)
            analysis["metrics"]["total_images"] = len(images)
            
            if len(large_images) == 0 and len(images) > 0:
                analysis["strengths"].append("Images are properly sized for web delivery")
            elif large_images:
                analysis["score"] -= 10
                analysis["improvements"].append(f"Optimize {len(large_images)} oversized images to improve load time")
        
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
            
            if viewport_meta:
                analysis["strengths"].append("Mobile viewport properly configured")
            else:
                analysis["score"] -= 20
                analysis["issues"].append("No mobile viewport meta tag")
                analysis["improvements"].append("Add viewport meta tag for mobile responsiveness")
        
        except Exception as e:
            logger.warning(f"Viewport check failed: {e}")
        
        return analysis
    
    async def _run_lighthouse(self, url: str) -> Optional[LighthouseMetrics]:
        """Run Lighthouse CLI and parse results"""
        try:
            # Create temp file for results
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                output_path = f.name
            
            # Run Lighthouse
            cmd = [
                'lighthouse',
                url,
                '--output=json',
                f'--output-path={output_path}',
                '--chrome-flags="--headless --no-sandbox"',
                '--only-categories=performance,accessibility,best-practices,seo',
                '--quiet'
            ]
            
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.warning(f"Lighthouse failed: {result.stderr}")
                return None
            
            # Parse results
            with open(output_path, 'r') as f:
                lighthouse_data = json.load(f)
            
            # Extract metrics
            metrics = LighthouseMetrics(
                performance_score=int(lighthouse_data['categories']['performance']['score'] * 100),
                accessibility_score=int(lighthouse_data['categories']['accessibility']['score'] * 100),
                best_practices_score=int(lighthouse_data['categories']['best-practices']['score'] * 100),
                seo_score=int(lighthouse_data['categories']['seo']['score'] * 100),
                first_contentful_paint=lighthouse_data['audits']['first-contentful-paint']['numericValue'],
                speed_index=lighthouse_data['audits']['speed-index']['numericValue'],
                largest_contentful_paint=lighthouse_data['audits']['largest-contentful-paint']['numericValue'],
                time_to_interactive=lighthouse_data['audits']['interactive']['numericValue'],
                total_blocking_time=lighthouse_data['audits']['total-blocking-time']['numericValue'],
                cumulative_layout_shift=lighthouse_data['audits']['cumulative-layout-shift']['numericValue'],
                lighthouse_available=True
            )
            
            logger.info(f"✅ Lighthouse analysis completed - Performance: {metrics.performance_score}")
            return metrics
            
        except Exception as e:
            logger.warning(f"Lighthouse execution failed: {e}")
            return None
    
    def _analyze_lighthouse_results(self, analysis: Dict[str, Any], metrics: LighthouseMetrics) -> Dict[str, Any]:
        """Analyze Lighthouse results and generate feedback"""
        
        # Performance Score
        perf_score = metrics.performance_score
        if perf_score >= 90:
            analysis["strengths"].append(f"Excellent Lighthouse performance score: {perf_score}/100")
        elif perf_score >= 75:
            analysis["strengths"].append(f"Good Lighthouse performance score: {perf_score}/100")
            analysis["score"] -= 10
        elif perf_score >= 50:
            analysis["issues"].append(f"Average performance score: {perf_score}/100")
            analysis["improvements"].append("Optimize page performance to achieve 90+ Lighthouse score")
            analysis["score"] -= 20
        else:
            analysis["issues"].append(f"Poor performance score: {perf_score}/100")
            analysis["improvements"].append("Critical performance issues need immediate attention")
            analysis["score"] -= 30
        
        # First Contentful Paint
        fcp = metrics.first_contentful_paint / 1000  # Convert to seconds
        if fcp < 1.8:
            analysis["strengths"].append(f"Fast First Contentful Paint: {fcp:.2f}s")
        elif fcp < 3.0:
            pass  # Acceptable
        else:
            analysis["improvements"].append(f"Reduce First Contentful Paint from {fcp:.2f}s to under 1.8s")
        
        # Largest Contentful Paint
        lcp = metrics.largest_contentful_paint / 1000
        if lcp < 2.5:
            analysis["strengths"].append(f"Good Largest Contentful Paint: {lcp:.2f}s")
        else:
            analysis["improvements"].append(f"Optimize Largest Contentful Paint from {lcp:.2f}s to under 2.5s")
        
        # Cumulative Layout Shift
        if metrics.cumulative_layout_shift < 0.1:
            analysis["strengths"].append("Excellent visual stability (low layout shift)")
        elif metrics.cumulative_layout_shift < 0.25:
            pass  # Acceptable
        else:
            analysis["improvements"].append("Reduce layout shifts by specifying image dimensions and reserving space for ads")
        
        return analysis
    
    async def _analyze_psychological(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """5. PSYCHOLOGICAL: Trust signals and user psychology"""
        
        analysis = {
            "score": 100,
            "issues": [],
            "recommendations": [],
            "metrics": {},
            "strengths": [],
            "improvements": []
        }
        
        # Trust badges
        trust_selectors = [
            '.trust', '.security', '.badge', '.verified', '.guarantee',
            '[class*="trust"]', '[class*="security"]', '[class*="verified"]'
        ]
        
        trust_elements = []
        for selector in trust_selectors:
            elements = soup.select(selector)
            trust_elements.extend(elements)
        
        analysis["metrics"]["trust_badges"] = len(trust_elements)
        
        if len(trust_elements) >= 3:
            analysis["strengths"].append(f"Strong trust signals with {len(trust_elements)} badges/guarantees visible")
        elif len(trust_elements) >= 2:
            analysis["strengths"].append(f"Trust signals present ({len(trust_elements)} found)")
        else:
            analysis["score"] -= 20
            analysis["issues"].append("Insufficient trust signals")
            analysis["improvements"].append("Add security badges, payment icons, and trust seals")
            analysis["improvements"].append("Display customer testimonials or reviews prominently")
        
        # Return policy
        return_policy_indicators = soup.find_all(text=re.compile(r'return|refund|guarantee', re.I))
        analysis["metrics"]["has_return_policy"] = len(return_policy_indicators) > 0
        
        if return_policy_indicators:
            analysis["strengths"].append("Return/refund policy is mentioned - reduces purchase anxiety")
        else:
            analysis["score"] -= 15
            analysis["improvements"].append("Make return/refund policy clearly visible to build confidence")
        
        # FAQ section
        faq_found = False
        faq_selectors = ['.faq', '.frequently-asked', '[class*="faq"]', 'h1, h2, h3, h4, h5, h6']
        
        for selector in faq_selectors:
            elements = soup.select(selector)
            for element in elements:
                if re.search(r'faq|frequently.{0,10}asked', element.get_text(), re.I):
                    faq_found = True
                    break
            if faq_found:
                break
        
        analysis["metrics"]["has_faq"] = faq_found
        
        if faq_found:
            analysis["strengths"].append("FAQ section present - addresses common concerns proactively")
        else:
            analysis["score"] -= 10
            analysis["improvements"].append("Add FAQ section to address common questions and concerns")
        
        # Contact information
        contact_indicators = soup.find_all(text=re.compile(r'contact|support|help|email|phone', re.I))
        if len(contact_indicators) > 3:
            analysis["strengths"].append("Contact information is accessible - builds trust")
        
        return analysis
    
    def _calculate_framework_score(self, analyses: List[Dict[str, Any]]) -> int:
        """Calculate overall framework score"""
        if not analyses:
            return 0
        
        total_score = sum(analysis.get('score', 0) for analysis in analyses)
        return total_score // len(analyses)
    
    def get_framework_insights(self, framework_results: Dict[str, Any]) -> AIInsights:
        """Convert framework results to AIInsights with detailed feedback"""
        
        # Calculate category scores
        category_scores = {
            "navigation": framework_results.get('navigation', {}).get('score', 100),
            "display": framework_results.get('display', {}).get('score', 100),
            "information": framework_results.get('information', {}).get('score', 100),
            "technical": framework_results.get('technical', {}).get('score', 100),
            "psychological": framework_results.get('psychological', {}).get('score', 100)
        }
        
        # Generate framework feedback for each category
        framework_feedback = []
        for category in ["navigation", "display", "information", "technical", "psychological"]:
            if category in framework_results:
                cat_data = framework_results[category]
                feedback = FrameworkFeedback(
                    category=category,
                    score=cat_data.get('score', 100),
                    strengths=cat_data.get('strengths', [])[:4],  # Limit to 4
                    improvements=cat_data.get('improvements', [])[:4],  # Limit to 4
                    metrics=cat_data.get('metrics', {})
                )
                framework_feedback.append(feedback)
        
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
        
        # Generate recommendations
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
        
        # Extract Lighthouse metrics if available
        lighthouse_metrics = None
        if 'technical' in framework_results:
            lighthouse_metrics = framework_results['technical'].get('lighthouse_metrics')
        
        return AIInsights(
            overall_score=framework_results.get('overall_framework_score', 100),
            category_scores=category_scores,
            recommendations=recommendations,
            visual_issues=visual_issues[:10],
            mobile_issues=mobile_issues[:5],
            framework_feedback=framework_feedback,
            lighthouse_metrics=lighthouse_metrics
        )
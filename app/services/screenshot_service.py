"""Screenshot capture service using Playwright"""

import asyncio
import logging
from playwright.async_api import async_playwright
from typing import Tuple

logger = logging.getLogger(__name__)

class ScreenshotService:
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
            logger.info("✅ Screenshot service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize screenshot service: {e}")
            raise
    
    async def capture_website(self, url: str) -> Tuple[bytes, bytes]:
        """Capture desktop and mobile screenshots"""
        if not self.browser:
            await self.initialize()
        
        desktop_screenshot = None
        mobile_screenshot = None
        
        try:
            # Desktop screenshot
            page = await self.browser.new_page()
            
            # Set a real user agent to avoid bot detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            })
            
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # More lenient navigation - use domcontentloaded instead of networkidle
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)  # Increased timeout
            await page.wait_for_timeout(3000)  # Wait a bit more for dynamic content
            
            desktop_screenshot = await page.screenshot(full_page=True)
            await page.close()
            
            # Mobile screenshot
            page = await self.browser.new_page()
            
            # Set mobile user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            })
            
            await page.set_viewport_size({"width": 375, "height": 667})  # iPhone 8
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)  # Increased timeout
            await page.wait_for_timeout(3000)
            
            mobile_screenshot = await page.screenshot(full_page=True)
            await page.close()
            
            logger.info(f"📸 Screenshots captured for {url}")
            
        except Exception as e:
            logger.error(f"Screenshot capture failed for {url}: {e}")
            raise
        
        return desktop_screenshot, mobile_screenshot
    
    async def close(self):
        """Close browser and playwright"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
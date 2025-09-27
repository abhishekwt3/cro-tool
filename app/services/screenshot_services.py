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
                args=['--no-sandbox', '--disable-dev-shm-usage']
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
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)  # Wait for dynamic content
            desktop_screenshot = await page.screenshot(full_page=True)
            await page.close()
            
            # Mobile screenshot
            page = await self.browser.new_page()
            await page.set_viewport_size({"width": 375, "height": 667})  # iPhone 8
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
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
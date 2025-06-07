import asyncio
from typing import List, Optional
from playwright.async_api import async_playwright
from schemas import ReelItem
from config import settings
import logging

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT
        self.base_url = settings.INSTAGRAM_BASE_URL

    async def scrape_reels(self, username: str, limit: int = settings.REELS_LIMIT) -> List[ReelItem]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=settings.HEADLESS)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            try:
                # Navigate to profile page
                profile_url = f"{self.base_url}/{username}/"
                logger.info(f"Scraping profile: {profile_url}")
                await page.goto(profile_url, timeout=self.timeout)
                
                # Check if account exists or is private
                if await self._is_account_unavailable(page):
                    raise ValueError(f"Account @{username} not found or is private")
                
                # Scroll to load more reels
                await self._scroll_page(page, scroll_count=3)
                
                # Extract reels data
                reels = await page.query_selector_all('a[href*="/reel/"]')
                if not reels:
                    raise ValueError(f"No reels found for @{username}")
                
                # Process reels
                reels_data = []
                for reel in reels[:limit]:
                    try:
                        reel_data = await self._extract_reel_data(reel)
                        reels_data.append(reel_data)
                    except Exception as e:
                        logger.error(f"Error processing reel: {str(e)}")
                        continue
                
                return reels_data
            
            finally:
                await browser.close()
    
    async def _is_account_unavailable(self, page) -> bool:
        error_element = await page.query_selector('._ab1y')
        if error_element:
            error_text = await error_element.inner_text()
            return "Sorry, this page isn't available." in error_text
        return False
    
    async def _scroll_page(self, page, scroll_count: int = 3):
        for _ in range(scroll_count):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
    
    async def _extract_reel_data(self, reel_element) -> ReelItem:
        reel_url = await reel_element.get_attribute('href')
        full_reel_url = f"{self.base_url}{reel_url}"
        reel_id = reel_url.split('/reel/')[1].strip('/')
        
        # Get thumbnail URL
        thumbnail = await reel_element.query_selector('img')
        thumbnail_url = await thumbnail.get_attribute('src') if thumbnail else None
        
        # Get caption (from aria-label)
        caption = await reel_element.get_attribute('aria-label')
        
        return ReelItem(
            id=reel_id,
            reel_url=full_reel_url,
            video_url=None,  # Would need to visit individual reel page
            thumbnail_url=thumbnail_url,
            caption=caption,
            posted_at=None,
            views=None,
            likes=None,
            comments=None
        )
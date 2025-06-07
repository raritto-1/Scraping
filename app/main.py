from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from schemas import ReelItem, ScrapeRequest
from scraper import InstagramScraper
import logging
import uvicorn

app = FastAPI(
    title="Instagram Reels Scraper API",
    description="API for scraping public Instagram Reels",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

scraper = InstagramScraper()

@app.get("/scrape", response_model=list[ReelItem])
async def scrape_reels(
    username: str = Query(..., description="Instagram username to scrape"),
    limit: int = Query(30, description="Maximum number of reels to return", ge=1, le=50)
):
    """
    Scrape reels from a public Instagram account via GET request
    """
    try:
        logger.info(f"Scraping reels for @{username}")
        return await scraper.scrape_reels(username, limit)
    except Exception as e:
        logger.error(f"Error scraping reels: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/scrape", response_model=list[ReelItem])
async def scrape_reels_post(request: ScrapeRequest):
    """
    Scrape reels from a public Instagram account via POST request
    """
    try:
        logger.info(f"Scraping reels for @{request.username}")
        return await scraper.scrape_reels(request.username, request.limit)
    except Exception as e:
        logger.error(f"Error scraping reels: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
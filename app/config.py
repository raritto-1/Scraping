import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    INSTAGRAM_BASE_URL = "https://www.instagram.com"
    REELS_LIMIT = int(os.getenv("REELS_LIMIT", 30))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30000))  # 30 seconds
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

settings = Settings()
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReelItem(BaseModel):
    id: str
    reel_url: str
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    caption: Optional[str]
    posted_at: Optional[datetime]
    views: Optional[int]
    likes: Optional[int]
    comments: Optional[int]

class ScrapeRequest(BaseModel):
    username: str
    limit: Optional[int] = 30
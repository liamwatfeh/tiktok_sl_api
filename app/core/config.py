import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "TikTok Social Media Analysis API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered TikTok hashtag conversation analysis"
    
    # TikTok API Configuration (RapidAPI)
    TIKTOK_RAPIDAPI_KEY: str = Field(..., env="TIKTOK_RAPIDAPI_KEY")
    TIKTOK_RAPIDAPI_HOST: str = "tiktok-scrapper-videos-music-challenges-downloader.p.rapidapi.com"
    TIKTOK_BASE_URL: str = "https://tiktok-scrapper-videos-music-challenges-downloader.p.rapidapi.com"
    
    # AI Configuration
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    DEFAULT_MODEL: str = "gpt-4.1-2025-04-14"
    MAX_CONCURRENT_AGENTS: int = 3
    
    # Authentication
    SERVICE_API_KEY: str = Field(..., env="SERVICE_API_KEY")
    
    # Processing Limits
    MAX_POSTS_PER_REQUEST: int = 50
    DEFAULT_POSTS_PER_REQUEST: int = 20
    MAX_QUOTE_LENGTH: int = 200
    
    # Comments Processing
    MAX_COMMENTS_PER_VIDEO: int = 100
    DEFAULT_COMMENTS_PER_VIDEO: int = 50
    
    # Request Configuration
    REQUEST_TIMEOUT: float = 250.0
    TIKTOK_REQUEST_DELAY: float = 0.1  # 100ms between requests
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # 1 second between retries
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"

settings = Settings()

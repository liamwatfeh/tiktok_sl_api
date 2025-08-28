from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """
    Application configuration settings.
    
    All settings can be overridden via environment variables.
    Sensitive values (API keys) must be provided via environment variables.
    """
    # API Configuration
    API_TITLE: str = Field(
        default="TikTok Social Media Analysis API",
        description="API title for documentation"
    )
    API_VERSION: str = Field(
        default="1.0.0",
        description="API version"
    )
    API_DESCRIPTION: str = Field(
        default="AI-powered TikTok hashtag conversation analysis",
        description="API description for documentation"
    )
    
    # TikTok API Configuration (RapidAPI)
    TIKTOK_RAPIDAPI_KEY: str = Field(
        ..., 
        env="TIKTOK_RAPIDAPI_KEY",
        description="TikTok RapidAPI key (required)",
        min_length=10
    )
    TIKTOK_RAPIDAPI_HOST: str = Field(
        default="tiktok-scrapper-videos-music-challenges-downloader.p.rapidapi.com",
        env="TIKTOK_RAPIDAPI_HOST",
        description="TikTok RapidAPI host"
    )
    TIKTOK_BASE_URL: str = Field(
        default="https://tiktok-scrapper-videos-music-challenges-downloader.p.rapidapi.com",
        env="TIKTOK_BASE_URL",
        description="TikTok API base URL"
    )
    
    # AI Configuration
    OPENAI_API_KEY: str = Field(
        ..., 
        env="OPENAI_API_KEY",
        description="OpenAI API key (required)",
        min_length=20
    )
    DEFAULT_MODEL: str = Field(
        default="gpt-4.1-2025-04-14",
        env="DEFAULT_MODEL",
        description="Default OpenAI model to use"
    )
    MAX_CONCURRENT_AGENTS: int = Field(
        default=3,
        env="MAX_CONCURRENT_AGENTS",
        description="Maximum concurrent AI analysis calls",
        ge=1, le=10
    )
    
    # Authentication
    SERVICE_API_KEY: str = Field(
        ..., 
        env="SERVICE_API_KEY",
        description="API key for service authentication (required)",
        min_length=16
    )
    
    # Processing Limits
    MAX_POSTS_PER_REQUEST: int = Field(
        default=50,
        env="MAX_POSTS_PER_REQUEST",
        description="Maximum videos per request",
        ge=1, le=100
    )
    DEFAULT_POSTS_PER_REQUEST: int = Field(
        default=20,
        env="DEFAULT_POSTS_PER_REQUEST",
        description="Default number of videos per request",
        ge=1, le=50
    )
    MAX_QUOTE_LENGTH: int = Field(
        default=200,
        env="MAX_QUOTE_LENGTH",
        description="Maximum length for extracted quotes",
        ge=50, le=500
    )
    MAX_CONCURRENT_AGENTS: int = Field(
        default=3,
        env="MAX_CONCURRENT_AGENTS", 
        description="Maximum concurrent OpenAI API calls for video analysis",
        ge=1, le=10
    )
    
    # Comments Processing
    MAX_COMMENTS_PER_VIDEO: int = Field(
        default=100,
        env="MAX_COMMENTS_PER_VIDEO",
        description="Maximum comments to collect per video",
        ge=10, le=200
    )
    DEFAULT_COMMENTS_PER_VIDEO: int = Field(
        default=50,
        env="DEFAULT_COMMENTS_PER_VIDEO",
        description="Default number of comments per video",
        ge=10, le=100
    )
    
    # Request Configuration
    REQUEST_TIMEOUT: float = Field(
        default=250.0,
        env="REQUEST_TIMEOUT",
        description="HTTP request timeout in seconds",
        ge=30.0, le=300.0
    )
    TIKTOK_REQUEST_DELAY: float = Field(
        default=0.1,
        env="TIKTOK_REQUEST_DELAY",
        description="Delay between TikTok API requests in seconds",
        ge=0.0, le=5.0
    )
    MAX_RETRIES: int = Field(
        default=3,
        env="MAX_RETRIES",
        description="Maximum number of retries for failed requests",
        ge=0, le=10
    )
    RETRY_DELAY: float = Field(
        default=1.0,
        env="RETRY_DELAY",
        description="Delay between retries in seconds",
        ge=0.1, le=10.0
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # Environment
    ENVIRONMENT: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Application environment (development, staging, production)"
    )
    
    # Server Configuration
    PORT: int = Field(
        default=8000,
        env="PORT",
        description="Port for the server to listen on (Railway sets this automatically)",
        ge=1, le=65535
    )
    
    # Testing mode
    USE_MOCK_DATA: bool = Field(
        default=False,
        env="USE_MOCK_DATA",
        description="Use mock data instead of real TikTok API calls (for testing)"
    )
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level is one of the allowed values."""
        allowed_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in allowed_levels:
            raise ValueError(f'LOG_LEVEL must be one of: {allowed_levels}')
        return v.upper()
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        """Validate environment is one of the allowed values."""
        allowed_envs = {'development', 'staging', 'production'}
        if v.lower() not in allowed_envs:
            raise ValueError(f'ENVIRONMENT must be one of: {allowed_envs}')
        return v.lower()
    
    @validator('DEFAULT_POSTS_PER_REQUEST')
    def validate_default_posts(cls, v, values):
        """Ensure default posts doesn't exceed maximum."""
        max_posts = values.get('MAX_POSTS_PER_REQUEST', 50)
        if v > max_posts:
            raise ValueError(f'DEFAULT_POSTS_PER_REQUEST ({v}) cannot exceed MAX_POSTS_PER_REQUEST ({max_posts})')
        return v
    
    @validator('DEFAULT_COMMENTS_PER_VIDEO')
    def validate_default_comments(cls, v, values):
        """Ensure default comments doesn't exceed maximum."""
        max_comments = values.get('MAX_COMMENTS_PER_VIDEO', 100)
        if v > max_comments:
            raise ValueError(f'DEFAULT_COMMENTS_PER_VIDEO ({v}) cannot exceed MAX_COMMENTS_PER_VIDEO ({max_comments})')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True
        extra = "forbid"  # Prevent extra fields

settings = Settings()

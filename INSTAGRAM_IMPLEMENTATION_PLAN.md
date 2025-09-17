# 📸 Instagram Social Listening API - Comprehensive Implementation Plan

> **For Cursor Agent Mode**: Step-by-step implementation guide with narrow, focused tasks that can be executed incrementally by AI agents.

## 🎯 **Project Overview**

**Goal**: Create an Instagram social listening API with 5 endpoints that analyze hashtags, search posts, search reels, user posts, and user reels for sentiment, themes, and purchase intent using the Real-Time Instagram Scraper API and OpenAI.

**Architecture**: Duplicate the proven TikTok API structure for Instagram with 80% code reuse.

**Timeline**: 8 weeks across 4 phases

**Cost per Analysis**: ~$1.01 (21 Instagram API calls + 20 OpenAI calls)

**5 Endpoints**:
1. **`/analyze-instagram-hashtags`** - Hashtag feed analysis
2. **`/analyze-instagram-search-posts`** - Search posts by keyword  
3. **`/analyze-instagram-search-reels`** - Search reels by keyword
4. **`/analyze-instagram-user-posts`** - User posts analysis
5. **`/analyze-instagram-user-reels`** - User reels analysis

---

## 📋 **Phase 1: Foundation Setup** (Week 1-2)

### **Task 1.1: Project Structure Setup**
Create the basic project structure mirroring the TikTok API:

**Steps for Cursor Agent**:
1. Create new directory `instagram_sl_api` 
2. Copy the following structure from the TikTok project:
   ```
   instagram_sl_api/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── core/
   │   │   ├── __init__.py
   │   │   ├── config.py
   │   │   └── exceptions.py
   │   ├── models/
   │   │   ├── __init__.py
   │   │   └── instagram_schemas.py
   │   └── services/
   │       ├── __init__.py
   │       ├── instagram_hashtags/
   │       │   ├── __init__.py
   │       │   └── hashtag_service.py
   │       ├── instagram_search_posts/
   │       │   ├── __init__.py
   │       │   └── search_posts_service.py
   │       ├── instagram_search_reels/
   │       │   ├── __init__.py
   │       │   └── search_reels_service.py
   │       ├── instagram_user_posts/
   │       │   ├── __init__.py
   │       │   └── user_posts_service.py
   │       ├── instagram_user_reels/
   │       │   ├── __init__.py
   │       │   └── user_reels_service.py
   │       └── instagram_shared/
   │           ├── __init__.py
   │           ├── instagram_api_client.py
   │           ├── instagram_comment_collector.py
   │           ├── instagram_data_cleaners.py
   │           ├── instagram_ai_analyzer.py
   │           └── instagram_response_builder.py
   ├── requirements.txt
   ├── .env.example
   ├── .gitignore
   └── README.md
   ```

**Deliverable**: Clean project structure with empty files ready for implementation.

### **Task 1.2: Environment Configuration**
Set up configuration management for Instagram API keys.

**Edit `app/core/config.py`**:
```python
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = Field(
        default="Instagram Social Media Analysis API",
        description="API title for documentation"
    )
    API_VERSION: str = Field(
        default="1.0.0", 
        description="API version"
    )
    
    # Instagram API Configuration (RapidAPI)
    INSTAGRAM_RAPIDAPI_KEY: str = Field(
        ...,
        env="INSTAGRAM_RAPIDAPI_KEY",
        description="Instagram RapidAPI key (required)",
        min_length=10
    )
    INSTAGRAM_RAPIDAPI_HOST: str = Field(
        default="real-time-instagram-scraper-api1.p.rapidapi.com",
        env="INSTAGRAM_RAPIDAPI_HOST",
        description="Instagram RapidAPI host"
    )
    INSTAGRAM_BASE_URL: str = Field(
        default="https://real-time-instagram-scraper-api1.p.rapidapi.com",
        env="INSTAGRAM_BASE_URL",
        description="Instagram API base URL"
    )
    
    # AI Configuration
    OPENAI_API_KEY: str = Field(
        ...,
        env="OPENAI_API_KEY", 
        description="OpenAI API key (required)",
        min_length=20
    )
    DEFAULT_MODEL: str = Field(
        default="gpt-4-turbo-2024-04-09",
        env="DEFAULT_MODEL",
        description="Default OpenAI model to use"
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
        description="Maximum posts per request",
        ge=1, le=100
    )
    DEFAULT_POSTS_PER_REQUEST: int = Field(
        default=20,
        env="DEFAULT_POSTS_PER_REQUEST", 
        description="Default number of posts per request",
        ge=1, le=50
    )
    MAX_COMMENTS_PER_POST: int = Field(
        default=50,
        env="MAX_COMMENTS_PER_POST",
        description="Maximum comments to collect per post",
        ge=10, le=100
    )
    
    # Request Configuration  
    REQUEST_TIMEOUT: float = Field(
        default=30.0,
        env="REQUEST_TIMEOUT",
        description="HTTP request timeout in seconds",
        ge=10.0, le=120.0
    )
    INSTAGRAM_REQUEST_DELAY: float = Field(
        default=0.5,
        env="INSTAGRAM_REQUEST_DELAY",
        description="Delay between Instagram API requests in seconds",
        ge=0.0, le=5.0
    )
    
    # Environment
    ENVIRONMENT: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Application environment"
    )
    
    # Server Configuration
    PORT: int = Field(
        default=8000,
        env="PORT",
        description="Port for the server to listen on",
        ge=1, le=65535
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
```

**Create `.env.example`**:
```env
# Instagram API (RapidAPI)
INSTAGRAM_RAPIDAPI_KEY=your_rapidapi_key_here
INSTAGRAM_RAPIDAPI_HOST=real-time-instagram-scraper-api1.p.rapidapi.com
INSTAGRAM_BASE_URL=https://real-time-instagram-scraper-api1.p.rapidapi.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
DEFAULT_MODEL=gpt-4-turbo-2024-04-09

# Service Authentication
SERVICE_API_KEY=your_service_api_key_here

# Processing Configuration
MAX_POSTS_PER_REQUEST=50
DEFAULT_POSTS_PER_REQUEST=20
MAX_COMMENTS_PER_POST=50
REQUEST_TIMEOUT=30.0
INSTAGRAM_REQUEST_DELAY=0.5

# Environment
ENVIRONMENT=development
PORT=8000
```

**Deliverable**: Complete configuration management ready for Instagram API keys.

### **Task 1.3: Dependencies and Requirements**
Set up the required Python packages with latest versions as of December 2024.

**Create/Update `requirements.txt`**:
```txt
# Core FastAPI and Web Framework (Latest versions)
fastapi[standard]==0.115.6
uvicorn[standard]==0.32.2

# Pydantic for data validation and settings (Latest)
pydantic==2.10.4
pydantic-settings==2.6.2

# AI/ML Dependencies (Latest)
openai==1.58.1

# HTTP Client and Networking (Latest)
httpx==0.28.1
requests==2.32.3

# Environment and Configuration
python-dotenv==1.0.1

# Rate Limiting and Throttling
slowapi==0.1.9
asyncio-throttle==1.0.2

# Development and Testing (Latest)
pytest==8.3.4
pytest-asyncio==0.25.0
pytest-httpx==0.31.2

# Logging and Monitoring
structlog==24.5.0

# Data Processing (Latest)
pandas==2.2.3
numpy==2.2.1

# Additional FastAPI Extensions
python-multipart==0.0.12

# Instagram API Integration (Optional - if using alternative libraries)
# Note: We'll use RapidAPI Instagram scraper instead, but these are alternatives:
# instagrapi==2.1.2  # Direct Instagram private API (use with caution)
# pystagram==0.1.0   # Instagram Graph API wrapper (if using official API)

# Security and Authentication
cryptography==43.0.3
python-jose[cryptography]==3.3.0

# Database (if needed for caching)
redis==5.2.0
sqlalchemy==2.0.36
```

**Modern Dependency Management Alternative (Recommended)**:
Create `pyproject.toml` for modern Python projects:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "instagram-social-listening-api"
version = "1.0.0"
description = "AI-powered Instagram social media analysis API"
requires-python = ">=3.11"
dependencies = [
    "fastapi[standard]==0.115.6",
    "uvicorn[standard]==0.32.2",
    "pydantic==2.10.4",
    "pydantic-settings==2.6.2",
    "openai==1.58.1",
    "httpx==0.28.1",
    "requests==2.32.3",
    "python-dotenv==1.0.1",
    "slowapi==0.1.9",
    "structlog==24.5.0",
    "pandas==2.2.3",
    "numpy==2.2.1",
    "python-multipart==0.0.12",
    "cryptography==43.0.3",
]

[project.optional-dependencies]
dev = [
    "pytest==8.3.4",
    "pytest-asyncio==0.25.0",
    "pytest-httpx==0.31.2",
]
```

**Steps for Cursor Agent**:
1. Create both `requirements.txt` and `pyproject.toml` (modern approach)
2. Use exact version pinning for reproducibility
3. Include security-focused packages (cryptography, python-jose)
4. Add optional Instagram API libraries as comments
5. Test installation: `pip install -r requirements.txt`
6. Verify all packages install without conflicts

**Key Updates for December 2024**:
- **FastAPI 0.115.6**: Latest stable with improved performance
- **Pydantic 2.10.4**: Enhanced validation and serialization
- **OpenAI 1.58.1**: Latest SDK with improved streaming and error handling
- **Security packages**: Added cryptography and python-jose for robust auth
- **Modern format**: Included pyproject.toml as the new standard

**Deliverable**: Complete, modern dependency management with latest stable versions.

### **Task 1.4: Exception Handling Setup**
Copy and adapt the exception handling from TikTok API.

**Edit `app/core/exceptions.py`**:
```python
import logging
from typing import Optional, Dict, Any
from datetime import datetime

class InstagramAPIException(Exception):
    """Base exception for Instagram API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None,
        log_level: str = "ERROR"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self._generate_error_code()
        self.details = self._sanitize_details(details or {})
        self.log_level = log_level
        self.timestamp = datetime.utcnow().isoformat()
        
        # Log the exception
        logger = logging.getLogger(self.__class__.__module__)
        getattr(logger, log_level.lower(), logger.error)(
            f"{self.error_code}: {self.message}",
            extra={
                "error_code": self.error_code,
                "status_code": self.status_code,
                "details": self.details,
                "timestamp": self.timestamp
            }
        )
        
        super().__init__(self.message)
    
    def _generate_error_code(self) -> str:
        """Generate error code from class name."""
        class_name = self.__class__.__name__
        if class_name.endswith('Error'):
            class_name = class_name[:-5]
        return class_name.upper()
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize details to prevent sensitive information leakage."""
        sanitized = {}
        sensitive_keys = {'password', 'token', 'key', 'secret', 'auth', 'api_key'}
        
        for key, value in details.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + "...[TRUNCATED]"
            else:
                sanitized[key] = value
                
        return sanitized
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "status_code": self.status_code
        }

class InstagramValidationError(InstagramAPIException):
    """Request validation error."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["provided_value"] = value
        super().__init__(message, status_code=400, details=details)

class InstagramDataCollectionError(InstagramAPIException):
    """Instagram data collection error."""
    
    def __init__(self, message: str, api_endpoint: Optional[str] = None, http_status: Optional[int] = None):
        details = {}
        if api_endpoint:
            details["api_endpoint"] = api_endpoint
        if http_status:
            details["http_status"] = http_status
        super().__init__(message, status_code=502, details=details)

class InstagramAnalysisError(InstagramAPIException):
    """AI analysis error."""
    
    def __init__(self, message: str, model: Optional[str] = None, post_id: Optional[str] = None):
        details = {}
        if model:
            details["model"] = model
        if post_id:
            details["post_id"] = post_id
        super().__init__(message, status_code=503, details=details)

class RateLimitExceededError(InstagramAPIException):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str, service: Optional[str] = None, retry_after: Optional[int] = None):
        details = {}
        if service:
            details["service"] = service
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, status_code=429, details=details, log_level="WARNING")

class AuthenticationError(InstagramAPIException):
    """Authentication error."""
    
    def __init__(self, message: str, auth_type: Optional[str] = None):
        details = {"auth_type": auth_type} if auth_type else {}
        super().__init__(message, status_code=401, details=details, log_level="WARNING")
```

**Deliverable**: Complete exception handling system ready for Instagram-specific errors.

---

## 📋 **Phase 2: Core API Infrastructure** (Week 3-4)

### **Task 2.1: Data Models and Schemas**
Create Pydantic models for Instagram API requests and responses.

**Edit `app/models/instagram_schemas.py`**:
```python
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

# ===== ACTUAL INSTAGRAM API DATA MODELS =====
# Based on real RapidAPI response schemas

class InstagramUser(BaseModel):
    """Instagram user data from API response"""
    pk: str = Field(..., description="User primary key")
    pk_id: str = Field(..., description="User primary key ID") 
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Display name")
    is_private: bool = Field(default=False, description="Private account")
    is_verified: bool = Field(default=False, description="Verified account")
    profile_pic_url: str = Field(..., description="Profile picture URL")
    strong_id__: str = Field(..., description="Strong ID")

class InstagramImageVersion(BaseModel):
    """Image version with different sizes"""
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    url: str = Field(..., description="Image URL")

class InstagramImageVersions(BaseModel):
    """Image versions container"""
    candidates: List[InstagramImageVersion] = Field(default=[], description="Available image sizes")

class InstagramCarouselItem(BaseModel):
    """Individual item in carousel post"""
    id: str = Field(..., description="Carousel item ID")
    pk: str = Field(..., description="Carousel item primary key")
    media_type: int = Field(..., description="1=image, 2=video")
    image_versions2: Optional[InstagramImageVersions] = Field(None, description="Image versions")
    accessibility_caption: Optional[str] = Field(None, description="Alt text")

class InstagramVideoVersion(BaseModel):
    """Video version with different qualities"""
    bandwidth: int = Field(..., description="Video bandwidth")
    height: int = Field(..., description="Video height")
    width: int = Field(..., description="Video width")
    id: str = Field(..., description="Video version ID")
    type: int = Field(..., description="Video type")
    url: str = Field(..., description="Video URL")

class InstagramOriginalSoundInfo(BaseModel):
    """Original sound/audio information for reels"""
    audio_asset_id: int = Field(..., description="Audio asset ID")
    duration_in_ms: int = Field(..., description="Audio duration in milliseconds")
    original_audio_title: str = Field(..., description="Audio title")
    progressive_download_url: str = Field(..., description="Audio download URL")
    should_mute_audio: bool = Field(default=False, description="Should mute audio")

class InstagramPost(BaseModel):
    """Single Instagram post from hashtag/user feed"""
    pk: str = Field(..., description="Post primary key")
    id: str = Field(..., description="Post ID with user suffix")
    code: str = Field(..., description="Post shortcode")
    strong_id__: str = Field(..., description="Strong ID")
    media_type: int = Field(..., description="1=image, 2=video, 8=carousel")
    taken_at: int = Field(..., description="Unix timestamp")
    created_at: int = Field(..., description="Creation timestamp")
    caption: Optional[str] = Field(None, description="Post caption")
    like_count: int = Field(default=0, description="Number of likes")
    comment_count: int = Field(default=0, description="Number of comments")
    user: InstagramUser = Field(..., description="Post author")
    owner: InstagramUser = Field(..., description="Post owner (same as user)")
    image_versions2: Optional[InstagramImageVersions] = Field(None, description="Image versions")
    carousel_media: Optional[List[InstagramCarouselItem]] = Field(None, description="Carousel items")
    carousel_media_count: Optional[int] = Field(None, description="Number of carousel items")
    accessibility_caption: Optional[str] = Field(None, description="Alt text")
    
    # Reel-specific fields
    play_count: Optional[int] = Field(None, description="Video play count (reels only)")
    video_duration: Optional[float] = Field(None, description="Video duration in seconds (reels only)")
    video_versions: Optional[List[InstagramVideoVersion]] = Field(None, description="Video quality versions (reels only)")
    original_sound_info: Optional[InstagramOriginalSoundInfo] = Field(None, description="Original audio info (reels only)")
    has_audio: Optional[bool] = Field(None, description="Whether video has audio (reels only)")
    
    @property
    def instagram_url(self) -> str:
        """Generate Instagram post URL from shortcode"""
        return f"https://www.instagram.com/p/{self.code}/"
    
    @property 
    def media_type_name(self) -> str:
        """Get human-readable media type"""
        type_map = {1: "photo", 2: "video", 8: "carousel"}
        return type_map.get(self.media_type, "unknown")

class InstagramComment(BaseModel):
    """Instagram comment from post"""
    pk: str = Field(..., description="Comment ID")
    text: str = Field(..., description="Comment text")
    created_at: int = Field(..., description="Unix timestamp")
    like_count: int = Field(default=0, description="Comment likes")
    user: InstagramUser = Field(..., description="Comment author")
    strong_id__: str = Field(..., description="Strong ID")

class InstagramHashtagData(BaseModel):
    """Data section from hashtag response"""
    medias: List[InstagramPost] = Field(default=[], description="Posts from hashtag")

class InstagramHashtagResponse(BaseModel):
    """Response from /v1/hashtag_media endpoint"""
    data: InstagramHashtagData = Field(..., description="Response data")
    next_max_id: Optional[str] = Field(None, description="Pagination token")

class InstagramReelClip(BaseModel):
    """Individual reel clip from search reels response"""
    media: InstagramPost = Field(..., description="Reel media content")

class InstagramReelsData(BaseModel):
    """Data section from reels response"""
    clips: List[InstagramReelClip] = Field(default=[], description="Reels from search")

class InstagramReelsResponse(BaseModel):
    """Response from /v2/reels_by_keyword endpoint"""
    data: InstagramReelsData = Field(..., description="Response data")
    pagination_token: Optional[str] = Field(None, description="Pagination token")

class InstagramUserPostsData(BaseModel):
    """Data section from user posts response"""
    items: List[InstagramPost] = Field(default=[], description="Posts from user")
    more_available: bool = Field(default=False, description="More posts available")
    num_results: int = Field(default=0, description="Number of results returned")

class InstagramUserPostsResponse(BaseModel):
    """Response from /v1/user_posts endpoint"""
    data: InstagramUserPostsData = Field(..., description="Response data")
    auto_load_more_enabled: bool = Field(default=False, description="Auto load more enabled")

class InstagramUserReelItem(BaseModel):
    """Individual reel item from user reels response"""
    media: InstagramPost = Field(..., description="Reel media content")

class InstagramUserReelsData(BaseModel):
    """Data section from user reels response"""
    items: List[InstagramUserReelItem] = Field(default=[], description="Reels from user")
    paging_info: Optional[Dict[str, Any]] = Field(None, description="Pagination info")

class InstagramUserReelsResponse(BaseModel):
    """Response from /v1/user_reels endpoint"""
    data: InstagramUserReelsData = Field(..., description="Response data")

class InstagramCommentsData(BaseModel):
    """Data section from comments response"""
    caption: Optional[InstagramComment] = Field(None, description="Post caption as comment")
    comments: List[InstagramComment] = Field(default=[], description="Post comments")
    comment_count: int = Field(default=0, description="Total comment count")
    has_more_comments: bool = Field(default=False, description="More comments available")
    pagination_token: Optional[str] = Field(None, description="Token for next page")

class InstagramCommentsResponse(BaseModel):
    """Response from /v2/media_comments endpoint (INTERNAL USE ONLY)"""
    data: InstagramCommentsData = Field(..., description="Response data")
    status: str = Field(default="ok", description="Response status")
    message: Optional[str] = Field(None, description="Response message")

# ===== API REQUEST/RESPONSE MODELS =====

class InstagramHashtagAnalysisRequest(BaseModel):
    """Request model for Instagram hashtag analysis."""
    
    hashtag: str = Field(
        ...,
        description="Hashtag to analyze (without # symbol)",
        min_length=1,
        max_length=100
    )
    max_posts: int = Field(
        default=20,
        description="Maximum number of posts to analyze",
        ge=1,
        le=50
    )
    max_comments_per_post: int = Field(
        default=50,
        description="Maximum comments per post to analyze",
        ge=10,
        le=100
    )
    region: Optional[str] = Field(
        default=None,
        description="Region filter (e.g., 'US', 'UK')"
    )
    ai_analysis_prompt: str = Field(
        default="Analyze sentiment, themes, and purchase intent",
        description="Custom AI analysis instructions",
        min_length=10,
        max_length=500
    )
    model: str = Field(
        default="gpt-4-turbo-2024-04-09",
        description="OpenAI model to use for analysis"
    )
    max_quote_length: int = Field(
        default=200,
        description="Maximum length for extracted quotes",
        ge=50,
        le=500
    )
    
    @validator('hashtag')
    def validate_hashtag(cls, v):
        # Remove # if present and validate
        clean_hashtag = v.strip().lstrip('#')
        if not clean_hashtag.replace('_', '').isalnum():
            raise ValueError('Hashtag contains invalid characters')
        return clean_hashtag

class InstagramAccountAnalysisRequest(BaseModel):
    """Request model for Instagram account analysis."""
    
    username: str = Field(
        ...,
        description="Instagram username to analyze (without @ symbol)",
        min_length=1,
        max_length=100
    )
    max_posts: int = Field(
        default=20,
        description="Maximum number of posts to analyze",
        ge=1,
        le=50
    )
    max_comments_per_post: int = Field(
        default=50,
        description="Maximum comments per post to analyze", 
        ge=10,
        le=100
    )
    ai_analysis_prompt: str = Field(
        default="Analyze sentiment, themes, and purchase intent",
        description="Custom AI analysis instructions",
        min_length=10,
        max_length=500
    )
    model: str = Field(
        default="gpt-4-turbo-2024-04-09",
        description="OpenAI model to use for analysis"
    )
    max_quote_length: int = Field(
        default=200,
        description="Maximum length for extracted quotes",
        ge=50,
        le=500
    )
    
    @validator('username')
    def validate_username(cls, v):
        # Remove @ if present and validate
        clean_username = v.strip().lstrip('@')
        if not clean_username.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Username contains invalid characters')
        return clean_username

class InstagramSearchPostsAnalysisRequest(BaseModel):
    """Request model for Instagram search posts analysis."""
    
    query: str = Field(
        ...,
        description="Search query for posts",
        min_length=1,
        max_length=200
    )
    max_posts: int = Field(
        default=20,
        description="Maximum number of posts to analyze",
        ge=1,
        le=50
    )
    max_comments_per_post: int = Field(
        default=50,
        description="Maximum comments per post to analyze",
        ge=10,
        le=100
    )
    ai_analysis_prompt: str = Field(
        default="Analyze sentiment, themes, and purchase intent",
        description="Custom AI analysis instructions",
        min_length=10,
        max_length=500
    )
    model: str = Field(
        default="gpt-4-turbo-2024-04-09",
        description="OpenAI model to use for analysis"
    )
    max_quote_length: int = Field(
        default=200,
        description="Maximum length for extracted quotes",
        ge=50,
        le=500
    )
    
    @validator('query')
    def validate_query(cls, v):
        query = v.strip()
        if not query:
            raise ValueError('Search query cannot be empty')
        return query

class InstagramSearchReelsAnalysisRequest(BaseModel):
    """Request model for Instagram search reels analysis."""
    
    query: str = Field(
        ...,
        description="Search query for reels",
        min_length=1,
        max_length=200
    )
    max_posts: int = Field(
        default=20,
        description="Maximum number of reels to analyze",
        ge=1,
        le=50
    )
    max_comments_per_post: int = Field(
        default=50,
        description="Maximum comments per reel to analyze",
        ge=10,
        le=100
    )
    ai_analysis_prompt: str = Field(
        default="Analyze sentiment, themes, and purchase intent",
        description="Custom AI analysis instructions",
        min_length=10,
        max_length=500
    )
    model: str = Field(
        default="gpt-4-turbo-2024-04-09",
        description="OpenAI model to use for analysis"
    )
    max_quote_length: int = Field(
        default=200,
        description="Maximum length for extracted quotes",
        ge=50,
        le=500
    )
    
    @validator('query')
    def validate_query(cls, v):
        query = v.strip()
        if not query:
            raise ValueError('Search query cannot be empty')
        return query

class InstagramUserPostsAnalysisRequest(BaseModel):
    """Request model for Instagram user posts analysis."""
    
    username: str = Field(
        ...,
        description="Instagram username (without @ symbol)",
        min_length=1,
        max_length=100
    )
    max_posts: int = Field(
        default=20,
        description="Maximum number of posts to analyze",
        ge=1,
        le=50
    )
    max_comments_per_post: int = Field(
        default=50,
        description="Maximum comments per post to analyze",
        ge=10,
        le=100
    )
    ai_analysis_prompt: str = Field(
        default="Analyze sentiment, themes, and purchase intent",
        description="Custom AI analysis instructions",
        min_length=10,
        max_length=500
    )
    model: str = Field(
        default="gpt-4-turbo-2024-04-09",
        description="OpenAI model to use for analysis"
    )
    max_quote_length: int = Field(
        default=200,
        description="Maximum length for extracted quotes",
        ge=50,
        le=500
    )
    
    @validator('username')
    def validate_username(cls, v):
        # Remove @ if present and validate
        clean_username = v.strip().lstrip('@')
        if not clean_username.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Username contains invalid characters')
        return clean_username

class InstagramUserReelsAnalysisRequest(BaseModel):
    """Request model for Instagram user reels analysis."""
    
    username: str = Field(
        ...,
        description="Instagram username (without @ symbol)",
        min_length=1,
        max_length=100
    )
    max_posts: int = Field(
        default=20,
        description="Maximum number of reels to analyze",
        ge=1,
        le=50
    )
    max_comments_per_post: int = Field(
        default=50,
        description="Maximum comments per reel to analyze",
        ge=10,
        le=100
    )
    ai_analysis_prompt: str = Field(
        default="Analyze sentiment, themes, and purchase intent",
        description="Custom AI analysis instructions",
        min_length=10,
        max_length=500
    )
    model: str = Field(
        default="gpt-4-turbo-2024-04-09",
        description="OpenAI model to use for analysis"
    )
    max_quote_length: int = Field(
        default=200,
        description="Maximum length for extracted quotes",
        ge=50,
        le=500
    )
    
    @validator('username')
    def validate_username(cls, v):
        # Remove @ if present and validate
        clean_username = v.strip().lstrip('@')
        if not clean_username.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Username contains invalid characters')
        return clean_username

class InstagramSearchAnalysisRequest(BaseModel):
    """Request model for Instagram search analysis."""
    
    query: str = Field(
        ...,
        description="Search query",
        min_length=1,
        max_length=200
    )
    max_posts: int = Field(
        default=20,
        description="Maximum number of posts to analyze",
        ge=1,
        le=50
    )
    max_comments_per_post: int = Field(
        default=50,
        description="Maximum comments per post to analyze",
        ge=10,
        le=100
    )
    region: Optional[str] = Field(
        default=None,
        description="Region filter (e.g., 'US', 'UK')"
    )
    ai_analysis_prompt: str = Field(
        default="Analyze sentiment, themes, and purchase intent",
        description="Custom AI analysis instructions",
        min_length=10,
        max_length=500
    )
    model: str = Field(
        default="gpt-4-turbo-2024-04-09",
        description="OpenAI model to use for analysis"
    )
    max_quote_length: int = Field(
        default=200,
        description="Maximum length for extracted quotes",
        ge=50,
        le=500
    )

class InstagramAnalysisItem(BaseModel):
    """Individual analysis result with source tracking."""
    
    quote: str = Field(..., description="Text that was analyzed (post caption or comment)")
    sentiment: str = Field(..., description="Sentiment classification (positive, negative, neutral)")
    theme: str = Field(..., description="Main theme or topic identified")
    purchase_intent: str = Field(..., description="Purchase intent level (high, medium, low, none)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI analysis confidence score")
    
    # Source identification
    source_type: str = Field(..., description="'post_caption' or 'comment'")
    post_shortcode: str = Field(..., description="Instagram post shortcode")
    post_url: str = Field(..., description="Direct Instagram post URL (https://www.instagram.com/p/{shortcode}/)")
    post_author_username: str = Field(..., description="Post author's username")
    
    # Quote author (different from post author if it's a comment)
    quote_author_username: str = Field(..., description="Username of who wrote the quote")
    quote_author_is_verified: bool = Field(default=False, description="Whether quote author is verified")
    
    # Optional fields based on source type
    comment_id: Optional[str] = Field(None, description="Comment ID if source is comment")
    comment_like_count: Optional[int] = Field(None, description="Comment likes if source is comment")
    
    # Post metadata
    media_type: str = Field(..., description="photo, video, or carousel")
    post_like_count: int = Field(default=0, description="Post likes")
    post_comment_count: int = Field(default=0, description="Post comments")
    post_created_at: int = Field(..., description="Post creation timestamp")
    
    # Additional context
    hashtags_in_caption: List[str] = Field(default=[], description="Hashtags found in post caption")

class InstagramAnalysisMetadata(BaseModel):
    """Analysis metadata and statistics."""
    
    total_posts_analyzed: int
    total_comments_found: int
    relevant_insights_extracted: int
    processing_time_seconds: float
    model_used: str
    
    instagram_api_usage: Dict[str, Any]
    openai_api_usage: Dict[str, Any]
    
    sentiment_distribution: Dict[str, int]
    purchase_intent_distribution: Dict[str, int]
    top_themes: List[Dict[str, Any]]
    
    instagram_specific: Optional[Dict[str, Any]] = None

class InstagramUnifiedAnalysisResponse(BaseModel):
    """Unified response model for all Instagram analysis endpoints."""
    
    comment_analyses: List[InstagramAnalysisItem]
    metadata: InstagramAnalysisMetadata
```

**Deliverable**: Complete data models for all Instagram API requests and responses.

### **Task 2.2: Instagram API Client**
Create the core client for Real-Time Instagram Scraper API.

**Steps for Cursor Agent**:
1. Edit `app/services/instagram_shared/instagram_api_client.py`
2. Copy the TikTok API client structure but adapt for Instagram endpoints
3. Implement these methods with **EXACT** parameters:
   - `get_hashtag_posts(hashtag, feed_type="recent", max_id=None, next_page=None)` → `/v1/hashtag_media`
   - `search_posts(query, pagination_token=None)` → `/v1/posts_by_keyword`
   - `search_reels(query, pagination_token=None)` → `/v2/reels_by_keyword`
   - `get_user_posts(username_or_id, count=None)` → `/v1/user_posts`
   - `get_user_reels(username_or_id)` → `/v1/user_reels`
   - `get_post_comments(code_or_id_or_url, sort_order="popular", pagination_token=None)` → `/v2/media_comments` (INTERNAL)
4. Include rate limiting with 0.5 second delays between requests
5. Add proper error handling for Instagram API responses

**Real API Parameters** (from your actual tests):
```python
# 1. Hashtag endpoint:
url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v1/hashtag_media"
querystring = {
    "hashtag": "tokyo",           # Required: hashtag without #
    "feed_type": "recent",        # Required: "recent" or "top"
    "max_id": None,              # Optional: pagination
    "next_page": None,           # Optional: pagination for top feed
    "nocors": "rapid_do_not_include_in_request_key"  # Optional: CORS bypass
}

# 2. Search Posts endpoint:
url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v1/posts_by_keyword"
querystring = {
    "query": "japan",            # Required: search term
    "pagination_token": None,    # Optional: pagination from previous response
}

# 3. Search Reels endpoint:
url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v2/reels_by_keyword"
querystring = {
    "query": "japan",            # Required: search term
    "pagination_token": None,    # Optional: pagination from previous response
}

# 4. User Posts endpoint:
url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v1/user_posts"
querystring = {
    "username_or_id": "sooyaaa__", # Required: username or user ID
    "count": "12",               # Optional: number of posts (default varies)
}

# 5. User Reels endpoint:
url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v1/user_reels"
querystring = {
    "username_or_id": "sooyaaa__", # Required: username or user ID
}

# 6. Comments endpoint (INTERNAL ONLY - not exposed to users):
url = "https://real-time-instagram-scraper-api1.p.rapidapi.com/v2/media_comments"
querystring = {
    "code_or_id_or_url": "DDPp2UWzWEm", # Required: post shortcode, ID, or URL
    "sort_order": "popular",              # Optional: "popular" or "newest" 
    "pagination_token": None,             # Optional: for loading more comments
}

# Common headers for all endpoints:
headers = {
    "x-rapidapi-key": "YOUR_KEY",
    "x-rapidapi-host": "real-time-instagram-scraper-api1.p.rapidapi.com"
}
```

**Key Implementation Notes**:
- **Hashtag/Search Posts response**: Posts are in `response["data"]["medias"]` array
- **Search Reels response**: Reels are in `response["data"]["clips"]` array, each clip has `media` property
- **User Posts response**: Posts are in `response["data"]["items"]` array
- **User Reels response**: Reels are in `response["data"]["items"]` array, each item has `media` property
- **Comments response**: Comments are in `response["data"]["comments"]` array (INTERNAL ONLY)
- **Post ID format**: Use `post["code"]` (shortcode) for comment collection, not `pk`
- **Media types**: `1=image`, `2=video`, `8=carousel`
- **Carousel handling**: Check `carousel_media` array for multi-image posts
- **Reel-specific fields**: `play_count`, `video_duration`, `video_versions`, `original_sound_info`
- **User posts pagination**: Uses `more_available` boolean and `num_results` count
- **User reels pagination**: Uses `paging_info.max_id` and `more_available`
- **Comments pagination**: Uses `pagination_token` for loading more comments
- **API versions**: Posts use `/v1/`, Search Reels and Comments use `/v2/`, User Reels use `/v1/`
- **High comment usage**: Comments endpoint called once per post (20+ calls per user request)
- Handle 429 rate limit errors with retry logic
- Log all API calls for debugging

**Deliverable**: Complete Instagram API client with all required endpoints.

### **Task 2.3: Comment Collection Service**
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_shared/instagram_comment_collector.py`
2. Create `collect_all_comments(posts, max_comments_per_post)` method
3. For each post, call `api_client.get_post_comments(post.code, sort_order="popular")` using post shortcode
4. Handle pagination if more than max_comments_per_post available
5. Group comments by post_id in returned dictionary
6. Track metadata: total comments, API calls, processing time

**Deliverable**: Service that collects comments for multiple posts efficiently.

### **Task 2.4: Data Cleaning Service**  
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_shared/instagram_data_cleaners.py`
2. Copy TikTok data cleaning logic and adapt for **real Instagram JSON structure**
3. Implement `clean_instagram_posts()` method with actual field paths:

```python
def clean_instagram_posts(raw_posts: List[Dict]) -> List[Dict]:
    """Clean Instagram posts using actual API response structure."""
    cleaned_posts = []
    
    for post in raw_posts:
        cleaned_post = {
            "post_id": post["pk"],                    # Primary key
            "instagram_id": post["id"],               # ID with user suffix
            "shortcode": post["code"],                # Instagram shortcode
            "post_url": f"https://www.instagram.com/p/{post['code']}/",  # Instagram URL
            "media_type": post["media_type"],         # 1=image, 2=video, 8=carousel
            "media_type_name": {1: "photo", 2: "video", 8: "carousel"}.get(post["media_type"], "unknown"),
            "caption": post.get("caption", ""),       # Post caption
            "like_count": post.get("like_count", 0),  # Likes
            "comment_count": post.get("comment_count", 0),  # Comments
            "created_at": post["taken_at"],           # Unix timestamp
            "username": post["user"]["username"],     # Author username
            "user_fullname": post["user"]["full_name"],  # Author name
            "is_verified": post["user"]["is_verified"],  # Verified status
            "accessibility_caption": post.get("accessibility_caption", ""),  # Alt text
            "carousel_media_count": post.get("carousel_media_count", 0),  # Carousel items
            "image_urls": extract_image_urls(post),   # All image URLs
            "hashtags": extract_hashtags_from_caption(post.get("caption", "")),  # Extracted hashtags
        }
        cleaned_posts.append(cleaned_post)
    
    return cleaned_posts

def extract_image_urls(post: Dict) -> List[str]:
    """Extract image URLs from post (handles carousel and single images)."""
    urls = []
    
    # Single image/video post
    if post.get("image_versions2", {}).get("candidates"):
        # Get highest quality image (first in candidates)
        best_image = post["image_versions2"]["candidates"][0]
        urls.append(best_image["url"])
    
    # Carousel post  
    if post.get("carousel_media"):
        for item in post["carousel_media"]:
            if item.get("image_versions2", {}).get("candidates"):
                best_image = item["image_versions2"]["candidates"][0]
                urls.append(best_image["url"])
    
    return urls

def extract_hashtags_from_caption(caption: str) -> List[str]:
    """Extract hashtags from post caption."""
    import re
    if not caption:
        return []
    
    # Find all hashtags (# followed by alphanumeric chars and underscores)
    hashtags = re.findall(r'#([a-zA-Z0-9_]+)', caption)
    return hashtags
```

4. Implement `clean_instagram_comments()` method with actual structure
5. Add Instagram-specific features:
   - Extract hashtags from captions using `post.get("caption", "")`
   - Calculate engagement rates: `(likes + comments) / followers` (if available)
   - Handle Instagram media types: `1=image, 2=video, 8=carousel`
   - Extract carousel media URLs from `carousel_media` array
   - Filter spam comments by checking comment patterns

**Deliverable**: Clean, normalized Instagram data ready for AI analysis.

---

## 📋 **Phase 3: AI Analysis Integration** (Week 5-6)

### **Task 3.1: OpenAI Analysis Service**
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_shared/instagram_ai_analyzer.py`
2. Copy TikTok AI analyzer but adapt prompts for Instagram
3. Create method `analyze_posts_with_comments()`
4. For each post, build comprehensive prompt with:
   - Post caption (if exists)
   - All comments for that post (in 'popular' order, limited by user's max_comments_per_post)
   - Post metadata (media type, engagement, author info)
   - User's custom analysis instructions
5. Call OpenAI with structured JSON output
6. **CRITICAL**: For each analyzed quote, include:
   - Original post URL: `https://www.instagram.com/p/{post.code}/`
   - Whether quote is from post caption or comment
   - Quote author info (post author vs commenter)
   - All metadata needed for `InstagramAnalysisItem` schema

**Key Instagram Prompt Adaptations**:
- Include media type (photo vs video vs carousel)
- Add location information if available
- Include engagement metrics in context
- Adapt examples for Instagram content style

**Sample Analysis Data Flow**:
```json
// Input to AI: Post + Comments
{
  "post": {
    "shortcode": "DDPp2UWzWEm",
    "url": "https://www.instagram.com/p/DDPp2UWzWEm/",
    "caption": "Long time no see Bangkok! Thanks to @Dior made my golden night with shining #DiorGoldHouse ✨💛",
    "author": "sooyaaa__",
    "media_type": "photo",
    "likes": 1247000,
    "comments": 27486
  },
  "comments": [
    {"text": "지수여왕님 생일 축하드립니다", "author": "hosseyni_.msii", "likes": 17},
    {"text": "예뿌댜아아아ㅏ아아아 💗", "author": "hyeri_0609", "likes": 4048}
  ]
}

// Output from AI: Analysis Items
[
  {
    "quote": "Long time no see Bangkok! Thanks to @Dior made my golden night with shining #DiorGoldHouse ✨💛",
    "sentiment": "positive",
    "theme": "luxury brand partnership",
    "purchase_intent": "medium",
    "source_type": "post_caption",
    "post_url": "https://www.instagram.com/p/DDPp2UWzWEm/",
    "quote_author_username": "sooyaaa__"
  },
  {
    "quote": "예뿌댜아아아ㅏ아아아 💗",
    "sentiment": "positive", 
    "theme": "fan appreciation",
    "purchase_intent": "none",
    "source_type": "comment",
    "post_url": "https://www.instagram.com/p/DDPp2UWzWEm/",
    "quote_author_username": "hyeri_0609",
    "comment_like_count": 4048
  }
]
```

**Deliverable**: AI analysis service that provides insights on Instagram content with full source tracking.

### **Task 3.2: Response Builder Service**
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_shared/instagram_response_builder.py`
2. Copy TikTok response builder structure
3. Adapt metadata to include Instagram-specific metrics:
   - Content type breakdown (photo/video/carousel)
   - Location analysis if available
   - Engagement rate statistics
   - Instagram API usage tracking
4. Calculate sentiment and purchase intent distributions
5. Generate top themes analysis

**Deliverable**: Service that builds comprehensive Instagram analysis responses.

---

## 📋 **Phase 4: Service Orchestration & Endpoints** (Week 7-8)

### **Task 4.1: Hashtag Analysis Service**
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_hashtags/hashtag_service.py`
2. Copy TikTok hashtag service structure
3. Implement `analyze_hashtag()` method with 4-stage pipeline:
   - Stage 1: Call `api_client.get_hashtag_posts()`
   - Stage 2: Clean posts with `data_cleaner.clean_instagram_posts()`
   - Stage 3: Collect & clean comments, then AI analysis
   - Stage 4: Build final response
4. Add comprehensive error handling and logging
5. Track processing time and API usage

**Deliverable**: Complete hashtag analysis orchestration service.

### **Task 4.2: Search Posts Analysis Service** 
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_search_posts/search_posts_service.py`
2. Similar to hashtag service but call `api_client.search_posts()`
3. Handle search query optimization
4. Support keyword-based analysis for posts

**Deliverable**: Complete search posts analysis orchestration service.

### **Task 4.3: Search Reels Analysis Service**
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_search_reels/search_reels_service.py`  
2. Similar to hashtag service but call `api_client.search_reels()`
3. Handle reel-specific metadata (video duration, play count, audio info)
4. Support keyword-based analysis for reels

**Deliverable**: Complete search reels analysis orchestration service.

### **Task 4.4: User Posts Analysis Service**
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_user_posts/user_posts_service.py`
2. Similar to hashtag service but call `api_client.get_user_posts()`
3. Add user-specific analysis features
4. Handle private accounts gracefully

**Deliverable**: Complete user posts analysis orchestration service.

### **Task 4.5: User Reels Analysis Service**
**Steps for Cursor Agent**:
1. Edit `app/services/instagram_user_reels/user_reels_service.py`
2. Similar to hashtag service but call `api_client.get_user_reels()`
3. Add reel-specific analysis features (video metrics, audio analysis)
4. Handle private accounts gracefully

**Deliverable**: Complete user reels analysis orchestration service.

### **Task 4.6: FastAPI Endpoints**
**Steps for Cursor Agent**:
1. Edit `app/main.py`
2. Copy TikTok main.py structure 
3. Create five main endpoints:
   - `POST /analyze-instagram-hashtags` → `hashtag_service.analyze_hashtag()`
   - `POST /analyze-instagram-search-posts` → `search_posts_service.analyze_search_posts()`
   - `POST /analyze-instagram-search-reels` → `search_reels_service.analyze_search_reels()`
   - `POST /analyze-instagram-user-posts` → `user_posts_service.analyze_user_posts()`
   - `POST /analyze-instagram-user-reels` → `user_reels_service.analyze_user_reels()`
4. Add authentication, rate limiting, and error handling
5. Include comprehensive API documentation
6. Use correct request models for each endpoint:
   - `InstagramHashtagAnalysisRequest`
   - `InstagramSearchPostsAnalysisRequest`
   - `InstagramSearchReelsAnalysisRequest`
   - `InstagramUserPostsAnalysisRequest`
   - `InstagramUserReelsAnalysisRequest`

**Deliverable**: Complete FastAPI application with all 5 Instagram endpoints.

---

## 🧪 **Testing & Deployment** (Week 8)

### **Task 5.1: Basic Testing**
**Steps for Cursor Agent**:
1. Create test file `tests/test_instagram_endpoints.py`
2. Test each endpoint with sample data
3. Verify error handling
4. Test rate limiting

### **Task 5.2: Environment Setup**
**Steps for Cursor Agent**:
1. Create `.env` file with real API keys
2. Test with actual Instagram scraper API
3. Verify OpenAI integration
4. Test end-to-end analysis

### **Task 5.3: Deployment Preparation**
**Steps for Cursor Agent**:
1. Create `Dockerfile` (copy from TikTok project)
2. Update `README.md` with Instagram-specific instructions
3. Test deployment locally
4. Prepare for Railway deployment

---

## 🔄 **Implementation Strategy for Cursor Agent**

### **Recommended Order**:
1. **Start with Phase 1** - Get basic structure working
2. **Test each component individually** - Don't wait until the end
3. **Use mock data initially** - Test without API calls first  
4. **Gradual integration** - Add real API calls once structure works
5. **Iterative testing** - Test each phase before moving to next

### **Key Success Factors**:
- **Reuse 80% from TikTok API** - Copy working patterns
- **Test incrementally** - Don't build everything then test
- **Start simple** - Basic functionality first, advanced features later
- **Handle errors gracefully** - Instagram API can be unreliable

**This plan gives you narrow, focused tasks perfect for Cursor agent mode. Each task has clear deliverables and can be implemented independently.**

# TikTok Hashtag Analysis API - Comprehensive Implementation Plan

This document provides a detailed, step-by-step implementation plan for building a TikTok Hashtag Analysis API with shared infrastructure. Each phase and step is designed to be implemented independently by Cursor AI agents.

## 🎯 **API Overview**
- **Primary Endpoint**: `/analyze-tiktok-hashtags`
- **Input**: hashtags list, posts per hashtag, ai_analysis_prompt
- **Output**: Structured analysis with sentiment, themes, purchase intent
- **Process**: Collect hashtag posts → Collect comments → Clean data → AI analysis → Return results

---

## 📋 **Phase 1: Project Foundation**

### **Step 1.1: Create Complete Project Structure**
**File**: Create project directory structure

```bash
tiktok-hashtag-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── tiktok_schemas.py
│   ├── services/
│   │   ├── tiktok_shared/
│   │   │   ├── __init__.py
│   │   │   ├── tiktok_api_client.py
│   │   │   ├── tiktok_comment_collector.py
│   │   │   ├── tiktok_data_cleaners.py
│   │   │   ├── tiktok_ai_analyzer.py
│   │   │   └── tiktok_response_builder.py
│   │   ├── tiktok_hashtags/
│   │   │   ├── __init__.py
│   │   │   ├── hashtag_collector.py
│   │   │   └── hashtag_service.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── exceptions.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── tiktok_shared/
│   │   ├── __init__.py
│   │   └── test_integration.py
│   └── tiktok_hashtags/
│       ├── __init__.py
│       └── test_hashtag_endpoint.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── Dockerfile
```

**Success Criteria**: All directories and `__init__.py` files created

---

### **Step 1.2: Setup Dependencies**
**File**: `requirements.txt`

```txt
fastapi[all]==0.116.1
uvicorn[standard]==0.35.0
pydantic>=2.10.0
pydantic-ai==0.7.1
griffe==1.11.1
openai>=1.54.3
httpx==0.28.1
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
asyncio-throttle==1.0.2
```

**Success Criteria**: Dependencies file created with exact versions

---

### **Step 1.3: Core Configuration**
**File**: `app/core/config.py`

```python
import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "TikTok Hashtag Analysis API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered TikTok hashtag conversation analysis"
    
    # TikTok API Configuration (RapidAPI)
    TIKTOK_RAPIDAPI_KEY: str = Field(..., env="TIKTOK_RAPIDAPI_KEY")
    TIKTOK_RAPIDAPI_HOST: str = "tiktok-scrapper-videos-music-challenges-downloader.p.rapidapi.com"
    TIKTOK_BASE_URL: str = "https://tiktok-scrapper-videos-music-challenges-downloader.p.rapidapi.com"
    
    # AI Configuration
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    DEFAULT_MODEL: str = "gpt-4o-mini-2024-07-18"
    MAX_CONCURRENT_AGENTS: int = 3
    
    # Authentication
    SERVICE_API_KEY: str = Field(..., env="SERVICE_API_KEY")
    
    # Processing Limits
    MAX_HASHTAGS_PER_REQUEST: int = 5
    MAX_POSTS_PER_HASHTAG: int = 50
    DEFAULT_POSTS_PER_HASHTAG: int = 20
    MAX_QUOTE_LENGTH: int = 200
    
    # Request Configuration
    REQUEST_TIMEOUT: float = 250.0
    TIKTOK_REQUEST_DELAY: float = 0.1  # 100ms between requests
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Success Criteria**: Configuration class implemented with all TikTok-specific settings

---

### **Step 1.4: Custom Exception Classes**
**File**: `app/core/exceptions.py`

```python
from typing import Optional, Dict, Any

class TikTokAPIException(Exception):
    """Base exception for TikTok API errors."""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }

class ValidationError(TikTokAPIException):
    """Request validation error."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["provided_value"] = value
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(TikTokAPIException):
    """Authentication error."""
    
    def __init__(self, message: str, auth_type: str = None):
        details = {"auth_type": auth_type} if auth_type else {}
        super().__init__(message, status_code=401, details=details)

class ConfigurationError(TikTokAPIException):
    """Server configuration error."""
    
    def __init__(self, message: str, config_key: str = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, status_code=500, details=details)

class TikTokDataCollectionError(TikTokAPIException):
    """TikTok data collection error."""
    
    def __init__(self, message: str, api_endpoint: str = None, http_status: int = None):
        details = {}
        if api_endpoint:
            details["api_endpoint"] = api_endpoint
        if http_status:
            details["http_status"] = http_status
        super().__init__(message, status_code=502, details=details)

class TikTokAnalysisError(TikTokAPIException):
    """AI analysis error."""
    
    def __init__(self, message: str, model: str = None, video_id: str = None):
        details = {}
        if model:
            details["model"] = model
        if video_id:
            details["video_id"] = video_id
        super().__init__(message, status_code=503, details=details)

class RateLimitExceededError(TikTokAPIException):
    """Rate limit exceeded."""
    
    def __init__(self, message: str, service: str = None, retry_after: int = None):
        details = {}
        if service:
            details["service"] = service
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, status_code=429, details=details)

class TimeoutError(TikTokAPIException):
    """Request timeout error."""
    
    def __init__(self, message: str, operation: str = None, timeout_seconds: float = None):
        details = {}
        if operation:
            details["operation"] = operation
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(message, status_code=504, details=details)
```

**Success Criteria**: Complete exception hierarchy implemented for TikTok API

---

### **Step 1.5: Environment Template**
**File**: `.env.example`

```bash
# TikTok API Configuration (RapidAPI)
TIKTOK_RAPIDAPI_KEY=your-rapidapi-tiktok-scraper-key-here

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Service Authentication
SERVICE_API_KEY=your-service-api-key-here

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Optional Overrides
MAX_HASHTAGS_PER_REQUEST=5
MAX_POSTS_PER_HASHTAG=50
REQUEST_TIMEOUT=250.0
```

**Success Criteria**: Environment template created with all required variables

---

## 📊 **Phase 2: TikTok Data Models**

### **Step 2.1: TikTok Request Schema**
**File**: `app/models/tiktok_schemas.py` (Part 1 - Request)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TikTokHashtagAnalysisRequest(BaseModel):
    """Request schema for TikTok hashtag analysis"""
    
    # Hashtag parameters
    hashtags: List[str] = Field(
        ..., 
        min_items=1, 
        max_items=5,
        description="List of hashtags to search (without # symbol)",
        example=["bmwmotorrad", "r12gs", "advrider"]
    )
    number_of_posts_per_hashtag: int = Field(
        default=20, 
        ge=1, 
        le=50,
        description="Number of posts to analyze per hashtag"
    )
    
    # AI Analysis parameters
    ai_analysis_prompt: str = Field(
        ..., 
        min_length=10,
        description="Custom AI analysis criteria for content evaluation",
        example="Analyze motorcycle discussions for sentiment about BMW motorcycles, purchase intent, and user experiences"
    )
    
    # Model configuration
    model: str = Field(
        default="gpt-4o-mini-2024-07-18",
        description="AI model to use for analysis"
    )
    
    # Output configuration
    max_quote_length: int = Field(
        default=200,
        ge=50,
        le=500,
        description="Maximum length of extracted quotes"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "hashtags": ["bmwmotorrad", "motorcyclelife"],
                "number_of_posts_per_hashtag": 25,
                "ai_analysis_prompt": "Analyze motorcycle discussions for sentiment about BMW motorcycles, purchase intent, and user experiences. Focus on comments expressing opinions about BMW bikes, pricing, or buying decisions.",
                "model": "gpt-4o-mini-2024-07-18",
                "max_quote_length": 200
            }
        }
```

**Success Criteria**: TikTok request schema with validation and BMW example

---

### **Step 2.2: TikTok Response Schemas**
**File**: `app/models/tiktok_schemas.py` (Part 2 - Response, append to existing file)

```python
class TikTokCommentAnalysis(BaseModel):
    """Individual TikTok comment analysis result"""
    
    # Core analysis fields
    video_id: str = Field(..., description="TikTok video ID (aweme_id)")
    video_url: Optional[str] = Field(None, description="TikTok video URL")
    quote: str = Field(..., description="Extracted comment text")
    sentiment: str = Field(..., description="positive/negative/neutral")
    theme: str = Field(..., description="Topic category")
    purchase_intent: str = Field(..., description="high/medium/low/none")
    date: str = Field(..., description="Comment date in ISO format")
    source: str = Field(default="tiktok", description="Data source")
    
    # Enhanced context fields
    conversation_context: str = Field(..., description="What this comment responds to")
    thread_context: str = Field(..., description="Broader discussion context")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence level")
    
    # TikTok-specific fields
    hashtag_source: str = Field(..., description="Which hashtag found this content")
    video_play_count: int = Field(default=0, description="Video play count")
    video_like_count: int = Field(default=0, description="Video like count")
    comment_like_count: int = Field(default=0, description="Comment like count")
    
    # Thread structure fields
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID if reply")
    thread_depth: int = Field(default=0, description="Reply depth level")
    is_reply: bool = Field(default=False, description="Whether this is a reply")

class TikTokAnalysisMetadata(BaseModel):
    """TikTok analysis metadata"""
    
    # Standard analysis metadata
    total_videos_analyzed: int = Field(..., description="Number of videos processed")
    total_comments_found: int = Field(..., description="Total comments collected")
    relevant_comments_extracted: int = Field(..., description="Comments matching criteria")
    analysis_timestamp: str = Field(..., description="When analysis completed")
    processing_time_seconds: float = Field(..., description="Total processing time")
    model_used: str = Field(..., description="AI model used")
    
    # TikTok-specific metadata  
    hashtags_analyzed: List[str] = Field(..., description="List of hashtags processed")
    total_video_plays: int = Field(default=0, description="Sum of all video plays")
    total_video_likes: int = Field(default=0, description="Sum of all video likes")
    average_engagement_rate: float = Field(default=0.0, description="Average engagement percentage")
    hashtag_api_calls: int = Field(default=0, description="API calls for hashtag data")
    comments_api_calls: int = Field(default=0, description="API calls for comment data")
    
    # Threading metadata
    max_reply_depth: int = Field(default=0, description="Deepest reply thread found")
    total_threaded_comments: int = Field(default=0, description="Total comments with threading")
    top_level_comments: int = Field(default=0, description="Non-reply comments")
    reply_comments: int = Field(default=0, description="Reply comments")

class TikTokUnifiedAnalysisResponse(BaseModel):
    """Final TikTok analysis response"""
    comment_analyses: List[TikTokCommentAnalysis] = Field(..., description="List of analyzed comments")
    metadata: TikTokAnalysisMetadata = Field(..., description="Analysis metadata")
```

**Success Criteria**: Complete response schemas with TikTok-specific fields

---

### **Step 2.3: Internal TikTok API Schemas**
**File**: `app/models/tiktok_schemas.py` (Part 3 - Internal, append to existing file)

```python
# Internal schemas for TikTok API responses
class TikTokVideoAuthor(BaseModel):
    """TikTok video author information"""
    uid: str
    nickname: str
    unique_id: str
    avatar_thumb: Optional[dict] = None
    region: Optional[str] = None

class TikTokVideoStatistics(BaseModel):
    """TikTok video statistics"""
    digg_count: int = 0  # likes
    comment_count: int = 0
    play_count: int = 0
    share_count: int = 0

class TikTokHashtagInfo(BaseModel):
    """TikTok hashtag information"""
    cha_name: str
    type: int

class TikTokVideo(BaseModel):
    """TikTok video data structure"""
    aweme_id: str
    desc: str  # video caption
    create_time: int  # timestamp
    author: TikTokVideoAuthor
    statistics: TikTokVideoStatistics
    cha_list: List[TikTokHashtagInfo] = []
    share_url: Optional[str] = None
    video: Optional[dict] = None  # video metadata

class TikTokCommentUser(BaseModel):
    """TikTok comment user information"""
    uid: str
    nickname: str
    unique_id: str
    avatar_thumb: Optional[dict] = None

class TikTokComment(BaseModel):
    """TikTok comment data structure"""
    cid: str  # comment ID
    aweme_id: str  # video ID
    create_time: int  # timestamp
    text: str  # comment content
    digg_count: int = 0  # likes
    reply_id: str = "0"  # parent comment ID ("0" = top level)
    reply_to_reply_id: str = "0"
    user: TikTokCommentUser

# Internal processing schemas
class PostWithComments(BaseModel):
    """Internal structure for video with comments (reused from Facebook API)"""
    post_id: str
    post_title: str
    post_content: str
    post_author: str
    post_score: int  # likes
    post_date: str
    subreddit: str  # hashtag name
    permalink: str
    url: str
    comments: List[dict]  # nested comment structure
```

**Success Criteria**: Internal schemas match TikTok API response structure

---

## 🔗 **Phase 3: TikTok API Client**

### **Step 3.1: Core TikTok API Client**
**File**: `app/services/tiktok_shared/tiktok_api_client.py`

```python
import httpx
import asyncio
import time
import logging
from typing import Dict, List, Optional
from app.core.config import settings
from app.core.exceptions import (
    TikTokDataCollectionError, 
    TimeoutError,
    RateLimitExceededError
)

logger = logging.getLogger(__name__)

class TikTokAPIClient:
    """
    HTTP client for RapidAPI TikTok Scraper.
    Handles all TikTok API endpoints with proper error handling and rate limiting.
    """
    
    def __init__(self, rapidapi_key: str):
        self.rapidapi_key = rapidapi_key
        self.base_url = settings.TIKTOK_BASE_URL
        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": settings.TIKTOK_RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }
        self.client = httpx.Client(
            headers=self.headers,
            timeout=httpx.Timeout(settings.REQUEST_TIMEOUT)
        )
        logger.info("TikTok API Client initialized")
    
    def _handle_response(self, response: httpx.Response, endpoint: str) -> Dict:
        """Handle HTTP response with comprehensive error checking."""
        try:
            response.raise_for_status()
            data = response.json()
            
            # Check TikTok API status
            if data.get("status") != "ok":
                error_msg = f"TikTok API error at {endpoint}: {data}"
                logger.error(error_msg)
                raise TikTokDataCollectionError(
                    message=f"TikTok API returned error status",
                    api_endpoint=endpoint,
                    http_status=response.status_code
                )
            
            logger.debug(f"Successful API response from {endpoint}")
            return data
            
        except httpx.TimeoutException:
            logger.error(f"Timeout at {endpoint} after {settings.REQUEST_TIMEOUT}s")
            raise TimeoutError(
                message=f"TikTok API timeout at {endpoint}",
                operation=f"TikTok API call: {endpoint}",
                timeout_seconds=settings.REQUEST_TIMEOUT
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"Rate limit hit at {endpoint}")
                raise RateLimitExceededError(
                    message="TikTok API rate limit exceeded",
                    service="TikTok RapidAPI",
                    retry_after=60
                )
            logger.error(f"HTTP error at {endpoint}: {e.response.status_code}")
            raise TikTokDataCollectionError(
                message=f"TikTok API HTTP error at {endpoint}",
                api_endpoint=endpoint,
                http_status=e.response.status_code
            )
        except Exception as e:
            logger.error(f"Unexpected error at {endpoint}: {e}")
            raise TikTokDataCollectionError(
                message=f"Unexpected error calling TikTok API",
                api_endpoint=endpoint
            )
    
    def challenge_feed_by_keyword(self, keyword: str, count: int = 50, cursor: Optional[str] = None) -> Dict:
        """
        Get posts from hashtag feed using Challenge Feed by Keyword endpoint.
        
        Args:
            keyword: Hashtag to search (without # symbol)
            count: Number of posts to retrieve (max 50)
            cursor: Pagination cursor
            
        Returns:
            TikTok API response with aweme_list
        """
        endpoint = "/hashtag/posts"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "keyword": keyword,
            "count": min(count, 50)  # Respect API limits
        }
        if cursor:
            params["cursor"] = cursor
        
        logger.info(f"Calling Challenge Feed API for keyword: {keyword}, count: {count}")
        
        try:
            response = self.client.get(url, params=params)
            return self._handle_response(response, endpoint)
        except Exception as e:
            logger.error(f"Error in challenge_feed_by_keyword for {keyword}: {e}")
            raise
    
    def get_video_comments(self, aweme_id: str, cursor: Optional[str] = None) -> Dict:
        """
        Get comments for a specific video using Comments by Video ID endpoint.
        
        Args:
            aweme_id: TikTok video ID
            cursor: Pagination cursor
            
        Returns:
            TikTok API response with comments array
        """
        endpoint = "/comments"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "aweme_id": aweme_id
        }
        if cursor:
            params["cursor"] = cursor
        
        logger.info(f"Calling Comments API for video: {aweme_id}")
        
        try:
            response = self.client.get(url, params=params)
            return self._handle_response(response, endpoint)
        except Exception as e:
            logger.error(f"Error in get_video_comments for {aweme_id}: {e}")
            raise
    
    def user_posts(self, username: str, count: int = 50, cursor: Optional[str] = None) -> Dict:
        """
        Get posts from a user account (for future account monitoring endpoint).
        
        Args:
            username: TikTok username
            count: Number of posts to retrieve
            cursor: Pagination cursor
            
        Returns:
            TikTok API response with user posts
        """
        endpoint = "/user/posts"
        url = f"{self.base_url}{endpoint}"
        
        params = {
            "username": username,
            "count": count
        }
        if cursor:
            params["cursor"] = cursor
        
        logger.info(f"Calling User Posts API for: {username}")
        
        try:
            response = self.client.get(url, params=params)
            return self._handle_response(response, endpoint)
        except Exception as e:
            logger.error(f"Error in user_posts for {username}: {e}")
            raise
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
        logger.info("TikTok API Client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

**Success Criteria**: Complete TikTok API client with error handling and all endpoints

---

### **Step 3.2: TikTok Comment Collector**
**File**: `app/services/tiktok_shared/tiktok_comment_collector.py`

```python
import time
import logging
from typing import Dict, List, Optional
from app.services.tiktok_shared.tiktok_api_client import TikTokAPIClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class TikTokCommentCollector:
    """
    Collects and paginates through TikTok video comments.
    Shared component used by all TikTok endpoints.
    """
    
    def __init__(self, api_client: TikTokAPIClient):
        self.api_client = api_client
        self.request_delay = settings.TIKTOK_REQUEST_DELAY
        logger.info("TikTok Comment Collector initialized")
    
    def collect_video_comments(self, aweme_id: str, max_comments: int = 100) -> List[Dict]:
        """
        Collect all comments for a single video with pagination.
        
        Args:
            aweme_id: TikTok video ID
            max_comments: Maximum comments to collect per video
            
        Returns:
            List of comment dictionaries
        """
        logger.info(f"Collecting comments for video {aweme_id}, max: {max_comments}")
        
        all_comments = []
        cursor = None
        calls_made = 0
        
        while len(all_comments) < max_comments:
            try:
                # Rate limiting between calls
                if calls_made > 0:
                    time.sleep(self.request_delay)
                
                response = self.api_client.get_video_comments(aweme_id, cursor)
                calls_made += 1
                
                # Extract comments from response
                comments_data = response.get("data", {})
                comments = comments_data.get("comments", [])
                
                if not comments:
                    logger.info(f"No more comments found for video {aweme_id}")
                    break
                
                # Add comments to collection (respect max limit)
                for comment in comments:
                    if len(all_comments) >= max_comments:
                        break
                    all_comments.append(comment)
                
                # Check pagination
                has_more = comments_data.get("has_more", False)
                cursor = comments_data.get("cursor")
                
                if not has_more or not cursor:
                    logger.info(f"Reached end of comments for video {aweme_id}")
                    break
                
                logger.debug(f"Collected {len(all_comments)} comments so far for video {aweme_id}")
                
            except Exception as e:
                logger.error(f"Error collecting comments for video {aweme_id}: {e}")
                break
        
        logger.info(f"Finished collecting {len(all_comments)} comments for video {aweme_id}")
        return all_comments
    
    def collect_all_comments(self, videos: List[Dict], max_comments_per_video: int = 100) -> Dict:
        """
        Collect comments for multiple videos sequentially.
        
        Args:
            videos: List of TikTok video dictionaries
            max_comments_per_video: Maximum comments per video
            
        Returns:
            Dictionary with comments_by_video mapping and metadata
        """
        logger.info(f"Collecting comments for {len(videos)} videos")
        
        comments_by_video = {}
        total_api_calls = 0
        successful_videos = 0
        
        for i, video in enumerate(videos):
            aweme_id = video.get("aweme_id")
            if not aweme_id:
                logger.warning(f"Video at index {i} missing aweme_id, skipping")
                continue
            
            logger.info(f"Processing video {i+1}/{len(videos)}: {aweme_id}")
            
            try:
                comments = self.collect_video_comments(aweme_id, max_comments_per_video)
                comments_by_video[aweme_id] = comments
                successful_videos += 1
                
                # Estimate API calls (rough approximation based on pagination)
                estimated_calls = max(1, len(comments) // 50)  # ~50 comments per call
                total_api_calls += estimated_calls
                
            except Exception as e:
                logger.error(f"Failed to collect comments for video {aweme_id}: {e}")
                comments_by_video[aweme_id] = []
        
        total_comments = sum(len(comments) for comments in comments_by_video.values())
        
        logger.info(f"Comment collection complete: {total_comments} total comments from {successful_videos}/{len(videos)} videos")
        
        return {
            "comments_by_video": comments_by_video,
            "metadata": {
                "videos_processed": len(videos),
                "successful_videos": successful_videos,
                "total_comments_collected": total_comments,
                "comments_api_calls": total_api_calls
            }
        }
```

**Success Criteria**: Comment collector with pagination and batch processing

---

## 🧹 **Phase 4: Data Cleaning & Transformation**

### **Step 4.1: TikTok Data Cleaners**
**File**: `app/services/tiktok_shared/tiktok_data_cleaners.py`

```python
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.models.tiktok_schemas import PostWithComments

logger = logging.getLogger(__name__)

def clean_tiktok_video(raw_video: Dict) -> Dict:
    """
    Transform TikTok video data to standardized post format.
    
    Maps TikTok structure to Facebook-compatible format:
    - aweme_id → post_id
    - desc → post_content/post_title  
    - author.nickname → post_author
    - statistics.digg_count → post_score
    - create_time → post_date
    
    Args:
        raw_video: Raw TikTok video data from API
        
    Returns:
        Cleaned video dictionary
    """
    try:
        # Extract basic video information
        aweme_id = raw_video.get("aweme_id", "")
        desc = raw_video.get("desc", "")
        create_time = raw_video.get("create_time", 0)
        
        # Extract author information
        author = raw_video.get("author", {})
        author_name = author.get("nickname", author.get("unique_id", "Unknown"))
        
        # Extract engagement statistics
        stats = raw_video.get("statistics", {})
        digg_count = stats.get("digg_count", 0)
        play_count = stats.get("play_count", 0)
        comment_count = stats.get("comment_count", 0)
        share_count = stats.get("share_count", 0)
        
        # Extract hashtags
        cha_list = raw_video.get("cha_list", [])
        hashtags = [tag.get("cha_name", "") for tag in cha_list if tag.get("cha_name")]
        
        # Generate post title from description
        post_title = desc.split('\n')[0] if desc else f"TikTok Video {aweme_id}"
        if len(post_title) > 80:
            post_title = post_title[:77] + "..."
        
        # Convert timestamp to datetime
        try:
            post_date = datetime.fromtimestamp(create_time).isoformat() + "Z"
        except (ValueError, OSError):
            post_date = datetime.now().isoformat() + "Z"
            logger.warning(f"Invalid timestamp {create_time} for video {aweme_id}")
        
        # Generate URLs
        share_url = raw_video.get("share_url", f"https://tiktok.com/video/{aweme_id}")
        
        # Extract video metadata
        video_info = raw_video.get("video", {})
        duration_ms = video_info.get("duration", 0)
        video_duration = duration_ms / 1000 if duration_ms else 0  # Convert to seconds
        
        cleaned_video = {
            # Standard post fields (compatible with Facebook API format)
            "post_id": aweme_id,
            "post_title": post_title,
            "post_content": desc,
            "post_author": author_name,
            "post_score": digg_count,  # likes
            "post_date": post_date,
            "subreddit": "tiktok",  # Will be overridden with hashtag
            "permalink": share_url,
            "url": share_url,
            
            # TikTok-specific fields
            "play_count": play_count,
            "comment_count": comment_count,
            "share_count": share_count,
            "hashtags": hashtags,
            "video_duration": video_duration,
            "author_uid": author.get("uid", ""),
            "author_unique_id": author.get("unique_id", "")
        }
        
        logger.debug(f"Cleaned video {aweme_id}: {post_title[:50]}...")
        return cleaned_video
        
    except Exception as e:
        logger.error(f"Error cleaning TikTok video {raw_video.get('aweme_id', 'unknown')}: {e}")
        # Return minimal structure to prevent pipeline failure
        return {
            "post_id": raw_video.get("aweme_id", "error"),
            "post_title": "Error Processing Video",
            "post_content": "",
            "post_author": "Unknown",
            "post_score": 0,
            "post_date": datetime.now().isoformat() + "Z",
            "subreddit": "tiktok",
            "permalink": "",
            "url": "",
            "play_count": 0,
            "comment_count": 0,
            "share_count": 0,
            "hashtags": [],
            "video_duration": 0
        }

def clean_tiktok_comments(raw_comments: List[Dict]) -> List[Dict]:
    """
    Transform TikTok comments and build nested thread structure.
    
    TikTok uses reply_id system:
    - reply_id = "0" means top-level comment  
    - reply_id = comment_id means reply to that comment
    
    Args:
        raw_comments: List of raw TikTok comments from API
        
    Returns:
        List of cleaned comments with nested structure
    """
    if not raw_comments:
        return []
    
    logger.info(f"Cleaning {len(raw_comments)} TikTok comments")
    
    cleaned_comments = []
    comment_map = {}  # For building thread structure
    
    # First pass: clean individual comments
    for raw_comment in raw_comments:
        try:
            cleaned_comment = clean_single_tiktok_comment(raw_comment)
            if cleaned_comment:
                cleaned_comments.append(cleaned_comment)
                comment_map[cleaned_comment["id"]] = cleaned_comment
        except Exception as e:
            logger.error(f"Error cleaning comment {raw_comment.get('cid', 'unknown')}: {e}")
            continue
    
    # Second pass: build thread structure
    nested_comments = build_tiktok_nested_structure(cleaned_comments, comment_map)
    
    logger.info(f"Processed {len(nested_comments)} top-level comments with threading")
    return nested_comments

def clean_single_tiktok_comment(raw_comment: Dict) -> Optional[Dict]:
    """
    Clean individual TikTok comment.
    
    Args:
        raw_comment: Raw comment data from TikTok API
        
    Returns:
        Cleaned comment dictionary or None if invalid
    """
    try:
        cid = raw_comment.get("cid", "")
        text = raw_comment.get("text", "")
        create_time = raw_comment.get("create_time", 0)
        digg_count = raw_comment.get("digg_count", 0)
        reply_id = raw_comment.get("reply_id", "0")
        
        # Skip empty comments
        if not text.strip():
            return None
        
        # Extract user information
        user = raw_comment.get("user", {})
        author = user.get("nickname", user.get("unique_id", "Unknown"))
        
        # Convert timestamp
        try:
            comment_date = datetime.fromtimestamp(create_time).isoformat() + "Z"
        except (ValueError, OSError):
            comment_date = datetime.now().isoformat() + "Z"
        
        return {
            # Standard comment fields (compatible with Facebook API)
            "id": cid,
            "author": author,
            "body": text,
            "score": digg_count,
            "date": comment_date,
            "depth": 0,  # Will be calculated in threading
            "replies_count": 0,  # Will be calculated in threading
            "children": [],
            
            # TikTok-specific fields
            "reply_id": reply_id,
            "reply_to_reply_id": raw_comment.get("reply_to_reply_id", "0"),
            "author_uid": user.get("uid", ""),
            
            # Thread structure placeholders (populated during nesting)
            "parent_comment_id": None,
            "thread_position": 0,
            "children_count": 0,
            "conversation_quality": None
        }
        
    except Exception as e:
        logger.error(f"Error processing single comment: {e}")
        return None

def build_tiktok_nested_structure(comments: List[Dict], comment_map: Dict[str, Dict]) -> List[Dict]:
    """
    Build nested comment structure from TikTok's reply_id system.
    
    TikTok threading logic:
    - reply_id = "0": top-level comment (depth = 0)
    - reply_id = comment_id: reply to that comment (depth = parent_depth + 1)
    
    Args:
        comments: List of cleaned comments
        comment_map: Dictionary mapping comment_id to comment object
        
    Returns:
        List of top-level comments with nested children
    """
    logger.info(f"Building nested structure for {len(comments)} comments")
    
    top_level_comments = []
    
    # Process each comment to determine its place in the hierarchy
    for comment in comments:
        reply_id = comment.get("reply_id", "0")
        
        if reply_id == "0":
            # Top-level comment
            comment["depth"] = 0
            comment["parent_comment_id"] = None
            top_level_comments.append(comment)
        else:
            # Reply to another comment
            parent = comment_map.get(reply_id)
            if parent:
                comment["depth"] = parent.get("depth", 0) + 1
                comment["parent_comment_id"] = reply_id
                
                # Add to parent's children
                if "children" not in parent:
                    parent["children"] = []
                parent["children"].append(comment)
            else:
                # Orphaned reply - treat as top-level
                logger.warning(f"Orphaned reply {comment['id']} with reply_id {reply_id}")
                comment["depth"] = 0
                comment["parent_comment_id"] = None
                top_level_comments.append(comment)
    
    # Calculate additional thread metrics for all comments
    for comment in comments:
        comment["children_count"] = len(comment.get("children", []))
        comment["conversation_quality"] = _assess_tiktok_conversation_quality(comment)
    
    return top_level_comments

def _assess_tiktok_conversation_quality(comment: Dict) -> str:
    """
    Assess conversation quality for TikTok comments based on engagement.
    
    Scoring factors:
    - Likes on the comment
    - Number of replies
    - Content length
    - Thread depth
    
    Args:
        comment: Comment dictionary
        
    Returns:
        Quality level: "high", "medium", "low", or "none"
    """
    score = 0
    
    # Engagement scoring (TikTok likes)
    likes = comment.get("score", 0)
    if likes >= 50:
        score += 3
    elif likes >= 20:
        score += 2
    elif likes >= 5:
        score += 1
    
    # Thread engagement (replies)
    replies = comment.get("children_count", 0)
    if replies >= 5:
        score += 3
    elif replies >= 2:
        score += 2
    elif replies >= 1:
        score += 1
    
    # Content length (longer comments often more substantive)
    content_length = len(comment.get("body", ""))
    if content_length >= 200:
        score += 2
    elif content_length >= 100:
        score += 1
    
    # Thread depth (deeper discussions)
    depth = comment.get("depth", 0)
    if depth >= 3:
        score += 2
    elif depth >= 2:
        score += 1
    
    # Return quality categories
    if score >= 7:
        return "high"
    elif score >= 4:
        return "medium"
    elif score >= 1:
        return "low"
    else:
        return "none"

def assemble_videos_with_comments(
    videos_by_hashtag: Dict[str, List[Dict]], 
    comments_by_video: Dict[str, List[Dict]], 
    hashtags: List[str]
) -> List[PostWithComments]:
    """
    Assemble TikTok videos with their comments into PostWithComments objects.
    
    Args:
        videos_by_hashtag: Dict mapping hashtag to list of videos
        comments_by_video: Dict mapping aweme_id to list of comments  
        hashtags: List of hashtags being analyzed
        
    Returns:
        List of PostWithComments objects ready for AI analysis
    """
    logger.info("Assembling videos with comments into PostWithComments objects")
    
    posts_with_comments = []
    total_videos = 0
    successful_assemblies = 0
    
    for hashtag, videos in videos_by_hashtag.items():
        logger.info(f"Processing {len(videos)} videos for hashtag: #{hashtag}")
        total_videos += len(videos)
        
        for video in videos:
            try:
                # Clean video data
                clean_video = clean_tiktok_video(video)
                clean_video["subreddit"] = hashtag  # Set hashtag as "subreddit"
                
                # Get and clean comments for this video
                aweme_id = clean_video["post_id"]
                raw_comments = comments_by_video.get(aweme_id, [])
                clean_comments = clean_tiktok_comments(raw_comments) if raw_comments else []
                
                # Create PostWithComments object
                post_with_comments = PostWithComments(
                    post_id=clean_video["post_id"],
                    post_title=clean_video["post_title"],
                    post_content=clean_video["post_content"],
                    post_author=clean_video["post_author"],
                    post_score=clean_video["post_score"],
                    post_date=clean_video["post_date"],
                    subreddit=clean_video["subreddit"],
                    permalink=clean_video["permalink"],
                    url=clean_video["url"],
                    comments=clean_comments
                )
                
                posts_with_comments.append(post_with_comments)
                successful_assemblies += 1
                
            except Exception as e:
                logger.error(f"Error assembling video {video.get('aweme_id', 'unknown')}: {e}")
                continue
    
    logger.info(f"Assembly complete: {successful_assemblies}/{total_videos} videos successfully processed")
    return posts_with_comments
```

**Success Criteria**: Complete data cleaning pipeline that transforms TikTok structure to standardized format

---

## 🤖 **Phase 5: AI Analysis Integration**

### **Step 5.1: TikTok AI Analysis Agent**
**File**: `app/services/tiktok_shared/tiktok_ai_analyzer.py` (Part 1)

```python
import asyncio
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.models.tiktok_schemas import TikTokCommentAnalysis, PostWithComments
from app.core.config import settings

logger = logging.getLogger(__name__)

class TikTokCommentFilteringAgent:
    """
    AI agent for analyzing TikTok comments with platform-specific context.
    Uses OpenAI via Pydantic AI for structured comment analysis.
    """
    
    def __init__(self, user_analysis_prompt: str, max_quote_length: int = 200):
        self.user_analysis_prompt = user_analysis_prompt
        self.max_quote_length = max_quote_length
        
        # Initialize Pydantic AI agent with OpenAI
        model = OpenAIModel(settings.DEFAULT_MODEL)
        self.agent = Agent(
            model=model,
            result_type=List[TikTokCommentAnalysis],
            system_prompt=self._build_system_prompt()
        )
        
        logger.info(f"TikTok AI agent initialized with model: {settings.DEFAULT_MODEL}")
    
    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt for TikTok comment analysis."""
        return f"""
You are an expert social media analyst specializing in TikTok content analysis.

USER ANALYSIS CRITERIA:
{self.user_analysis_prompt}

TIKTOK PLATFORM CONTEXT:
- Short-form video content (15-60 seconds typically)
- Casual, emoji-rich communication style with abbreviations and slang
- Visual and audio elements heavily influence comment context
- Hashtag-driven discovery and viral trend participation
- Younger demographic (Gen Z/Millennial) with unique language patterns
- Comments often reference video content, music, effects, or trends
- High engagement through video plays, likes, shares, and comments
- Comment threading via reply system (less deep than Reddit/Facebook)
- Fast-paced content consumption and reaction patterns

ANALYSIS INSTRUCTIONS:
Analyze the provided TikTok video and its comments. Extract ONLY comments that are relevant to the user's analysis criteria and provide meaningful insights.

For each relevant comment, extract:

1. **quote**: The comment text (max {self.max_quote_length} characters)
2. **sentiment**: positive/negative/neutral based on tone and context
3. **theme**: Main topic category (e.g., "experience", "price", "comparison", "recommendation", "performance")  
4. **purchase_intent**: high/medium/low/none based on buying signals and interest level
5. **conversation_context**: Brief description of what this comment responds to (video content, other comments)
6. **thread_context**: Broader context of the discussion thread and conversation flow
7. **confidence_score**: Your confidence in this analysis (0.0 to 1.0)

TIKTOK-SPECIFIC ANALYSIS GUIDELINES:
- Pay attention to emoji usage, abbreviations, and Gen Z slang
- Consider references to video content, music, visual effects, or TikTok trends
- Account for TikTok's informal communication style and quick reactions
- Recognize hashtag usage patterns and viral trend participation
- Factor in the visual/audio nature of TikTok when interpreting comment context
- Understand generational language differences and cultural references

FILTERING CRITERIA:
- Skip generic engagement comments ("first!", "💚", "follow me", "fire")
- Skip spam, promotional, or completely off-topic comments
- Skip pure emoji reactions without substantive content
- Focus on comments that provide genuine opinions, experiences, or insights
- Prioritize comments with authentic purchase intent or brand discussion
- Include comments showing real user experiences, recommendations, or comparisons
- Value comments that demonstrate product knowledge or specific interest

QUALITY INDICATORS:
- Specific product mentions or model references
- Personal experience sharing ("I have...", "I bought...")
- Detailed questions about features, pricing, or availability
- Comparisons between brands or products
- Recommendations to others with reasoning
- Technical discussions or specifications

OUTPUT REQUIREMENTS:
Return a list of TikTokCommentAnalysis objects for relevant comments only.
If no relevant comments meet the criteria, return an empty list.
Ensure all fields are properly populated with meaningful values.
"""
    
    async def analyze_video_comments(self, video_data: Dict) -> List[TikTokCommentAnalysis]:
        """
        Analyze comments for a single TikTok video using AI.
        
        Args:
            video_data: Dictionary containing video and comment data
            
        Returns:
            List of TikTokCommentAnalysis objects
        """
        try:
            # Build comprehensive analysis prompt
            analysis_prompt = self._build_analysis_prompt(video_data)
            
            # Set OpenAI API key temporarily (pydantic-ai requirement)
            original_key = os.environ.get("OPENAI_API_KEY")
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            
            try:
                # Run AI analysis
                logger.info(f"Running AI analysis for video {video_data.get('post_id', 'unknown')}")
                result = await self.agent.run(analysis_prompt)
                
                # Handle different pydantic-ai response formats
                if hasattr(result, 'data'):
                    analyses = result.data
                else:
                    analyses = result
                
                # Ensure we have a list
                if not isinstance(analyses, list):
                    analyses = []
                
                # Post-process results
                processed_analyses = []
                for analysis in analyses:
                    if isinstance(analysis, dict):
                        # Convert dict to TikTokCommentAnalysis
                        analysis = TikTokCommentAnalysis(**analysis)
                    
                    # Populate TikTok-specific fields from video data
                    analysis = self._populate_tiktok_fields(analysis, video_data)
                    
                    # Populate thread fields by matching quotes to original comments
                    analysis = self._populate_thread_fields(analysis, video_data)
                    
                    # Truncate quote if needed
                    if len(analysis.quote) > self.max_quote_length:
                        analysis.quote = analysis.quote[:self.max_quote_length-3] + "..."
                    
                    processed_analyses.append(analysis)
                
                logger.info(f"AI extracted {len(processed_analyses)} relevant comments from video {video_data.get('post_id', 'unknown')}")
                return processed_analyses
                
            finally:
                # Restore original API key
                if original_key:
                    os.environ["OPENAI_API_KEY"] = original_key
                else:
                    os.environ.pop("OPENAI_API_KEY", None)
        
        except Exception as e:
            logger.error(f"Error in AI analysis for video {video_data.get('post_id', 'unknown')}: {e}")
            return []
    
    def _build_analysis_prompt(self, video_data: Dict) -> str:
        """
        Build detailed analysis prompt with TikTok video and comment context.
        
        Args:
            video_data: Video data dictionary
            
        Returns:
            Formatted prompt string for AI analysis
        """
        # Extract video information
        post_info = f"""
TIKTOK VIDEO INFORMATION:
- Video ID: {video_data.get('post_id', 'Unknown')}
- Caption/Title: {video_data.get('post_title', 'No title')}  
- Content: {video_data.get('post_content', 'No content')}
- Author: {video_data.get('post_author', 'Unknown')}
- Likes: {video_data.get('post_score', 0):,}
- Plays: {video_data.get('play_count', 0):,}
- Shares: {video_data.get('share_count', 0):,}
- Comments: {video_data.get('comment_count', 0):,}
- Hashtags: {', '.join(video_data.get('hashtags', []))}
- Duration: {video_data.get('video_duration', 0)} seconds
- Source Hashtag: #{video_data.get('subreddit', 'unknown')}
"""
        
        # Format comments for AI analysis with TikTok context
        comments_text = self._format_comments_for_ai(video_data.get('comments', []))
        
        return f"""
{post_info}

COMMENTS TO ANALYZE:
{comments_text}

Please analyze these TikTok comments according to the criteria provided in the system prompt.
Focus on extracting comments that are relevant to the user's analysis criteria and provide genuine insights about the topics of interest.
"""
    
    def _format_comments_for_ai(self, comments: List[Dict], max_comments: int = 50) -> str:
        """
        Format comments for AI analysis with TikTok thread context.
        
        Args:
            comments: List of comment dictionaries
            max_comments: Maximum comments to include
            
        Returns:
            Formatted comments string for AI prompt
        """
        if not comments:
            return "No comments found for this video."
        
        # Limit comments to avoid token limits
        comments_to_analyze = comments[:max_comments]
        formatted_comments = []
        
        for i, comment in enumerate(comments_to_analyze, 1):
            # Add thread depth indicators
            depth = comment.get("depth", 0)
            thread_indicator = "  " * depth + ("↳ " if depth > 0 else "")
            
            # Format comment with TikTok-specific context
            comment_text = f"""
Comment {i}: {thread_indicator}
Author: @{comment.get('author', 'Unknown')}
Text: {comment.get('body', '')}
Likes: {comment.get('score', 0)}
Thread Depth: {depth}
Reply to: {comment.get('parent_comment_id', 'None (top-level)')}
Quality: {comment.get('conversation_quality', 'unknown')}
"""
            formatted_comments.append(comment_text.strip())
        
        if len(comments) > max_comments:
            formatted_comments.append(f"\n... and {len(comments) - max_comments} more comments not shown")
        
        return "\n\n".join(formatted_comments)
    
    def _populate_tiktok_fields(self, analysis: TikTokCommentAnalysis, video_data: Dict) -> TikTokCommentAnalysis:
        """
        Populate TikTok-specific fields in the analysis object.
        
        Args:
            analysis: TikTokCommentAnalysis object
            video_data: Video data dictionary
            
        Returns:
            Updated analysis object
        """
        # Set video-level information
        analysis.video_id = video_data.get('post_id', '')
        analysis.video_url = video_data.get('url', '')
        analysis.hashtag_source = video_data.get('subreddit', '')
        analysis.video_play_count = video_data.get('play_count', 0)
        analysis.video_like_count = video_data.get('post_score', 0)
        
        return analysis
    
    def _populate_thread_fields(self, analysis: TikTokCommentAnalysis, video_data: Dict) -> TikTokCommentAnalysis:
        """
        Match analysis quote back to original comment for thread information.
        
        Args:
            analysis: TikTokCommentAnalysis object
            video_data: Video data dictionary
            
        Returns:
            Updated analysis object with thread fields
        """
        comments = video_data.get('comments', [])
        
        # Find matching comment by quote similarity
        best_match = self._find_matching_comment(analysis.quote, comments)
        
        if best_match:
            # Populate thread fields from original comment
            analysis.parent_comment_id = best_match.get('parent_comment_id')
            analysis.thread_depth = best_match.get('depth', 0) 
            analysis.is_reply = best_match.get('depth', 0) > 0
            analysis.comment_like_count = best_match.get('score', 0)
        
        return analysis
    
    def _find_matching_comment(self, quote: str, comments: List[Dict]) -> Optional[Dict]:
        """
        Find original comment that matches the AI-extracted quote.
        
        Args:
            quote: AI-extracted quote text
            comments: List of original comment dictionaries
            
        Returns:
            Matching comment dictionary or None
        """
        quote_lower = quote.lower().strip()
        best_match = None
        best_similarity = 0
        
        def get_all_comments(comment_list):
            """Recursively get all comments including nested ones."""
            all_comments = []
            for comment in comment_list:
                all_comments.append(comment)
                if comment.get('children'):
                    all_comments.extend(get_all_comments(comment['children']))
            return all_comments
        
        all_comments = get_all_comments(comments)
        
        for comment in all_comments:
            comment_text = comment.get('body', '').lower().strip()
            if not comment_text:
                continue
            
            # Simple similarity check - could be enhanced with fuzzy matching
            if quote_lower in comment_text or comment_text in quote_lower:
                # Calculate rough similarity score
                similarity = min(len(quote_lower), len(comment_text)) / max(len(quote_lower), len(comment_text), 1)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = comment
        
        return best_match if best_similarity > 0.3 else None  # 30% similarity threshold
```

**Success Criteria**: TikTok AI analysis agent with platform-specific prompting

---

### **Step 5.2: TikTok Analysis Orchestrator**
**File**: `app/services/tiktok_shared/tiktok_ai_analyzer.py` (Part 2 - append to existing file)

```python
class TikTokAnalysisOrchestrator:
    """
    Orchestrates AI analysis across multiple TikTok videos with concurrency control.
    Manages rate limiting and error handling for batch analysis operations.
    """
    
    def __init__(self, openai_key: str, max_concurrent: int = 3):
        self.openai_key = openai_key
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        logger.info(f"TikTok Analysis Orchestrator initialized with max_concurrent: {max_concurrent}")
    
    async def analyze_all_videos(
        self, 
        posts_with_comments: List[PostWithComments], 
        user_prompt: str,
        max_quote_length: int = 200
    ) -> List[List[TikTokCommentAnalysis]]:
        """
        Analyze comments for all videos concurrently with rate limiting.
        
        Args:
            posts_with_comments: List of PostWithComments objects
            user_prompt: User's analysis criteria
            max_quote_length: Maximum quote length for extractions
            
        Returns:
            List of analysis results, one list per video
        """
        logger.info(f"Starting AI analysis for {len(posts_with_comments)} videos")
        
        # Create analysis tasks with concurrency control
        tasks = []
        for post in posts_with_comments:
            task = self._analyze_single_video(post, user_prompt, max_quote_length)
            tasks.append(task)
        
        # Execute with controlled concurrency
        start_time = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.now()
        
        # Process results and handle exceptions
        processed_results = []
        successful_analyses = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"AI analysis failed for video {i}: {result}")
                processed_results.append([])  # Empty list for failed analysis
            else:
                processed_results.append(result)
                successful_analyses += 1
        
        processing_time = (end_time - start_time).total_seconds()
        total_analyses = sum(len(analyses) for analyses in processed_results)
        
        logger.info(f"AI analysis completed: {total_analyses} relevant comments extracted from {successful_analyses}/{len(posts_with_comments)} videos in {processing_time:.1f}s")
        
        return processed_results
    
    async def _analyze_single_video(
        self, 
        post: PostWithComments, 
        user_prompt: str, 
        max_quote_length: int
    ) -> List[TikTokCommentAnalysis]:
        """
        Analyze single video with semaphore control for rate limiting.
        
        Args:
            post: PostWithComments object
            user_prompt: User's analysis criteria
            max_quote_length: Maximum quote length
            
        Returns:
            List of TikTokCommentAnalysis objects for this video
        """
        async with self.semaphore:
            try:
                # Create AI agent for this analysis
                agent = TikTokCommentFilteringAgent(user_prompt, max_quote_length)
                
                # Convert PostWithComments to dictionary for analysis
                video_data = {
                    "post_id": post.post_id,
                    "post_title": post.post_title,
                    "post_content": post.post_content,
                    "post_author": post.post_author,
                    "post_score": post.post_score,
                    "post_date": post.post_date,
                    "subreddit": post.subreddit,  # hashtag
                    "url": post.url,
                    "comments": [comment.dict() if hasattr(comment, 'dict') else comment for comment in post.comments],
                    
                    # TikTok-specific fields (extract from post if available)
                    "play_count": getattr(post, 'play_count', 0),
                    "share_count": getattr(post, 'share_count', 0),
                    "comment_count": getattr(post, 'comment_count', 0),
                    "hashtags": getattr(post, 'hashtags', []),
                    "video_duration": getattr(post, 'video_duration', 0)
                }
                
                # Perform AI analysis
                return await agent.analyze_video_comments(video_data)
                
            except Exception as e:
                logger.error(f"Error analyzing video {post.post_id}: {e}")
                return []

class TikTokResultsProcessor:
    """
    Processes and combines TikTok analysis results into final response format.
    Calculates comprehensive metadata and assembles unified response.
    """
    
    def combine_analysis_results(
        self,
        analysis_results: List[List[TikTokCommentAnalysis]],
        collection_metadata: Dict,
        posts_with_comments: List[PostWithComments],
        processing_time: float,
        model_used: str
    ) -> Dict:
        """
        Combine individual video analysis results into unified response.
        
        Args:
            analysis_results: List of analysis results per video
            collection_metadata: Metadata from data collection phase
            posts_with_comments: Original posts with comments
            processing_time: Total processing time in seconds
            model_used: AI model identifier
            
        Returns:
            Dictionary with combined results and comprehensive metadata
        """
        logger.info("Combining TikTok analysis results into unified response")
        
        # Flatten all analyses into single list
        all_analyses = []
        for video_analyses in analysis_results:
            all_analyses.extend(video_analyses)
        
        # Calculate comprehensive metadata
        metadata = self._calculate_comprehensive_metadata(
            all_analyses,
            collection_metadata,
            posts_with_comments,
            processing_time,
            model_used
        )
        
        logger.info(f"Combined {len(all_analyses)} total analyses with comprehensive metadata")
        
        return {
            "comment_analyses": all_analyses,
            "metadata": metadata
        }
    
    def _calculate_comprehensive_metadata(
        self,
        analyses: List[TikTokCommentAnalysis],
        collection_metadata: Dict,
        posts_with_comments: List[PostWithComments],
        processing_time: float,
        model_used: str
    ) -> Dict:
        """
        Calculate comprehensive metadata for TikTok analysis response.
        
        Args:
            analyses: List of all comment analyses
            collection_metadata: Collection phase metadata
            posts_with_comments: Original posts with comments
            processing_time: Total processing time
            model_used: AI model used
            
        Returns:
            Comprehensive metadata dictionary
        """
        # Basic analysis counts
        total_comments = sum(len(post.comments) for post in posts_with_comments)
        
        # Video engagement totals
        total_plays = 0
        total_likes = 0
        
        for post in posts_with_comments:
            total_plays += getattr(post, 'play_count', 0)
            total_likes += post.post_score
        
        # Calculate average engagement rate
        avg_engagement_rate = 0.0
        if total_plays > 0:
            avg_engagement_rate = (total_likes / total_plays) * 100
        
        # Thread analysis
        max_depth = 0
        reply_comments = 0
        top_level_comments = 0
        
        for post in posts_with_comments:
            for comment in post.comments:
                depth = comment.get('depth', 0) if isinstance(comment, dict) else getattr(comment, 'depth', 0)
                max_depth = max(max_depth, depth)
                if depth > 0:
                    reply_comments += 1
                else:
                    top_level_comments += 1
        
        # Extract unique hashtags analyzed
        hashtags_analyzed = []
        for post in posts_with_comments:
            hashtag = post.subreddit
            if hashtag and hashtag != "tiktok" and hashtag not in hashtags_analyzed:
                hashtags_analyzed.append(hashtag)
        
        # AI quality metrics
        confidence_scores = [a.confidence_score for a in analyses if hasattr(a, 'confidence_score')]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        high_confidence_count = sum(1 for score in confidence_scores if score >= 0.8)
        
        return {
            # Standard analysis metadata
            "total_videos_analyzed": len(posts_with_comments),
            "total_comments_found": total_comments,
            "relevant_comments_extracted": len(analyses),
            "analysis_timestamp": datetime.now().isoformat() + "Z",
            "processing_time_seconds": round(processing_time, 2),
            "model_used": model_used,
            
            # TikTok-specific metadata
            "hashtags_analyzed": hashtags_analyzed,
            "total_video_plays": total_plays,
            "total_video_likes": total_likes,
            "average_engagement_rate": round(avg_engagement_rate, 2),
            "hashtag_api_calls": collection_metadata.get("hashtag_api_calls", 0),
            "comments_api_calls": collection_metadata.get("comments_api_calls", 0),
            
            # Threading metadata
            "max_reply_depth": max_depth,
            "total_threaded_comments": total_comments,
            "top_level_comments": top_level_comments,
            "reply_comments": reply_comments,
            
            # AI quality metrics
            "average_confidence_score": round(avg_confidence, 3),
            "high_confidence_analyses": high_confidence_count
        }
```

**Success Criteria**: Complete AI analysis system with orchestration and result processing

---

### **Step 5.3: Response Builder**
**File**: `app/services/tiktok_shared/tiktok_response_builder.py`

```python
import logging
from typing import List, Dict, Any
from datetime import datetime
from app.models.tiktok_schemas import (
    TikTokCommentAnalysis, 
    TikTokAnalysisMetadata, 
    TikTokUnifiedAnalysisResponse
)

logger = logging.getLogger(__name__)

class TikTokResponseBuilder:
    """
    Builds final unified response for TikTok analysis.
    Shared component that assembles analysis results into standardized response format.
    """
    
    def build_unified_response(
        self,
        comment_analyses: List[TikTokCommentAnalysis],
        collection_metadata: Dict[str, Any],
        analysis_metadata: Dict[str, Any]
    ) -> TikTokUnifiedAnalysisResponse:
        """
        Build final unified analysis response from all components.
        
        Args:
            comment_analyses: List of TikTok comment analyses
            collection_metadata: Metadata from data collection phase
            analysis_metadata: Metadata from AI analysis phase
            
        Returns:
            Complete TikTokUnifiedAnalysisResponse object
        """
        logger.info(f"Building unified response with {len(comment_analyses)} analyses")
        
        try:
            # Combine metadata from all phases
            combined_metadata = self._combine_metadata(
                collection_metadata, 
                analysis_metadata
            )
            
            # Create metadata object with validation
            metadata = TikTokAnalysisMetadata(**combined_metadata)
            
            # Create unified response
            response = TikTokUnifiedAnalysisResponse(
                comment_analyses=comment_analyses,
                metadata=metadata
            )
            
            logger.info("Successfully built unified TikTok response")
            return response
            
        except Exception as e:
            logger.error(f"Error building unified response: {e}")
            raise
    
    def _combine_metadata(
        self, 
        collection_metadata: Dict[str, Any], 
        analysis_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Combine metadata from collection and analysis phases.
        
        Args:
            collection_metadata: Data collection metadata
            analysis_metadata: AI analysis metadata
            
        Returns:
            Combined metadata dictionary
        """
        # Start with analysis metadata as base (more comprehensive)
        combined = dict(analysis_metadata)
        
        # Add collection-specific metadata
        collection_fields = [
            "hashtag_api_calls", 
            "comments_api_calls", 
            "videos_collected", 
            "comments_collected",
            "collection_time_seconds"
        ]
        
        for field in collection_fields:
            if field in collection_metadata:
                combined[field] = collection_metadata[field]
        
        # Ensure all required fields have defaults
        required_defaults = {
            "total_videos_analyzed": 0,
            "total_comments_found": 0,
            "relevant_comments_extracted": 0,
            "analysis_timestamp": datetime.now().isoformat() + "Z",
            "processing_time_seconds": 0.0,
            "model_used": "unknown",
            "hashtags_analyzed": [],
            "total_video_plays": 0,
            "total_video_likes": 0,
            "average_engagement_rate": 0.0,
            "hashtag_api_calls": 0,
            "comments_api_calls": 0,
            "max_reply_depth": 0,
            "total_threaded_comments": 0,
            "top_level_comments": 0,
            "reply_comments": 0
        }
        
        for key, default_value in required_defaults.items():
            if key not in combined:
                combined[key] = default_value
        
        return combined
```

**Success Criteria**: Response builder that creates standardized TikTok API responses

---

## 📱 **Phase 6: Hashtag Collection Service**

### **Step 6.1: Hashtag Data Collector**
**File**: `app/services/tiktok_hashtags/hashtag_collector.py`

```python
import time
import logging
from typing import Dict, List, Tuple
from app.services.tiktok_shared.tiktok_api_client import TikTokAPIClient
from app.services.tiktok_shared.tiktok_comment_collector import TikTokCommentCollector
from app.core.config import settings

logger = logging.getLogger(__name__)

class TikTokHashtagCollector:
    """
    Collects TikTok videos from hashtag feeds using Challenge Feed by Keyword API.
    Hashtag-specific implementation that coordinates video and comment collection.
    """
    
    def __init__(self, rapidapi_key: str):
        self.api_client = TikTokAPIClient(rapidapi_key)
        self.comment_collector = TikTokCommentCollector(self.api_client)
        self.request_delay = settings.TIKTOK_REQUEST_DELAY
        logger.info("TikTok Hashtag Collector initialized")
    
    def collect_hashtag_data(
        self, 
        hashtags: List[str], 
        posts_per_hashtag: int = 20
    ) -> Dict:
        """
        Collect videos and comments for multiple hashtags.
        
        This is the main coordination method that:
        1. Collects videos for each hashtag via Challenge Feed API
        2. Collects comments for all videos via Comments API
        3. Assembles comprehensive metadata
        
        Args:
            hashtags: List of hashtags to search (without # symbol)
            posts_per_hashtag: Number of posts to collect per hashtag
            
        Returns:
            Dictionary with videos_by_hashtag, comments_by_video, and metadata
        """
        logger.info(f"Starting hashtag data collection for {len(hashtags)} hashtags: {hashtags}")
        
        start_time = time.time()
        videos_by_hashtag = {}
        all_videos = []
        hashtag_api_calls = 0
        
        # Phase 1: Collect videos for each hashtag
        for hashtag in hashtags:
            logger.info(f"Collecting videos for hashtag: #{hashtag}")
            
            try:
                videos, api_calls = self._collect_hashtag_videos(hashtag, posts_per_hashtag)
                videos_by_hashtag[hashtag] = videos
                all_videos.extend(videos)
                hashtag_api_calls += api_calls
                
                logger.info(f"Successfully collected {len(videos)} videos for #{hashtag}")
                
                # Rate limiting between hashtags to avoid overwhelming API
                if len(hashtags) > 1:
                    time.sleep(self.request_delay)
                    
            except Exception as e:
                logger.error(f"Failed to collect videos for hashtag #{hashtag}: {e}")
                videos_by_hashtag[hashtag] = []
        
        # Phase 2: Collect comments for all videos
        logger.info(f"Starting comment collection for {len(all_videos)} total videos")
        comments_result = self.comment_collector.collect_all_comments(all_videos)
        
        collection_time = time.time() - start_time
        
        # Phase 3: Build comprehensive metadata
        metadata = {
            # Request parameters
            "hashtags_searched": hashtags,
            "posts_per_hashtag_requested": posts_per_hashtag,
            
            # Collection results
            "total_videos_collected": len(all_videos),
            "total_comments_collected": comments_result["metadata"]["total_comments_collected"],
            
            # API usage tracking
            "hashtag_api_calls": hashtag_api_calls,
            "comments_api_calls": comments_result["metadata"]["comments_api_calls"],
            
            # Performance metrics
            "collection_time_seconds": round(collection_time, 2),
            
            # Detailed breakdown
            "videos_by_hashtag_count": {ht: len(vids) for ht, vids in videos_by_hashtag.items()},
            "successful_hashtags": len([ht for ht, vids in videos_by_hashtag.items() if vids]),
            "failed_hashtags": len([ht for ht, vids in videos_by_hashtag.items() if not vids])
        }
        
        logger.info(f"Hashtag data collection completed in {collection_time:.2f}s: {len(all_videos)} videos, {metadata['total_comments_collected']} comments")
        
        return {
            "videos_by_hashtag": videos_by_hashtag,
            "comments_by_video": comments_result["comments_by_video"],
            "metadata": metadata
        }
    
    def _collect_hashtag_videos(self, hashtag: str, count: int) -> Tuple[List[Dict], int]:
        """
        Collect videos for a single hashtag with pagination support.
        
        Args:
            hashtag: Hashtag to search (without # symbol)
            count: Number of videos to collect
            
        Returns:
            Tuple of (videos_list, api_calls_made)
        """
        logger.info(f"Fetching up to {count} videos for hashtag: #{hashtag}")
        
        videos = []
        cursor = None
        api_calls = 0
        max_attempts = 10  # Prevent infinite loops
        
        while len(videos) < count and api_calls < max_attempts:
            try:
                # Determine batch size for this request
                remaining = count - len(videos)
                batch_size = min(50, remaining)  # API typically supports max 50 per request
                
                # Make API call
                logger.debug(f"Calling Challenge Feed API: hashtag={hashtag}, count={batch_size}, cursor={cursor}")
                response = self.api_client.challenge_feed_by_keyword(
                    keyword=hashtag, 
                    count=batch_size, 
                    cursor=cursor
                )
                api_calls += 1
                
                # Extract videos from response
                data = response.get("data", {})
                aweme_list = data.get("aweme_list", [])
                
                if not aweme_list:
                    logger.info(f"No more videos available for hashtag #{hashtag} after {len(videos)} videos")
                    break
                
                # Add videos to collection (respect count limit)
                for video in aweme_list:
                    if len(videos) >= count:
                        break
                    videos.append(video)
                
                # Check pagination status
                has_more = data.get("has_more", False)
                cursor = data.get("cursor")
                
                if not has_more or not cursor:
                    logger.info(f"Reached end of available videos for hashtag #{hashtag}")
                    break
                
                logger.debug(f"Collected {len(videos)}/{count} videos for #{hashtag}")
                
                # Rate limiting between API calls
                if len(videos) < count:  # Don't delay on the last call
                    time.sleep(self.request_delay)
                
            except Exception as e:
                logger.error(f"Error collecting videos for hashtag #{hashtag} (attempt {api_calls}): {e}")
                break
        
        logger.info(f"Completed video collection for #{hashtag}: {len(videos)} videos in {api_calls} API calls")
        return videos, api_calls
    
    def close(self):
        """Close API client connection and cleanup resources."""
        try:
            self.api_client.close()
            logger.info("TikTok Hashtag Collector closed successfully")
        except Exception as e:
            logger.error(f"Error closing TikTok Hashtag Collector: {e}")
```

**Success Criteria**: Hashtag collector with robust pagination and error handling

---

### **Step 6.2: Main Hashtag Service**
**File**: `app/services/tiktok_hashtags/hashtag_service.py`

```python
import time
import logging
from typing import Dict, Any
from datetime import datetime
from app.models.tiktok_schemas import (
    TikTokHashtagAnalysisRequest, 
    TikTokUnifiedAnalysisResponse
)
from app.services.tiktok_hashtags.hashtag_collector import TikTokHashtagCollector
from app.services.tiktok_shared.tiktok_data_cleaners import assemble_videos_with_comments
from app.services.tiktok_shared.tiktok_ai_analyzer import TikTokAnalysisOrchestrator, TikTokResultsProcessor
from app.services.tiktok_shared.tiktok_response_builder import TikTokResponseBuilder
from app.core.config import settings
from app.core.exceptions import (
    ValidationError,
    AuthenticationError, 
    ConfigurationError,
    TikTokDataCollectionError,
    TikTokAnalysisError
)

logger = logging.getLogger(__name__)

class TikTokHashtagAnalysisService:
    """
    Main service for TikTok hashtag analysis endpoint.
    Orchestrates the complete 4-stage analysis pipeline:
    1. Data Collection - Hashtag videos and comments
    2. Data Cleaning - Transform and structure data  
    3. AI Analysis - Extract insights with OpenAI
    4. Response Assembly - Build final response
    """
    
    def __init__(self):
        self.response_builder = TikTokResponseBuilder()
        self.results_processor = TikTokResultsProcessor()
        logger.info("TikTok Hashtag Analysis Service initialized")
    
    async def analyze_hashtags(
        self, 
        request: TikTokHashtagAnalysisRequest, 
        api_key: str
    ) -> TikTokUnifiedAnalysisResponse:
        """
        Main hashtag analysis method implementing the complete 4-stage pipeline.
        
        Args:
            request: TikTok hashtag analysis request
            api_key: Service API key for authentication
            
        Returns:
            Complete TikTokUnifiedAnalysisResponse
        """
        start_time = time.time()
        request_id = f"hashtag_{int(start_time)}"
        
        logger.info(f"[{request_id}] Starting TikTok hashtag analysis for {len(request.hashtags)} hashtags")
        
        try:
            # Pre-flight validation
            self._validate_request(request)
            self._validate_api_key(api_key)
            
            # Stage 1: Data Collection
            logger.info(f"[{request_id}] Stage 1: TikTok hashtag data collection")
            collection_result = self._collect_hashtag_data(request)
            
            # Stage 2: Data Cleaning & Structuring
            logger.info(f"[{request_id}] Stage 2: Data cleaning and structuring")
            posts_with_comments = assemble_videos_with_comments(
                collection_result["videos_by_hashtag"],
                collection_result["comments_by_video"],
                request.hashtags
            )
            
            if not posts_with_comments:
                logger.warning(f"[{request_id}] No videos were successfully processed")
            
            # Stage 3: AI Analysis
            logger.info(f"[{request_id}] Stage 3: AI analysis for {len(posts_with_comments)} videos")
            analysis_results = await self._run_ai_analysis(
                posts_with_comments, 
                request.ai_analysis_prompt,
                request.model,
                request.max_quote_length
            )
            
            # Stage 4: Response Assembly
            logger.info(f"[{request_id}] Stage 4: Assembling final response")
            processing_time = time.time() - start_time
            
            response = self._assemble_response(
                analysis_results,
                collection_result["metadata"],
                posts_with_comments,
                processing_time,
                request.model
            )
            
            logger.info(f"[{request_id}] Hashtag analysis completed successfully in {processing_time:.1f}s")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"[{request_id}] Hashtag analysis failed after {processing_time:.1f}s: {e}")
            raise
    
    def _validate_request(self, request: TikTokHashtagAnalysisRequest) -> None:
        """
        Validate hashtag analysis request parameters.
        
        Args:
            request: Request object to validate
            
        Raises:
            ValidationError: If request parameters are invalid
        """
        # Check hashtags list
        if not request.hashtags:
            raise ValidationError(
                message="At least one hashtag is required",
                field="hashtags",
                value=request.hashtags
            )
        
        if len(request.hashtags) > settings.MAX_HASHTAGS_PER_REQUEST:
            raise ValidationError(
                message=f"Maximum {settings.MAX_HASHTAGS_PER_REQUEST} hashtags allowed per request",
                field="hashtags",
                value=len(request.hashtags)
            )
        
        # Clean hashtags (remove # symbol if present)
        cleaned_hashtags = []
        for hashtag in request.hashtags:
            clean_hashtag = hashtag.strip().lstrip('#')
            if not clean_hashtag:
                raise ValidationError(
                    message="Hashtag cannot be empty after cleaning",
                    field="hashtags",
                    value=hashtag
                )
            if len(clean_hashtag) > 50:  # Reasonable hashtag length limit
                raise ValidationError(
                    message="Hashtag too long (max 50 characters)",
                    field="hashtags", 
                    value=clean_hashtag
                )
            cleaned_hashtags.append(clean_hashtag)
        
        # Update request with cleaned hashtags
        request.hashtags = cleaned_hashtags
        
        # Validate posts per hashtag
        if request.number_of_posts_per_hashtag > settings.MAX_POSTS_PER_HASHTAG:
            raise ValidationError(
                message=f"Maximum {settings.MAX_POSTS_PER_HASHTAG} posts per hashtag allowed",
                field="number_of_posts_per_hashtag", 
                value=request.number_of_posts_per_hashtag
            )
        
        # Validate AI prompt
        if len(request.ai_analysis_prompt.strip()) < 10:
            raise ValidationError(
                message="AI analysis prompt must be at least 10 characters long",
                field="ai_analysis_prompt",
                value=len(request.ai_analysis_prompt.strip())
            )
        
        logger.info(f"Request validation passed for hashtags: {request.hashtags}")
    
    def _validate_api_key(self, api_key: str) -> None:
        """
        Validate service API key.
        
        Args:
            api_key: API key to validate
            
        Raises:
            AuthenticationError: If API key is invalid
            ConfigurationError: If service key not configured
        """
        if not api_key:
            raise AuthenticationError(
                message="Service API key is required",
                auth_type="service_api_key"
            )
        
        expected_key = settings.SERVICE_API_KEY
        if not expected_key:
            raise ConfigurationError(
                message="Service API key not configured on server",
                config_key="SERVICE_API_KEY"
            )
        
        if api_key != expected_key:
            raise AuthenticationError(
                message="Invalid service API key",
                auth_type="service_api_key"
            )
        
        logger.debug("Service API key validation passed")
    
    def _collect_hashtag_data(self, request: TikTokHashtagAnalysisRequest) -> Dict[str, Any]:
        """
        Stage 1: Collect TikTok hashtag data via RapidAPI.
        
        Args:
            request: Analysis request with hashtag parameters
            
        Returns:
            Dictionary with videos, comments, and collection metadata
            
        Raises:
            ConfigurationError: If TikTok API key not configured
            TikTokDataCollectionError: If data collection fails
        """
        rapidapi_key = settings.TIKTOK_RAPIDAPI_KEY
        if not rapidapi_key:
            raise ConfigurationError(
                message="TikTok RapidAPI key not configured",
                config_key="TIKTOK_RAPIDAPI_KEY"
            )
        
        try:
            collector = TikTokHashtagCollector(rapidapi_key)
            
            result = collector.collect_hashtag_data(
                hashtags=request.hashtags,
                posts_per_hashtag=request.number_of_posts_per_hashtag
            )
            
            collector.close()
            return result
            
        except Exception as e:
            logger.error(f"Data collection failed: {e}")
            raise TikTokDataCollectionError(
                message="Failed to collect TikTok hashtag data",
                api_endpoint="challenge_feed_by_keyword"
            )
    
    async def _run_ai_analysis(
        self, 
        posts_with_comments,
        user_prompt: str,
        model: str,
        max_quote_length: int
    ) -> List:
        """
        Stage 3: Run AI analysis on collected and cleaned data.
        
        Args:
            posts_with_comments: List of PostWithComments objects
            user_prompt: User's analysis criteria
            model: AI model to use
            max_quote_length: Maximum quote length
            
        Returns:
            List of analysis results per video
            
        Raises:
            ConfigurationError: If OpenAI API key not configured
            TikTokAnalysisError: If AI analysis fails
        """
        openai_key = settings.OPENAI_API_KEY
        if not openai_key:
            raise ConfigurationError(
                message="OpenAI API key not configured",
                config_key="OPENAI_API_KEY"
            )
        
        try:
            orchestrator = TikTokAnalysisOrchestrator(
                openai_key=openai_key,
                max_concurrent=settings.MAX_CONCURRENT_AGENTS
            )
            
            analysis_results = await orchestrator.analyze_all_videos(
                posts_with_comments,
                user_prompt,
                max_quote_length
            )
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise TikTokAnalysisError(
                message="Failed to complete AI analysis",
                model=model
            )
    
    def _assemble_response(
        self,
        analysis_results: List,
        collection_metadata: Dict[str, Any],
        posts_with_comments,
        processing_time: float,
        model_used: str
    ) -> TikTokUnifiedAnalysisResponse:
        """
        Stage 4: Assemble final response with comprehensive metadata.
        
        Args:
            analysis_results: AI analysis results
            collection_metadata: Collection metadata
            posts_with_comments: Original posts with comments
            processing_time: Total processing time
            model_used: AI model identifier
            
        Returns:
            Complete TikTokUnifiedAnalysisResponse
        """
        # Process results using results processor
        combined_results = self.results_processor.combine_analysis_results(
            analysis_results,
            collection_metadata,
            posts_with_comments,
            processing_time,
            model_used
        )
        
        # Build unified response using response builder
        return self.response_builder.build_unified_response(
            comment_analyses=combined_results["comment_analyses"],
            collection_metadata=collection_metadata,
            analysis_metadata=combined_results["metadata"]
        )
```

**Success Criteria**: Complete hashtag service with 4-stage pipeline orchestration

---

## 🚀 **Phase 7: FastAPI Endpoint**

### **Step 7.1: Main FastAPI Application**
**File**: `app/main.py`

```python
import time
import logging
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import (
    TikTokAPIException,
    ValidationError,
    AuthenticationError,
    ConfigurationError,
    TikTokDataCollectionError,
    TikTokAnalysisError,
    RateLimitExceededError,
    TimeoutError
)
from app.models.tiktok_schemas import (
    TikTokHashtagAnalysisRequest,
    TikTokUnifiedAnalysisResponse
)
from app.services.tiktok_hashtags.hashtag_service import TikTokHashtagAnalysisService

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", summary="Health Check")
async def health_check():
    """
    Health check endpoint to verify API status and configuration.
    
    Returns:
        Health status with configuration details
    """
    return {
        "status": "healthy",
        "api_name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "timestamp": time.time(),
        "configuration": {
            "tiktok_api_configured": bool(settings.TIKTOK_RAPIDAPI_KEY),
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "service_auth_configured": bool(settings.SERVICE_API_KEY),
            "max_hashtags_per_request": settings.MAX_HASHTAGS_PER_REQUEST,
            "max_posts_per_hashtag": settings.MAX_POSTS_PER_HASHTAG,
            "log_level": settings.LOG_LEVEL
        }
    }

# Root endpoint
@app.get("/", summary="API Information")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    
    Returns:
        API overview and endpoint list
    """
    return {
        "api_name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "endpoints": [
            "/analyze-tiktok-hashtags",
            "/health", 
            "/docs",
            "/redoc"
        ],
        "documentation": {
            "interactive_docs": "/docs",
            "alternative_docs": "/redoc"
        }
    }

# Main hashtag analysis endpoint
@app.post(
    "/analyze-tiktok-hashtags",
    response_model=TikTokUnifiedAnalysisResponse,
    summary="Analyze TikTok Hashtag Conversations",
    description="Monitor and analyze TikTok hashtag conversations for sentiment, themes, and purchase intent",
    responses={
        200: {"description": "Successful analysis with extracted insights"},
        400: {"description": "Invalid request parameters"},
        401: {"description": "Authentication failed"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        502: {"description": "TikTok API error"},
        503: {"description": "AI analysis service unavailable"},
        504: {"description": "Request timeout"}
    }
)
async def analyze_tiktok_hashtags(
    request: TikTokHashtagAnalysisRequest,
    x_api_key: str = Header(..., description="Service API key for authentication")
):
    """
    Analyze TikTok conversations for specified hashtags.
    
    This endpoint performs comprehensive analysis of TikTok hashtag conversations:
    
    1. **Data Collection**: Collects videos from specified hashtag feeds via TikTok API
    2. **Comment Gathering**: Retrieves comments for each video with pagination support  
    3. **Content Analysis**: Uses AI to analyze comments for sentiment, themes, and insights
    4. **Results Assembly**: Returns structured analysis with engagement metrics
    
    **Use Cases**:
    - Product launch monitoring (track hashtags during BMW model launches)
    - Brand sentiment analysis (monitor brand perception on TikTok)
    - Influencer campaign tracking (analyze hashtag campaign performance)
    - Market research (understand audience reactions and purchase intent)
    
    **Rate Limits**: 
    - Maximum 5 hashtags per request
    - Maximum 50 posts per hashtag
    - Processing typically takes 30-90 seconds depending on data volume
    
    Args:
        request: TikTok hashtag analysis request parameters
        x_api_key: Service API key (passed via X-API-Key header)
        
    Returns:
        TikTokUnifiedAnalysisResponse: Complete analysis results with metadata
    """
    request_id = f"tiktok_hashtag_{int(time.time())}"
    
    try:
        logger.info(f"[{request_id}] TikTok hashtag analysis request received: hashtags={request.hashtags}, posts_per_hashtag={request.number_of_posts_per_hashtag}")
        
        # Initialize service and run analysis
        service = TikTokHashtagAnalysisService()
        response = await service.analyze_hashtags(request, x_api_key)
        
        logger.info(f"[{request_id}] TikTok hashtag analysis completed successfully: {len(response.comment_analyses)} analyses extracted")
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] TikTok hashtag analysis failed: {e}")
        
        # Map custom exceptions to appropriate HTTP responses
        if isinstance(e, ValidationError):
            raise HTTPException(status_code=400, detail=e.to_dict())
        elif isinstance(e, AuthenticationError):
            raise HTTPException(status_code=401, detail=e.to_dict())
        elif isinstance(e, ConfigurationError):
            raise HTTPException(status_code=500, detail=e.to_dict())
        elif isinstance(e, TikTokDataCollectionError):
            raise HTTPException(status_code=502, detail=e.to_dict())
        elif isinstance(e, TikTokAnalysisError):
            raise HTTPException(status_code=503, detail=e.to_dict())
        elif isinstance(e, RateLimitExceededError):
            raise HTTPException(status_code=429, detail=e.to_dict())
        elif isinstance(e, TimeoutError):
            raise HTTPException(status_code=504, detail=e.to_dict())
        else:
            # Generic error for unexpected exceptions
            raise HTTPException(
                status_code=500, 
                detail={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred during analysis",
                    "request_id": request_id,
                    "type": "internal_error"
                }
            )

# Global exception handler for TikTok API exceptions
@app.exception_handler(TikTokAPIException)
async def tiktok_api_exception_handler(request, exc: TikTokAPIException):
    """
    Global exception handler for TikTok API exceptions.
    
    Args:
        request: FastAPI request object
        exc: TikTok API exception
        
    Returns:
        JSON error response with appropriate status code
    """
    logger.error(f"TikTok API exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """
    Global exception handler for unexpected errors.
    
    Args:
        request: FastAPI request object  
        exc: Unexpected exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR", 
            "message": "An unexpected error occurred",
            "type": "internal_error"
        }
    )

# Startup event handler
@app.on_event("startup")
async def startup_event():
    """
    Application startup handler.
    Logs startup information and validates configuration.
    """
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"TikTok API configured: {bool(settings.TIKTOK_RAPIDAPI_KEY)}")
    logger.info(f"OpenAI configured: {bool(settings.OPENAI_API_KEY)}")
    logger.info(f"Service auth configured: {bool(settings.SERVICE_API_KEY)}")

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown handler.
    Logs shutdown information and cleanup.
    """
    logger.info(f"Shutting down {settings.API_TITLE}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
```

**Success Criteria**: Complete FastAPI application with TikTok hashtag endpoint and comprehensive error handling

---

## 🧪 **Phase 8: Testing & Validation**

### **Step 8.1: Integration Test**
**File**: `tests/tiktok_hashtags/test_hashtag_endpoint.py`

```python
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from app.services.tiktok_hashtags.hashtag_service import TikTokHashtagAnalysisService
from app.models.tiktok_schemas import TikTokHashtagAnalysisRequest

class TestTikTokHashtagEndpoint:
    """
    Integration tests for TikTok hashtag analysis endpoint.
    Tests the complete pipeline from request to response.
    """
    
    @pytest.fixture
    def bmw_hashtag_request(self):
        """Sample BMW motorcycle hashtag analysis request."""
        return TikTokHashtagAnalysisRequest(
            hashtags=["bmwmotorrad", "motorcyclelife"],
            number_of_posts_per_hashtag=10,
            ai_analysis_prompt="Analyze motorcycle discussions for sentiment about BMW motorcycles, purchase intent, and user experiences. Focus on comments expressing opinions about BMW bikes, pricing, performance, or buying decisions.",
            model="gpt-4o-mini-2024-07-18",
            max_quote_length=180
        )
    
    @pytest.fixture 
    def mock_tiktok_challenge_feed_response(self):
        """Mock TikTok Challenge Feed API response."""
        return {
            "status": "ok",
            "data": {
                "aweme_list": [
                    {
                        "aweme_id": "7542094204852358455",
                        "desc": "💥 #bmw #motorcycle #r1250gs Adventure riding! 🏍️",
                        "create_time": 1756030808,
                        "author": {
                            "uid": "7187686173291217966",
                            "nickname": "bmw_rider_123",
                            "unique_id": "bmwrider123",
                            "region": "US"
                        },
                        "statistics": {
                            "digg_count": 15420,
                            "comment_count": 287,
                            "play_count": 892350,
                            "share_count": 1240
                        },
                        "cha_list": [
                            {"cha_name": "bmw", "type": 1},
                            {"cha_name": "motorcycle", "type": 1},
                            {"cha_name": "r1250gs", "type": 1}
                        ],
                        "share_url": "https://www.tiktok.com/@bmwrider123/video/7542094204852358455",
                        "video": {"duration": 45000}  # 45 seconds
                    }
                ],
                "has_more": False,
                "cursor": None
            }
        }
    
    @pytest.fixture
    def mock_tiktok_comments_response(self):
        """Mock TikTok Comments API response."""
        return {
            "status": "ok",
            "data": {
                "comments": [
                    {
                        "cid": "7542463290149634837",
                        "aweme_id": "7542094204852358455", 
                        "create_time": 1756116591,
                        "text": "Absolutely love my R1250GS! Best adventure bike I've ever owned. Planning to upgrade from my old F800GS soon 🔥",
                        "digg_count": 156,
                        "reply_id": "0",
                        "reply_to_reply_id": "0",
                        "user": {
                            "uid": "7527529371570373640",
                            "nickname": "adventure_rider_sarah",
                            "unique_id": "adventuresarah"
                        }
                    },
                    {
                        "cid": "7542463290149634838",
                        "aweme_id": "7542094204852358455",
                        "create_time": 1756116650,
                        "text": "How's the maintenance cost compared to Japanese bikes? Thinking about getting one",
                        "digg_count": 45,
                        "reply_id": "7542463290149634837",
                        "reply_to_reply_id": "0",
                        "user": {
                            "uid": "7527529371570373641", 
                            "nickname": "mike_moto",
                            "unique_id": "mikemoto"
                        }
                    },
                    {
                        "cid": "7542463290149634839",
                        "aweme_id": "7542094204852358455",
                        "create_time": 1756116700,
                        "text": "BMW reliability has improved so much! My S1000RR has been bulletproof",
                        "digg_count": 89,
                        "reply_id": "0",
                        "reply_to_reply_id": "0",
                        "user": {
                            "uid": "7527529371570373642",
                            "nickname": "track_day_tom",
                            "unique_id": "trackdaytom"
                        }
                    }
                ],
                "has_more": False,
                "cursor": None
            }
        }
    
    @pytest.fixture
    def mock_openai_analysis_response(self):
        """Mock OpenAI analysis response for BMW motorcycle content."""
        return [
            {
                "video_id": "7542094204852358455",
                "video_url": "https://www.tiktok.com/@bmwrider123/video/7542094204852358455",
                "quote": "Absolutely love my R1250GS! Best adventure bike I've ever owned. Planning to upgrade from my old F800GS soon",
                "sentiment": "positive",
                "theme": "experience",
                "purchase_intent": "high",
                "date": "2024-08-25T12:45:30Z",
                "source": "tiktok",
                "conversation_context": "User sharing positive experience with BMW R1250GS adventure motorcycle",
                "thread_context": "Discussion thread about BMW motorcycle ownership and experiences",
                "confidence_score": 0.94,
                "hashtag_source": "bmwmotorrad",
                "video_play_count": 892350,
                "video_like_count": 15420,
                "comment_like_count": 156,
                "parent_comment_id": None,
                "thread_depth": 0,
                "is_reply": False
            },
            {
                "video_id": "7542094204852358455",
                "video_url": "https://www.tiktok.com/@bmwrider123/video/7542094204852358455",
                "quote": "How's the maintenance cost compared to Japanese bikes? Thinking about getting one",
                "sentiment": "neutral",
                "theme": "comparison",
                "purchase_intent": "medium",
                "date": "2024-08-25T12:46:20Z",
                "source": "tiktok",
                "conversation_context": "User asking about maintenance costs and considering BMW purchase",
                "thread_context": "Reply to positive BMW experience comment, seeking practical information",
                "confidence_score": 0.88,
                "hashtag_source": "bmwmotorrad",
                "video_play_count": 892350,
                "video_like_count": 15420,
                "comment_like_count": 45,
                "parent_comment_id": "7542463290149634837",
                "thread_depth": 1,
                "is_reply": True
            }
        ]
    
    @patch('app.core.config.settings.TIKTOK_RAPIDAPI_KEY', 'test_rapidapi_key')
    @patch('app.core.config.settings.OPENAI_API_KEY', 'test_openai_key') 
    @patch('app.core.config.settings.SERVICE_API_KEY', 'test_service_key')
    async def test_complete_hashtag_analysis_pipeline(
        self,
        bmw_hashtag_request,
        mock_tiktok_challenge_feed_response, 
        mock_tiktok_comments_response,
        mock_openai_analysis_response
    ):
        """
        Test complete hashtag analysis pipeline from request to response.
        Validates the entire 4-stage process with BMW motorcycle use case.
        """
        
        # Mock TikTok API calls
        with patch('app.services.tiktok_shared.tiktok_api_client.TikTokAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock API responses
            mock_client.challenge_feed_by_keyword.return_value = mock_tiktok_challenge_feed_response
            mock_client.get_video_comments.return_value = mock_tiktok_comments_response
            
            # Mock OpenAI analysis
            with patch('app.services.tiktok_shared.tiktok_ai_analyzer.TikTokAnalysisOrchestrator') as mock_orchestrator_class:
                mock_orchestrator = Mock()
                mock_orchestrator_class.return_value = mock_orchestrator
                mock_orchestrator.analyze_all_videos.return_value = [mock_openai_analysis_response]
                
                # Execute complete analysis
                service = TikTokHashtagAnalysisService()
                response = await service.analyze_hashtags(
                    bmw_hashtag_request,
                    "test_service_key"
                )
                
                # Validate response structure
                assert isinstance(response.comment_analyses, list)
                assert len(response.comment_analyses) >= 1
                assert response.metadata.total_videos_analyzed >= 1
                assert "bmwmotorrad" in response.metadata.hashtags_analyzed
                
                # Validate first analysis (BMW experience comment)
                first_analysis = response.comment_analyses[0]
                assert first_analysis.sentiment == "positive"
                assert first_analysis.theme == "experience"
                assert first_analysis.purchase_intent == "high"
                assert first_analysis.source == "tiktok"
                assert first_analysis.hashtag_source == "bmwmotorrad"
                assert first_analysis.confidence_score >= 0.8
                assert "R1250GS" in first_analysis.quote
                
                # Validate metadata
                assert response.metadata.total_video_plays > 0
                assert response.metadata.total_video_likes > 0
                assert response.metadata.average_engagement_rate > 0
                assert response.metadata.hashtag_api_calls > 0
                assert response.metadata.comments_api_calls >= 0
                
                # Validate threading information
                if len(response.comment_analyses) > 1:
                    second_analysis = response.comment_analyses[1]
                    assert second_analysis.is_reply == True
                    assert second_analysis.thread_depth == 1
                    assert second_analysis.parent_comment_id is not None
    
    def test_hashtag_request_validation(self):
        """Test hashtag request validation logic."""
        service = TikTokHashtagAnalysisService()
        
        # Test empty hashtags list
        with pytest.raises(Exception):  # Should raise ValidationError
            invalid_request = TikTokHashtagAnalysisRequest(
                hashtags=[],
                ai_analysis_prompt="Test prompt for validation"
            )
            service._validate_request(invalid_request)
        
        # Test hashtag cleaning (remove # symbols)
        request_with_hashes = TikTokHashtagAnalysisRequest(
            hashtags=["#bmwmotorrad", "#motorcyclelife", "advrider"],
            ai_analysis_prompt="Test prompt for hashtag cleaning"
        )
        service._validate_request(request_with_hashes)
        assert request_with_hashes.hashtags == ["bmwmotorrad", "motorcyclelife", "advrider"]
        
        # Test too many hashtags
        with pytest.raises(Exception):  # Should raise ValidationError
            too_many_request = TikTokHashtagAnalysisRequest(
                hashtags=["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"],  # Exceeds limit
                ai_analysis_prompt="Test prompt for too many hashtags"
            )
            service._validate_request(too_many_request)
        
        # Test AI prompt too short
        with pytest.raises(Exception):  # Should raise ValidationError
            short_prompt_request = TikTokHashtagAnalysisRequest(
                hashtags=["bmw"],
                ai_analysis_prompt="short"  # Less than 10 characters
            )
            service._validate_request(short_prompt_request)
    
    @patch('app.core.config.settings.SERVICE_API_KEY', 'correct_service_key')
    def test_service_api_key_validation(self):
        """Test service API key validation."""
        service = TikTokHashtagAnalysisService()
        
        # Valid key should pass
        service._validate_api_key("correct_service_key")
        
        # Invalid key should raise exception
        with pytest.raises(Exception):  # Should raise AuthenticationError
            service._validate_api_key("wrong_service_key")
        
        # Empty key should raise exception
        with pytest.raises(Exception):  # Should raise AuthenticationError
            service._validate_api_key("")
    
    def test_performance_expectations(self, bmw_hashtag_request):
        """Test performance expectations and resource usage."""
        # Validate request parameters are within reasonable limits
        assert len(bmw_hashtag_request.hashtags) <= 5
        assert bmw_hashtag_request.number_of_posts_per_hashtag <= 50
        assert bmw_hashtag_request.max_quote_length <= 500
        assert len(bmw_hashtag_request.ai_analysis_prompt) >= 10
        
        # Expected processing characteristics
        expected_max_videos = len(bmw_hashtag_request.hashtags) * bmw_hashtag_request.number_of_posts_per_hashtag
        expected_max_api_calls = len(bmw_hashtag_request.hashtags) + expected_max_videos  # Hashtag calls + comment calls
        
        assert expected_max_videos <= 250  # Reasonable limit
        assert expected_max_api_calls <= 270  # API usage limit
```

**Success Criteria**: Comprehensive integration test covering BMW use case scenarios

---

### **Step 8.2: API Test Script**  
**File**: `test_tiktok_api.py` (in project root)

```python
import asyncio
import httpx
import json
import time
from typing import Dict, Any

async def test_tiktok_hashtag_endpoint():
    """
    Test the TikTok hashtag endpoint with real API calls.
    This script validates the complete API functionality.
    """
    
    # Configuration
    base_url = "http://localhost:8000"  # Adjust for your server
    service_api_key = "your_service_api_key_here"  # From your .env file
    
    # BMW motorcycle hashtag analysis request
    bmw_request_payload = {
        "hashtags": ["bmw", "motorcycle", "bmwmotorrad"],
        "number_of_posts_per_hashtag": 8,  # Small number for testing
        "ai_analysis_prompt": "Analyze motorcycle discussions for sentiment about BMW motorcycles, purchase intent, and user experiences. Focus on comments expressing genuine opinions about BMW bikes, pricing, performance comparisons, or buying decisions. Include discussions about specific BMW models like R1250GS, F850GS, S1000RR, etc.",
        "model": "gpt-4o-mini-2024-07-18",
        "max_quote_length": 180
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": service_api_key
    }
    
    print("🚀 Testing TikTok Hashtag Analysis API")
    print("="*50)
    print(f"Request payload:")
    print(json.dumps(bmw_request_payload, indent=2))
    print("\n" + "="*50)
    
    async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
        try:
            print("📡 Sending request to API...")
            start_time = time.time()
            
            response = await client.post(
                f"{base_url}/analyze-tiktok-hashtags",
                json=bmw_request_payload,
                headers=headers
            )
            
            end_time = time.time()
            request_duration = end_time - start_time
            
            print(f"⏱️  Response received in {request_duration:.1f} seconds")
            print(f"📊 HTTP Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ SUCCESS! Analysis completed")
                print("="*50)
                print("📈 ANALYSIS RESULTS SUMMARY:")
                print(f"   • Videos analyzed: {result['metadata']['total_videos_analyzed']}")
                print(f"   • Comments found: {result['metadata']['total_comments_found']}")
                print(f"   • Relevant extractions: {result['metadata']['relevant_comments_extracted']}")
                print(f"   • Hashtags processed: {result['metadata']['hashtags_analyzed']}")
                print(f"   • Total video plays: {result['metadata']['total_video_plays']:,}")
                print(f"   • Total video likes: {result['metadata']['total_video_likes']:,}")
                print(f"   • Average engagement: {result['metadata']['average_engagement_rate']:.2f}%")
                print(f"   • Processing time: {result['metadata']['processing_time_seconds']:.1f}s")
                print(f"   • API calls made: {result['metadata']['hashtag_api_calls']} hashtag + {result['metadata']['comments_api_calls']} comments")
                
                if result['comment_analyses']:
                    print(f"\n🔍 SAMPLE ANALYSIS RESULTS ({len(result['comment_analyses'])} total):")
                    for i, analysis in enumerate(result['comment_analyses'][:3], 1):  # Show first 3
                        print(f"\n   Analysis #{i}:")
                        print(f"      Quote: \"{analysis['quote'][:100]}{'...' if len(analysis['quote']) > 100 else ''}\"")
                        print(f"      Sentiment: {analysis['sentiment']} | Theme: {analysis['theme']} | Purchase Intent: {analysis['purchase_intent']}")
                        print(f"      Confidence: {analysis['confidence_score']:.2f} | Source: #{analysis['hashtag_source']}")
                        print(f"      Video: {analysis['video_play_count']:,} plays, {analysis['video_like_count']:,} likes")
                        if analysis.get('is_reply'):
                            print(f"      Thread: Reply at depth {analysis['thread_depth']}")
                
                # Validation checks
                print(f"\n✅ VALIDATION CHECKS:")
                assert result['metadata']['total_videos_analyzed'] > 0, "No videos were analyzed"
                assert len(result['metadata']['hashtags_analyzed']) > 0, "No hashtags were processed"  
                assert result['metadata']['processing_time_seconds'] > 0, "Processing time should be positive"
                
                if result['comment_analyses']:
                    first_analysis = result['comment_analyses'][0]
                    assert first_analysis['source'] == 'tiktok', "Source should be tiktok"
                    assert first_analysis['confidence_score'] >= 0.0, "Confidence score should be valid"
                    assert first_analysis['confidence_score'] <= 1.0, "Confidence score should be valid"
                    assert first_analysis['hashtag_source'] in bmw_request_payload['hashtags'], "Hashtag source should match request"
                
                print("   • All validation checks passed ✅")
                
            else:
                print("❌ REQUEST FAILED")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    print(f"Error details:")
                    print(json.dumps(error_data, indent=2))
                except:
                    pass
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

async def test_health_endpoint():
    """Test the health check endpoint."""
    print("\n🏥
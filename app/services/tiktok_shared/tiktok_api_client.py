"""
TikTok API Client for RapidAPI TikTok Scraper

Single HTTP client for all TikTok API endpoints with proper error handling and rate limiting.
Handles all TikTok API endpoints with comprehensive error handling, timeouts, and rate limiting.

Key Methods:
- challenge_feed(challenge_name: str) - Hashtag posts
- user_posts(username: str) - Account posts  
- search_videos(query: str) - Search functionality
- get_video_comments(video_id: str) - Comments (used by all)

Reusability: 100% - All endpoints use same base client
"""

import httpx
import asyncio
import time
import logging
from typing import Dict, List, Optional
from app.core.config import settings
from app.core.exceptions import (
    TikTokDataCollectionError, 
    TikTokTimeoutError,
    RateLimitExceededError,
    TikTokValidationError
)

logger = logging.getLogger(__name__)

class TikTokAPIClient:
    """
    HTTP client for RapidAPI TikTok Scraper.
    Handles all TikTok API endpoints with proper error handling and rate limiting.
    """
    
    def __init__(self, rapidapi_key: str):
        # Basic validation
        if not rapidapi_key or len(rapidapi_key.strip()) < 10:
            raise TikTokValidationError("Invalid RapidAPI key provided", field="rapidapi_key")
        
        self.rapidapi_key = rapidapi_key.strip()
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
        self.last_request_time = 0
        logger.info("TikTok API Client initialized")
    
    def _rate_limit_delay(self):
        """Simple rate limiting - respect the delay setting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < settings.TIKTOK_REQUEST_DELAY:
            delay = settings.TIKTOK_REQUEST_DELAY - time_since_last
            logger.debug(f"Rate limiting: sleeping {delay:.2f}s")
            time.sleep(delay)
        
        self.last_request_time = time.time()
    
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
            raise TikTokTimeoutError(
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
    
    def challenge_feed(self, challenge_name: str, max_cursor: Optional[str] = None) -> Dict:
        """
        Get posts from hashtag challenge feed using Challenge Feed endpoint.
        
        Args:
            challenge_name: Challenge/hashtag name to search (without # symbol)
            max_cursor: Pagination cursor for retrieving more results
            
        Returns:
            TikTok API response with aweme_list
        """
        # Basic input validation
        if not challenge_name or len(challenge_name.strip()) == 0:
            raise TikTokValidationError("Challenge name cannot be empty", field="challenge_name")
        
        clean_name = challenge_name.strip().lstrip('#')
        if not clean_name.replace('_', '').isalnum():
            raise TikTokValidationError("Invalid challenge name format", field="challenge_name", value=challenge_name)
        
        # Check if we should use mock data
        if settings.USE_MOCK_DATA:
            logger.info(f"Using MOCK data for challenge: {clean_name}")
            return self._get_mock_hashtag_videos(clean_name, 20)  # Default count
        
        endpoint = f"/challenge/{clean_name}/feed"
        url = f"{self.base_url}{endpoint}"
        
        params = {}
        if max_cursor:
            params["max_cursor"] = max_cursor
        
        logger.info(f"Calling Challenge Feed API for challenge: {clean_name}")
        
        try:
            self._rate_limit_delay()
            response = self.client.get(url, params=params)
            return self._handle_response(response, endpoint)
        except Exception as e:
            logger.error(f"Error in challenge_feed for {clean_name}: {e}")
            raise
    
    def get_video_comments(self, video_id: str, max_cursor: Optional[str] = None) -> Dict:
        """
        Get comments for a specific video using Comments by Video ID endpoint.
        
        Args:
            video_id: TikTok video ID (aweme_id)
            max_cursor: Pagination cursor for retrieving more comments
            
        Returns:
            TikTok API response with comments array
        """
        # Basic input validation
        if not video_id or len(video_id.strip()) == 0:
            raise TikTokValidationError("Video ID cannot be empty", field="video_id")
        
        clean_video_id = video_id.strip()
        if not clean_video_id.isdigit():
            raise TikTokValidationError("Video ID must be numeric", field="video_id", value=video_id)
        
        # Check if we should use mock data
        if settings.USE_MOCK_DATA:
            logger.info(f"Using MOCK data for video comments: {clean_video_id}")
            return self._get_mock_video_comments(clean_video_id, 20)  # Default count
        
        endpoint = f"/comments/{clean_video_id}"
        url = f"{self.base_url}{endpoint}"
        
        params = {}
        if max_cursor:
            params["max_cursor"] = max_cursor
        
        logger.info(f"Calling Comments API for video: {clean_video_id}")
        
        try:
            self._rate_limit_delay()
            response = self.client.get(url, params=params)
            return self._handle_response(response, endpoint)
        except Exception as e:
            logger.error(f"Error in get_video_comments for {clean_video_id}: {e}")
            raise
    
    def user_posts(self, username: str, count: int = 50, cursor: Optional[str] = None) -> Dict:
        """
        Get posts from a user account feed using User Feed endpoint.
        
        Args:
            username: TikTok username
            count: Number of posts to retrieve
            cursor: Pagination cursor
            
        Returns:
            TikTok API response with user feed videos (same format as hashtag endpoint)
        """
        # Basic input validation
        if not username or len(username.strip()) == 0:
            raise TikTokValidationError("Username cannot be empty", field="username")
        
        clean_username = username.strip().lstrip('@')
        if not clean_username.replace('_', '').replace('.', '').isalnum():
            raise TikTokValidationError("Invalid username format", field="username", value=username)
        
        if count < 1 or count > 100:
            raise TikTokValidationError("Count must be between 1 and 100", field="count", value=count)
        
        # Check if we should use mock data
        if settings.USE_MOCK_DATA:
            logger.info(f"Using MOCK data for user posts: {clean_username}")
            return self._get_mock_user_posts(clean_username, count)
        
        endpoint = f"/user/{clean_username}/feed"
        url = f"{self.base_url}{endpoint}"
        
        params = {}
        if count != 50:  # Only add count if different from default
            params["count"] = count
        if cursor:
            params["cursor"] = cursor
        
        logger.info(f"Calling User Feed API for: {clean_username}")
        
        try:
            self._rate_limit_delay()
            response = self.client.get(url, params=params)
            return self._handle_response(response, endpoint)
        except Exception as e:
            logger.error(f"Error in user_posts for {clean_username}: {e}")
            raise
    
    def close(self):
        """Close the HTTP client."""
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
            logger.info("TikTok API Client closed")
        except Exception as e:
            logger.warning(f"Error closing TikTok API client: {e}")
    
    def _get_mock_hashtag_videos(self, hashtag: str, count: int) -> Dict:
        """Generate mock hashtag video data for testing."""
        import time
        
        mock_videos = []
        for i in range(count):
            video_id = f"mock_{hashtag}_{i}_{int(time.time())}"
            mock_videos.append({
                "aweme_id": video_id,
                "desc": f"This is a mock TikTok video about {hashtag}. Video #{i+1}",
                "create_time": int(time.time()) - (i * 3600),
                "author": {
                    "uid": f"mock_user_{i}",
                    "nickname": f"MockUser{i}",
                    "unique_id": f"mockuser{i}",
                    "region": "US"
                },
                "statistics": {
                    "digg_count": 100 + (i * 10),
                    "comment_count": 20 + (i * 5),
                    "play_count": 1000 + (i * 100),
                    "share_count": 10 + i,
                    "collect_count": 5 + i
                },
                "share_url": f"https://vm.tiktok.com/mock{i}",
                "cha_list": [{"cha_name": hashtag}]
            })
        
        return {
            "status": "ok",
            "data": {
                "aweme_list": mock_videos,
                "has_more": len(mock_videos) >= count,
                "cursor": "mock_cursor_123"
            }
        }
    
    def _get_mock_video_comments(self, video_id: str, count: int) -> Dict:
        """Generate mock video comments for testing."""
        import time
        
        mock_comments = []
        for i in range(min(count, 10)):  # Limit to 10 mock comments
            mock_comments.append({
                "cid": f"mock_comment_{video_id}_{i}",
                "text": f"This is mock comment #{i+1} for video {video_id}. Great content!",
                "create_time": int(time.time()) - (i * 1800),
                "user": {
                    "uid": f"comment_user_{i}",
                    "nickname": f"CommentUser{i}",
                    "unique_id": f"commentuser{i}"
                },
                "digg_count": 5 + i,
                "reply_id": "0",
                "reply_to_reply_id": "0"
            })
        
        return {
            "status": "ok",
            "data": {
                "comments": mock_comments,
                "has_more": False,
                "cursor": "mock_comment_cursor"
            }
        }
    
    def _get_mock_user_posts(self, username: str, count: int) -> Dict:
        """Generate mock user posts data for testing (same format as account API)."""
        import time
        
        mock_videos = []
        for i in range(count):
            video_id = f"753031742141294517{i}"  # Realistic TikTok video ID format
            mock_videos.append({
                "aweme_id": video_id,
                "desc": f"Amazing content from @{username}! This is post #{i+1} #trending #content",
                "create_time": int(time.time()) - (i * 3600 * 24),  # One day apart
                "author": {
                    "uid": "681196071625020314",  # Realistic UID format
                    "nickname": username,
                    "unique_id": username,
                    "region": "US",
                    "avatar_thumb": {
                        "url_list": ["https://example.com/avatar.jpg"]
                    },
                    "follower_count": 5840377,
                    "following_count": 22,
                    "aweme_count": 384 + i
                },
                "statistics": {
                    "aweme_id": video_id,
                    "digg_count": 100018 + (i * 1000),
                    "comment_count": 4567 + (i * 100),
                    "play_count": 1454327 + (i * 10000),
                    "share_count": 3504 + (i * 50),
                    "collect_count": 6451 + (i * 20),
                    "download_count": 589 + (i * 10)
                },
                "share_url": f"https://www.tiktok.com/@{username}/video/{video_id}",
                "video": {
                    "duration": 13768 + (i * 1000),  # ~14 seconds
                    "ratio": "540p",
                    "cover": {
                        "url_list": ["https://example.com/cover.jpg"]
                    }
                },
                "music": {
                    "id": 7370712348132805000 + i,
                    "title": f"Trending Song {i+1}",
                    "author": "Artist Name"
                }
            })
        
        return {
            "status": "ok",
            "data": {
                "aweme_list": mock_videos,
                "has_more": len(mock_videos) >= count,
                "min_cursor": int(time.time() * 1000),
                "max_cursor": int(time.time() * 1000) - (count * 3600 * 24 * 1000),
                "cursor": f"mock_user_cursor_{username}"
            }
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

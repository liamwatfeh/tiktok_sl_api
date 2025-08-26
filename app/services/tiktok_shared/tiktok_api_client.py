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
    
    def challenge_feed(self, challenge_name: str, max_cursor: Optional[str] = None) -> Dict:
        """
        Get posts from hashtag challenge feed using Challenge Feed endpoint.
        
        Args:
            challenge_name: Challenge/hashtag name to search (without # symbol)
            max_cursor: Pagination cursor for retrieving more results
            
        Returns:
            TikTok API response with aweme_list
        """
        endpoint = f"/challenge/{challenge_name}/feed"
        url = f"{self.base_url}{endpoint}"
        
        params = {}
        if max_cursor:
            params["max_cursor"] = max_cursor
        
        logger.info(f"Calling Challenge Feed API for challenge: {challenge_name}")
        
        try:
            response = self.client.get(url, params=params)
            return self._handle_response(response, endpoint)
        except Exception as e:
            logger.error(f"Error in challenge_feed for {challenge_name}: {e}")
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
        endpoint = f"/comments/{video_id}"
        url = f"{self.base_url}{endpoint}"
        
        params = {}
        if max_cursor:
            params["max_cursor"] = max_cursor
        
        logger.info(f"Calling Comments API for video: {video_id}")
        
        try:
            response = self.client.get(url, params=params)
            return self._handle_response(response, endpoint)
        except Exception as e:
            logger.error(f"Error in get_video_comments for {video_id}: {e}")
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

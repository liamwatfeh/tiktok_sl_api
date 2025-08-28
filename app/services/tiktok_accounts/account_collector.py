"""
TikTok Account Collector
Uses User Posts API to collect account videos

Unique Components:
- AccountCollector - Uses User Posts API
- Metadata tracks account-specific metrics

Data Source: RapidAPI User Posts
Use Case: Monitor @bmwmotorrad official accounts
"""

import logging
from typing import Dict, List, Tuple
from app.services.tiktok_shared.tiktok_api_client import TikTokAPIClient
from app.core.exceptions import TikTokValidationError, TikTokDataCollectionError

logger = logging.getLogger(__name__)

class AccountCollector:
    """
    Collector for TikTok account posts using User Posts API.
    Follows the same pattern as hashtag collection but for user accounts.
    """
    
    def __init__(self, api_client: TikTokAPIClient):
        """
        Initialize account collector with API client.
        
        Args:
            api_client: TikTok API client instance
        """
        if not api_client:
            raise TikTokValidationError("API client is required", field="api_client")
        
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        logger.info("AccountCollector initialized")
    
    def collect_account_videos(self, username: str, max_posts: int = 20) -> Tuple[List[Dict], Dict]:
        """
        Collect videos from a specific TikTok account.
        
        Args:
            username: TikTok username to analyze (without @)
            max_posts: Maximum number of posts to collect (default: 20)
            
        Returns:
            Tuple of (videos_list, collection_metadata)
            Same format as hashtag collector - direct pipeline compatibility!
        """
        # Input validation
        if not username or len(username.strip()) == 0:
            raise TikTokValidationError("Username cannot be empty", field="username")
        
        clean_username = username.strip().lstrip('@')
        if not clean_username.replace('_', '').replace('.', '').isalnum():
            raise TikTokValidationError(
                "Username contains invalid characters", 
                field="username", 
                value=username
            )
        
        if max_posts < 1 or max_posts > 100:
            raise TikTokValidationError(
                "max_posts must be between 1 and 100", 
                field="max_posts", 
                value=max_posts
            )
        
        logger.info(f"Collecting {max_posts} videos for account: @{clean_username}")
        
        try:
            # Call TikTok API for user posts
            api_response = self.api_client.user_posts(clean_username, count=max_posts)
            
            # Extract videos from response
            videos = api_response.get("data", {}).get("aweme_list", [])
            
            if not videos:
                logger.warning(f"No videos found in API response for account: @{clean_username}")
                return [], {"error": "no_videos_in_response"}
            
            # Limit to requested count (already handled by API, but double-check)
            limited_videos = videos[:max_posts]
            
            # Create collection metadata
            metadata = {
                "account_requested": clean_username,
                "posts_requested": max_posts,
                "posts_found": len(videos),
                "posts_returned": len(limited_videos),
                "api_has_more": api_response.get("data", {}).get("has_more", False),
                "collection_time": logger.name,  # Will be filled by service
                "source": "user_posts_api"
            }
            
            logger.info(
                f"Account collection complete: {len(limited_videos)} videos collected "
                f"for @{clean_username}"
            )
            
            return limited_videos, metadata
            
        except TikTokValidationError:
            # Re-raise validation errors
            raise
        except TikTokDataCollectionError:
            # Re-raise data collection errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error collecting account videos for @{clean_username}: {e}")
            raise TikTokDataCollectionError(
                message=f"Failed to collect videos for account @{clean_username}: {str(e)}",
                api_endpoint=f"/user/{clean_username}/feed"
            )
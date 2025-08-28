"""
TikTok Comment Collector

Collects and paginates through TikTok video comments.
Shared component used by all TikTok endpoints.

Key Methods:
- collect_video_comments(aweme_id: str) - Single video
- collect_all_comments(videos: List[Dict]) - Batch processing
- Handle TikTok's reply threading system

Reusability: 100% - Identical logic regardless of video source
"""

import time
import logging
from typing import Dict, List, Optional
from app.services.tiktok_shared.tiktok_api_client import TikTokAPIClient
from app.core.config import settings
from app.core.exceptions import TikTokValidationError, TikTokDataCollectionError

logger = logging.getLogger(__name__)

class TikTokCommentCollector:
    """
    Collects and paginates through TikTok video comments.
    Shared component used by all TikTok endpoints.
    """
    
    def __init__(self, api_client: TikTokAPIClient):
        if not api_client:
            raise TikTokValidationError("API client is required", field="api_client")
        
        self.api_client = api_client
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
        # Basic input validation
        if not aweme_id or len(aweme_id.strip()) == 0:
            raise TikTokValidationError("Video ID cannot be empty", field="aweme_id")
        
        clean_aweme_id = aweme_id.strip()
        if not clean_aweme_id.isdigit():
            raise TikTokValidationError("Video ID must be numeric", field="aweme_id", value=aweme_id)
        
        if max_comments < 1 or max_comments > 200:
            raise TikTokValidationError("Max comments must be between 1 and 200", field="max_comments", value=max_comments)
        
        logger.info(f"Collecting comments for video {clean_aweme_id}, max: {max_comments}")
        
        all_comments = []
        cursor = None
        calls_made = 0
        
        while len(all_comments) < max_comments:
            try:
                # API client handles rate limiting automatically
                response = self.api_client.get_video_comments(clean_aweme_id, cursor)
                calls_made += 1
                
                # Extract comments from response
                comments_data = response.get("data", {})
                comments = comments_data.get("comments", [])
                
                if not comments:
                    logger.info(f"No more comments found for video {clean_aweme_id}")
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
                    logger.info(f"Reached end of comments for video {clean_aweme_id}")
                    break
                
                logger.debug(f"Collected {len(all_comments)} comments so far for video {clean_aweme_id}")
                
            except TikTokDataCollectionError as e:
                logger.error(f"TikTok API error collecting comments for video {clean_aweme_id}: {e.message}")
                break
            except Exception as e:
                logger.error(f"Unexpected error collecting comments for video {clean_aweme_id}: {str(e)}")
                break
        
        logger.info(f"Finished collecting {len(all_comments)} comments for video {clean_aweme_id}")
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
        # Basic input validation
        if not videos:
            logger.warning("No videos provided for comment collection")
            return {
                "comments_by_video": {},
                "metadata": {
                    "videos_processed": 0,
                    "successful_videos": 0,
                    "total_comments_collected": 0,
                    "comments_api_calls": 0
                }
            }
        
        if not isinstance(videos, list):
            raise TikTokValidationError("Videos must be a list", field="videos")
        
        if max_comments_per_video < 1 or max_comments_per_video > 200:
            raise TikTokValidationError("Max comments per video must be between 1 and 200", field="max_comments_per_video", value=max_comments_per_video)
        
        # Safety limit for batch processing
        if len(videos) > 100:
            logger.warning(f"Large batch of {len(videos)} videos - this may take a while")
        
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
                
            except TikTokValidationError as e:
                logger.warning(f"Invalid video ID {aweme_id}: {e.message}")
                comments_by_video[aweme_id] = []
            except TikTokDataCollectionError as e:
                logger.error(f"Failed to collect comments for video {aweme_id}: {e.message}")
                comments_by_video[aweme_id] = []
            except Exception as e:
                logger.error(f"Unexpected error collecting comments for video {aweme_id}: {str(e)}")
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

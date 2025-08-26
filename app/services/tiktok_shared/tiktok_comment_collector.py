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

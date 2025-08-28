"""
TikTok Data Cleaners
====================

Shared data cleaning and transformation utilities for TikTok API responses.
Handles the actual response schemas from RapidAPI TikTok Scraper endpoints.

This module provides:
- Video data cleaning and normalization
- Comment data cleaning and validation  
- Text processing and encoding fixes
- Error handling for malformed data
- Data structure standardization
"""

import re
import html
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from app.core.exceptions import TikTokDataCollectionError, TikTokValidationError

logger = logging.getLogger(__name__)


class TikTokDataCleaner:
    """
    Handles cleaning and transformation of TikTok API response data.
    
    This cleaner processes the actual response structures from RapidAPI TikTok Scraper:
    - Hashtag endpoint: /challenge/{hashtag}/feed  
    - Comments endpoint: /comments/{video_id}
    - Account endpoint: /user/posts (future)
    - Search endpoint: /search/videos (future)
    """
    
    def __init__(self):
        """Initialize the data cleaner with configuration."""
        self.max_description_length = 1000
        self.max_comment_length = 2000
        self.min_text_length = 1
        logger.info("TikTok Data Cleaner initialized")
    
    def clean_hashtag_response(self, api_response: Dict) -> Tuple[List[Dict], Dict]:
        """
        Clean hashtag challenge feed response.
        
        Args:
            api_response: Raw response from /challenge/{hashtag}/feed endpoint
            
        Returns:
            Tuple of (cleaned_videos_list, metadata)
            
        Raises:
            TikTokDataCollectionError: If response structure is invalid
        """
        # Basic input validation
        if not api_response:
            raise TikTokValidationError("API response cannot be empty", field="api_response")
        
        logger.info("Cleaning hashtag challenge feed response")
        
        try:
            # Validate response structure
            if not isinstance(api_response, dict):
                raise TikTokDataCollectionError(
                    message="Invalid API response format - not a dictionary",
                    api_endpoint="hashtag_feed"
                )
            
            if api_response.get("status") != "ok":
                raise TikTokDataCollectionError(
                    message=f"API returned error status: {api_response.get('status')}",
                    api_endpoint="hashtag_feed"
                )
            
            data = api_response.get("data", {})
            aweme_list = data.get("aweme_list", [])
            
            if not isinstance(aweme_list, list):
                raise TikTokDataCollectionError(
                    message="Invalid aweme_list format - not a list",
                    api_endpoint="hashtag_feed"
                )
            
            # Safety check for reasonable data size
            if len(aweme_list) > 1000:
                logger.warning(f"Large aweme_list size: {len(aweme_list)} videos - this may take time to process")
                aweme_list = aweme_list[:1000]  # Limit to prevent memory issues
            
            # Clean each video
            cleaned_videos = []
            skipped_count = 0
            
            for i, video_data in enumerate(aweme_list):
                try:
                    cleaned_video = self.clean_video_data(video_data)
                    if cleaned_video:
                        cleaned_videos.append(cleaned_video)
                    else:
                        skipped_count += 1
                        logger.debug(f"Skipped video at index {i} - missing required fields")
                        
                except Exception as e:
                    skipped_count += 1
                    logger.warning(f"Failed to clean video at index {i}: {e}")
                    continue
            
            # Create metadata
            metadata = {
                "total_videos_raw": len(aweme_list),
                "videos_cleaned": len(cleaned_videos),
                "videos_skipped": skipped_count,
                "cleaning_timestamp": datetime.now(timezone.utc).isoformat(),
                "api_endpoint": "hashtag_feed"
            }
            
            logger.info(f"Hashtag cleaning complete: {len(cleaned_videos)}/{len(aweme_list)} videos cleaned")
            return cleaned_videos, metadata
            
        except Exception as e:
            if isinstance(e, TikTokDataCollectionError):
                raise
            logger.error(f"Unexpected error cleaning hashtag response: {e}")
            raise TikTokDataCollectionError(
                message="Failed to clean hashtag response data",
                api_endpoint="hashtag_feed"
            )
    
    def clean_video_data(self, video_raw: Dict) -> Optional[Dict]:
        """
        Clean individual video data from TikTok API response.
        
        Args:
            video_raw: Raw video object from API response
            
        Returns:
            Cleaned video dictionary or None if invalid
        """
        # Basic input validation
        if not video_raw or not isinstance(video_raw, dict):
            logger.debug("Invalid video data - not a dictionary")
            return None
        
        try:
            # Extract required fields
            aweme_id = video_raw.get("aweme_id")
            if not aweme_id:
                logger.debug("Video missing aweme_id - skipping")
                return None
            
            # Clean description/caption
            desc = video_raw.get("desc", "")
            cleaned_desc = self.clean_text(desc, self.max_description_length)
            
            # Extract creation timestamp
            create_time = video_raw.get("create_time", 0)
            try:
                create_date = datetime.fromtimestamp(create_time, tz=timezone.utc).isoformat()
            except (ValueError, OSError):
                create_date = datetime.now(timezone.utc).isoformat()
                logger.debug(f"Invalid create_time {create_time} for video {aweme_id}")
            
            # Extract author information
            author_raw = video_raw.get("author", {})
            author = {
                "uid": str(author_raw.get("uid", "")),
                "nickname": self.clean_text(author_raw.get("nickname", ""), 100),
                "unique_id": self.clean_text(author_raw.get("unique_id", ""), 100),
                "region": author_raw.get("region", ""),
                "signature": self.clean_text(author_raw.get("signature", ""), 200)
            }
            
            # Extract statistics with safe conversion
            stats_raw = video_raw.get("statistics", {})
            statistics = {}
            for stat_name in ["digg_count", "comment_count", "play_count", "share_count", "collect_count"]:
                try:
                    value = stats_raw.get(stat_name, 0)
                    statistics[stat_name] = max(0, int(value))  # Ensure non-negative
                except (ValueError, TypeError):
                    statistics[stat_name] = 0
                    logger.debug(f"Invalid {stat_name} value for video {aweme_id}: {value}")
            
            # Extract share URL
            share_url = video_raw.get("share_url", "")
            if not share_url:
                # Fallback to share_info if available
                share_info = video_raw.get("share_info", {})
                share_url = share_info.get("share_url", "")
            
            # Extract hashtags from cha_list
            cha_list = video_raw.get("cha_list", [])
            hashtags = []
            for cha in cha_list:
                if isinstance(cha, dict) and "cha_name" in cha:
                    hashtag_name = self.clean_text(cha["cha_name"], 100)
                    if hashtag_name:
                        hashtags.append(hashtag_name)
            
            # Calculate engagement rate
            engagement_rate = 0.0
            if statistics["play_count"] > 0:
                total_engagements = statistics["digg_count"] + statistics["comment_count"] + statistics["share_count"]
                engagement_rate = (total_engagements / statistics["play_count"]) * 100
            
            # Build cleaned video object
            cleaned_video = {
                "aweme_id": aweme_id,
                "desc": cleaned_desc,
                "create_time": create_time,
                "create_date": create_date,
                "author": author,
                "statistics": statistics,
                "share_url": share_url,
                "hashtags": hashtags,
                "engagement_rate": round(engagement_rate, 2),
                
                # Additional metadata
                "region": video_raw.get("region", ""),
                "item_comment_settings": video_raw.get("item_comment_settings", 0),
                "video_duration": self._extract_video_duration(video_raw),
                "is_ads": video_raw.get("is_ads", False)
            }
            
            return cleaned_video
            
        except Exception as e:
            logger.warning(f"Error cleaning video data: {e}")
            return None
    
    def clean_comments_response(self, api_response: Dict, video_id: str) -> Tuple[List[Dict], Dict]:
        """
        Clean comments response from TikTok API.
        
        Args:
            api_response: Raw response from /comments/{video_id} endpoint
            video_id: TikTok video ID for context
            
        Returns:
            Tuple of (cleaned_comments_list, metadata)
        """
        # Basic input validation
        if not api_response:
            raise TikTokValidationError("API response cannot be empty", field="api_response")
        
        if not video_id or not isinstance(video_id, str):
            raise TikTokValidationError("Video ID must be a non-empty string", field="video_id")
        
        logger.info(f"Cleaning comments response for video {video_id}")
        
        try:
            # Validate response structure  
            if api_response.get("status") != "ok":
                raise TikTokDataCollectionError(
                    message=f"Comments API returned error status: {api_response.get('status')}",
                    api_endpoint="video_comments"
                )
            
            data = api_response.get("data", {})
            comments_raw = data.get("comments", [])
            
            if not isinstance(comments_raw, list):
                logger.warning(f"Invalid comments format for video {video_id}")
                return [], {"error": "invalid_format"}
            
            # Safety check for reasonable data size
            if len(comments_raw) > 5000:
                logger.warning(f"Large comments list size: {len(comments_raw)} comments - limiting to 5000")
                comments_raw = comments_raw[:5000]  # Prevent memory issues
            
            # Clean each comment
            cleaned_comments = []
            skipped_count = 0
            
            for comment_raw in comments_raw:
                try:
                    cleaned_comment = self.clean_comment_data(comment_raw, video_id)
                    if cleaned_comment:
                        cleaned_comments.append(cleaned_comment)
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    skipped_count += 1
                    logger.debug(f"Failed to clean comment: {e}")
                    continue
            
            # Create metadata
            metadata = {
                "video_id": video_id,
                "total_comments_raw": len(comments_raw),
                "comments_cleaned": len(cleaned_comments),
                "comments_skipped": skipped_count,
                "cleaning_timestamp": datetime.now(timezone.utc).isoformat(),
                "has_more": data.get("has_more", False),
                "cursor": data.get("cursor"),
                "api_endpoint": "video_comments"
            }
            
            logger.info(f"Comments cleaning complete: {len(cleaned_comments)}/{len(comments_raw)} comments cleaned")
            return cleaned_comments, metadata
            
        except Exception as e:
            if isinstance(e, TikTokDataCollectionError):
                raise
            logger.error(f"Unexpected error cleaning comments response: {e}")
            raise TikTokDataCollectionError(
                message=f"Failed to clean comments for video {video_id}",
                api_endpoint="video_comments"
            )
    
    def clean_comment_data(self, comment_raw: Dict, video_id: str) -> Optional[Dict]:
        """
        Clean individual comment data.
        
        Args:
            comment_raw: Raw comment object from API
            video_id: Video ID for validation
            
        Returns:
            Cleaned comment dictionary or None if invalid
        """
        # Basic input validation
        if not comment_raw or not isinstance(comment_raw, dict):
            logger.debug("Invalid comment data - not a dictionary")
            return None
        
        try:
            # Extract required fields
            cid = comment_raw.get("cid")
            text = comment_raw.get("text", "")
            
            if not cid or not text:
                logger.info(f"Comment missing cid or text - cid: '{cid}', text: '{text}' - skipping")
                return None
            
            # Clean comment text
            cleaned_text = self.clean_text(text, self.max_comment_length)
            if len(cleaned_text) < self.min_text_length:
                logger.info(f"Comment text too short after cleaning - original: '{text[:50]}...' cleaned: '{cleaned_text}' (len={len(cleaned_text)})")
                return None
            
            # Extract user information
            user_raw = comment_raw.get("user", {})
            user = {
                "uid": str(user_raw.get("uid", "")),
                "nickname": self.clean_text(user_raw.get("nickname", ""), 100),
                "unique_id": self.clean_text(user_raw.get("unique_id", ""), 100)
            }
            
            # Extract timestamps
            create_time = comment_raw.get("create_time", 0)
            try:
                create_date = datetime.fromtimestamp(create_time, tz=timezone.utc).isoformat()
            except (ValueError, OSError):
                create_date = datetime.now(timezone.utc).isoformat()
            
            # Extract engagement metrics with safe conversion
            try:
                digg_count = max(0, int(comment_raw.get("digg_count", 0)))
            except (ValueError, TypeError):
                digg_count = 0
            
            # Extract threading information
            reply_id = comment_raw.get("reply_id", "0")
            reply_to_reply_id = comment_raw.get("reply_to_reply_id", "0")
            is_reply = reply_id != "0"
            
            cleaned_comment = {
                "cid": cid,
                "aweme_id": video_id,
                "text": cleaned_text,
                "user": user,
                "create_time": create_time,
                "create_date": create_date,
                "digg_count": digg_count,
                "reply_id": reply_id,
                "reply_to_reply_id": reply_to_reply_id,
                "is_reply": is_reply,
                "text_length": len(cleaned_text)
            }
            
            return cleaned_comment
            
        except Exception as e:
            logger.error(f"Error cleaning comment data: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def clean_text(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            max_length: Maximum length to truncate to
            
        Returns:
            Cleaned text string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Safety check for extremely long text
        if len(text) > 50000:  # 50KB limit
            logger.warning(f"Extremely long text detected ({len(text)} chars) - truncating")
            text = text[:50000]
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove only control characters, keep emojis and international text
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        
        # Truncate if needed
        if max_length and len(text) > max_length:
            text = text[:max_length].rstrip()
        
        return text
    
    def _extract_video_duration(self, video_raw: Dict) -> int:
        """Extract video duration in seconds."""
        try:
            # Try video.duration first (in milliseconds)
            video_obj = video_raw.get("video", {})
            duration_ms = video_obj.get("duration", 0)
            if duration_ms > 0:
                return int(duration_ms / 1000)
            
            # Try music.duration as fallback
            music_obj = video_raw.get("music", {})
            duration_s = music_obj.get("duration", 0)
            if duration_s > 0:
                return int(duration_s)
            
            return 0
            
        except Exception:
            return 0
    
    def validate_cleaned_data(self, cleaned_videos: List[Dict]) -> Dict:
        """
        Validate cleaned video data for consistency.
        
        Args:
            cleaned_videos: List of cleaned video dictionaries
            
        Returns:
            Validation report dictionary
        """
        # Basic input validation
        if not isinstance(cleaned_videos, list):
            raise TikTokValidationError("Cleaned videos must be a list", field="cleaned_videos")
        
        logger.info(f"Validating {len(cleaned_videos)} cleaned videos")
        
        validation_report = {
            "total_videos": len(cleaned_videos),
            "valid_videos": 0,
            "videos_with_issues": 0,
            "issues": []
        }
        
        for i, video in enumerate(cleaned_videos):
            issues = []
            
            # Check required fields
            if not video.get("aweme_id"):
                issues.append("missing_aweme_id")
            
            if not video.get("desc"):
                issues.append("empty_description")
                
            if not video.get("author", {}).get("uid"):
                issues.append("missing_author_uid")
                
            if video.get("statistics", {}).get("play_count", 0) < 0:
                issues.append("negative_play_count")
            
            # Track issues
            if issues:
                validation_report["videos_with_issues"] += 1
                validation_report["issues"].extend(issues)
            else:
                validation_report["valid_videos"] += 1
        
        logger.info(f"Validation complete: {validation_report['valid_videos']}/{validation_report['total_videos']} videos valid")
        return validation_report


# Convenience functions for external usage
def clean_hashtag_response(api_response: Dict) -> Tuple[List[Dict], Dict]:
    """Convenience function to clean hashtag API response."""
    cleaner = TikTokDataCleaner()
    return cleaner.clean_hashtag_response(api_response)


def clean_comments_response(api_response: Dict, video_id: str) -> Tuple[List[Dict], Dict]:
    """Convenience function to clean comments API response."""
    cleaner = TikTokDataCleaner()
    return cleaner.clean_comments_response(api_response, video_id)
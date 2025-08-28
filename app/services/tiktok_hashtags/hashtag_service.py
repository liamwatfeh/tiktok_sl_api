"""
TikTok Hashtag Analysis Service
===============================

Main orchestration service for TikTok hashtag analysis endpoint.
Coordinates all shared components to provide complete hashtag analysis.

This service implements the 4-stage pipeline:
1. Data Collection: Get hashtag videos from TikTok API
2. Data Cleaning: Clean and validate video data
3. Comment Collection + AI Analysis: Get comments and analyze with AI
4. Response Assembly: Build unified API response
"""

import logging
import time
import asyncio
from typing import Dict, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.core.exceptions import (
    TikTokDataCollectionError, 
    TikTokAnalysisError,
    TikTokValidationError,
    ConfigurationError
)
from app.models.tiktok_schemas import TikTokHashtagAnalysisRequest
from app.services.tiktok_shared.tiktok_api_client import TikTokAPIClient
from app.services.tiktok_shared.tiktok_data_cleaners import TikTokDataCleaner
from app.services.tiktok_shared.tiktok_comment_collector import TikTokCommentCollector
from app.services.tiktok_shared.tiktok_ai_analyzer import TikTokAIAnalyzer
from app.services.tiktok_shared.tiktok_response_builder import TikTokResponseBuilder

logger = logging.getLogger(__name__)


class TikTokHashtagService:
    """
    Main service for TikTok hashtag analysis.
    
    Orchestrates the complete pipeline from hashtag input to analyzed results.
    Uses all shared infrastructure components in sequence.
    """
    
    def __init__(self):
        """Initialize the hashtag service with all required components."""
        # Validate critical configuration
        if not settings.TIKTOK_RAPIDAPI_KEY:
            raise ConfigurationError("TikTok API key not configured", config_key="TIKTOK_RAPIDAPI_KEY")
        if not settings.OPENAI_API_KEY:
            raise ConfigurationError("OpenAI API key not configured", config_key="OPENAI_API_KEY")
        
        # Initialize shared components
        try:
            self.api_client = TikTokAPIClient(settings.TIKTOK_RAPIDAPI_KEY)
            self.data_cleaner = TikTokDataCleaner()
            self.comment_collector = TikTokCommentCollector(self.api_client)
            self.ai_analyzer = TikTokAIAnalyzer()
            self.response_builder = TikTokResponseBuilder()
        except Exception as e:
            logger.error(f"Failed to initialize service components: {e}")
            raise ConfigurationError(f"Service initialization failed: {e}")
        
        logger.info("TikTok Hashtag Service initialized with all components")
    
    async def analyze_hashtag(self, request: TikTokHashtagAnalysisRequest) -> Dict:
        """
        Perform complete hashtag analysis.
        
        Args:
            request: Validated hashtag analysis request
            
        Returns:
            Complete analysis response dictionary
        """
        # Basic security validation for internal use
        if not request.hashtag or len(request.hashtag.strip()) == 0:
            raise TikTokValidationError("Hashtag cannot be empty", field="hashtag")
        
        # Remove # symbol if present and sanitize
        clean_hashtag = request.hashtag.strip().lstrip('#')
        if not clean_hashtag.replace('_', '').isalnum():
            raise TikTokValidationError("Hashtag contains invalid characters", field="hashtag", value=request.hashtag)
        
        logger.info(f"Starting hashtag analysis for: #{clean_hashtag}")
        pipeline_start_time = time.time()
        
        try:
            # Stage 1: Data Collection - Get hashtag videos
            logger.info("Stage 1: Collecting hashtag videos")
            videos_raw, videos_metadata = self._collect_hashtag_videos(
                hashtag=clean_hashtag,
                posts_count=request.max_posts
            )
            
            if not videos_raw:
                return self.response_builder.build_error_response(
                    f"No videos found for hashtag: {clean_hashtag}",
                    error_code="NO_VIDEOS_FOUND"
                )
            
            logger.info(f"Stage 1 complete: {len(videos_raw)} videos collected")
            
            # Stage 2: Data Cleaning - Clean video data
            logger.info("Stage 2: Cleaning video data")
            videos_cleaned, cleaning_metadata = self.data_cleaner.clean_hashtag_response({
                "status": "ok",
                "data": {"aweme_list": videos_raw}
            })
            
            if not videos_cleaned:
                return self.response_builder.build_error_response(
                    "No valid videos after cleaning",
                    error_code="NO_VALID_VIDEOS"
                )
            
            logger.info(f"Stage 2 complete: {len(videos_cleaned)} videos cleaned")
            
            # Stage 3a: Comment Collection
            logger.info("Stage 3a: Collecting comments from videos")
            comments_result = self.comment_collector.collect_all_comments(
                videos=videos_cleaned,
                max_comments_per_video=settings.DEFAULT_COMMENTS_PER_VIDEO
            )
            
            comments_by_video = comments_result["comments_by_video"]
            comments_metadata = comments_result["metadata"]
            
            # Check if we have any comments
            total_comments = sum(len(comments) for comments in comments_by_video.values())
            if total_comments == 0:
                return self.response_builder.build_error_response(
                    "No comments found for analysis",
                    error_code="NO_COMMENTS_FOUND"
                )
            
            logger.info(f"Stage 3a complete: {total_comments} comments collected")
            
            # Stage 3b: Comment Cleaning & Video-Comment Assembly
            logger.info("Stage 3b: Cleaning comment data")
            videos_with_comments = []
            total_cleaned_comments = 0
            
            # Create video-centric data structure
            for video in videos_cleaned:
                video_id = video.get("aweme_id")
                raw_comments = comments_by_video.get(video_id, [])
                
                # Clean comments for this video
                if raw_comments:
                    cleaned_comments, _ = self.data_cleaner.clean_comments_response(
                        {"status": "ok", "data": {"comments": raw_comments}},
                        video_id
                    )
                else:
                    cleaned_comments = []
                
                # Add to video-comments structure
                videos_with_comments.append({
                    "video_data": video,
                    "comments": cleaned_comments
                })
                
                total_cleaned_comments += len(cleaned_comments)
            
            if total_cleaned_comments == 0:
                return self.response_builder.build_error_response(
                    "No valid comments after cleaning",
                    error_code="NO_VALID_COMMENTS"
                )
            
            logger.info(f"Stage 3b complete: {total_cleaned_comments} comments cleaned")
            
            # Stage 3c: AI Analysis (Video-Centric with Concurrency)
            logger.info("Stage 3c: AI analysis of comments")
            
            # Use concurrent processing for multiple videos, sequential for single video
            if len(videos_with_comments) > 1:
                logger.info(f"Using concurrent processing for {len(videos_with_comments)} videos")
                analyzed_comments, analysis_metadata = await self.ai_analyzer.analyze_videos_with_comments_concurrent(
                    videos_with_comments=videos_with_comments,
                    ai_analysis_prompt=request.ai_analysis_prompt,
                    max_quote_length=request.max_quote_length
                )
            else:
                logger.info("Using sequential processing for single video")
                analyzed_comments, analysis_metadata = self.ai_analyzer.analyze_videos_with_comments(
                    videos_with_comments=videos_with_comments,
                    ai_analysis_prompt=request.ai_analysis_prompt,
                    max_quote_length=request.max_quote_length
                )
            
            if not analyzed_comments:
                return self.response_builder.build_error_response(
                    "No relevant comments found for analysis criteria",
                    error_code="NO_RELEVANT_COMMENTS"
                )
            
            logger.info(f"Stage 3c complete: {len(analyzed_comments)} comments analyzed")
            
            # Stage 4: Response Assembly
            logger.info("Stage 4: Building final response")
            
            # Calculate total pipeline time
            pipeline_end_time = time.time()
            total_pipeline_time = pipeline_end_time - pipeline_start_time
            
            processing_metadata = {
                "total_pipeline_time_seconds": round(total_pipeline_time, 2),
                "pipeline_stages_completed": 4
            }
            
            # Combine metadata from all stages
            unified_videos_metadata = {
                **videos_metadata,
                **cleaning_metadata
            }
            
            final_response = self.response_builder.build_analysis_response(
                analyzed_comments=analyzed_comments,
                hashtag=clean_hashtag,
                videos_metadata=unified_videos_metadata,
                comments_metadata=comments_metadata,
                analysis_metadata=analysis_metadata,
                processing_metadata=processing_metadata
            )
            
            logger.info(f"Hashtag analysis complete for #{clean_hashtag} in {total_pipeline_time:.2f}s")
            return final_response
            
        except TikTokValidationError as e:
            logger.warning(f"Validation error for hashtag analysis: {e.message}")
            return self.response_builder.build_error_response(
                f"Invalid request: {e.message}",
                error_code="VALIDATION_ERROR"
            )
            
        except TikTokDataCollectionError as e:
            logger.error(f"Data collection error: {e.message}")
            return self.response_builder.build_error_response(
                f"Failed to collect hashtag data: {e.message}",
                error_code="DATA_COLLECTION_ERROR"
            )
            
        except TikTokAnalysisError as e:
            logger.error(f"AI analysis error: {e.message}")
            return self.response_builder.build_error_response(
                f"Failed to analyze comments: {e.message}",
                error_code="ANALYSIS_ERROR"
            )
            
        except ConfigurationError as e:
            logger.error(f"Configuration error: {e.message}")
            return self.response_builder.build_error_response(
                "Service configuration error",
                error_code="CONFIGURATION_ERROR"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in hashtag analysis: {str(e)}")
            return self.response_builder.build_error_response(
                "An unexpected error occurred during analysis",
                error_code="INTERNAL_ERROR"
            )
    
    def _collect_hashtag_videos(self, hashtag: str, posts_count: int) -> tuple[list, dict]:
        """
        Collect videos for a hashtag using TikTok API.
        
        Args:
            hashtag: Hashtag to search (without # symbol)
            posts_count: Number of posts to collect
            
        Returns:
            Tuple of (videos_list, collection_metadata)
        """
        logger.info(f"Collecting {posts_count} videos for hashtag: {hashtag}")
        
        try:
            # Call TikTok API for hashtag challenge feed
            api_response = self.api_client.challenge_feed(hashtag)
            
            # Extract videos from response
            videos = api_response.get("data", {}).get("aweme_list", [])
            
            if not videos:
                logger.warning(f"No videos found in API response for hashtag: {hashtag}")
                return [], {"error": "no_videos_in_response"}
            
            # Limit to requested count
            limited_videos = videos[:posts_count]
            
            # Create collection metadata
            metadata = {
                "hashtag_requested": hashtag,
                "posts_requested": posts_count,
                "videos_found": len(videos),
                "videos_returned": len(limited_videos),
                "hashtag_api_calls": 1,
                "collection_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Successfully collected {len(limited_videos)} videos for hashtag: {hashtag}")
            return limited_videos, metadata
            
        except Exception as e:
            logger.error(f"Failed to collect hashtag videos: {e}")
            raise TikTokDataCollectionError(
                message=f"Failed to collect videos for hashtag: {hashtag}",
                api_endpoint="challenge_feed"
            )
    
    def health_check(self) -> Dict:
        """
        Perform health check of all service components.
        
        Returns:
            Health status dictionary
        """
        logger.info("Performing hashtag service health check")
        
        health_status = {
            "service": "TikTokHashtagService",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "api_client": "healthy" if self.api_client else "unhealthy",
                "data_cleaner": "healthy" if self.data_cleaner else "unhealthy",
                "comment_collector": "healthy" if self.comment_collector else "unhealthy",
                "ai_analyzer": "healthy" if self.ai_analyzer else "unhealthy",
                "response_builder": "healthy" if self.response_builder else "unhealthy"
            }
        }
        
        # Check if any components are unhealthy
        unhealthy_components = [
            name for name, status in health_status["components"].items() 
            if status == "unhealthy"
        ]
        
        if unhealthy_components:
            health_status["status"] = "unhealthy"
            health_status["issues"] = f"Unhealthy components: {', '.join(unhealthy_components)}"
        
        logger.info(f"Health check complete: {health_status['status']}")
        return health_status
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close API client."""
        try:
            if hasattr(self, 'api_client') and self.api_client:
                self.api_client.close()
        except Exception as e:
            logger.warning(f"Error closing API client: {e}")
        
        if exc_type:
            logger.error(f"Service exited with exception: {exc_type.__name__}: {exc_val}")
        
        logger.info("TikTok Hashtag Service closed")


# Convenience function for external usage
async def analyze_hashtag(request: TikTokHashtagAnalysisRequest) -> Dict:
    """
    Convenience function to analyze a hashtag.
    
    Args:
        request: Validated hashtag analysis request
        
    Returns:
        Complete analysis response dictionary
    """
    with TikTokHashtagService() as service:
        return await service.analyze_hashtag(request)
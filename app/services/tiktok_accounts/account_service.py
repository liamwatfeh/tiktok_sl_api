"""
TikTok Account Analysis Service
==============================

Main orchestration service for TikTok account analysis endpoint.
Coordinates all shared components to provide complete account analysis.

This service implements the 4-stage pipeline:
1. Data Collection: Get account videos from TikTok API
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
from app.models.tiktok_schemas import TikTokAccountAnalysisRequest
from app.services.tiktok_accounts.account_collector import AccountCollector
from app.services.tiktok_shared.tiktok_api_client import TikTokAPIClient
from app.services.tiktok_shared.tiktok_data_cleaners import TikTokDataCleaner
from app.services.tiktok_shared.tiktok_comment_collector import TikTokCommentCollector
from app.services.tiktok_shared.tiktok_ai_analyzer import TikTokAIAnalyzer
from app.services.tiktok_shared.tiktok_response_builder import TikTokResponseBuilder

logger = logging.getLogger(__name__)


class TikTokAccountService:
    """
    Main service for TikTok account analysis.
    
    Orchestrates the complete pipeline from account input to analyzed results.
    Uses all shared infrastructure components in sequence.
    """
    
    def __init__(self):
        """Initialize the account service with all required components."""
        # Validate critical configuration
        if not settings.TIKTOK_RAPIDAPI_KEY:
            raise ConfigurationError("TikTok API key not configured", config_key="TIKTOK_RAPIDAPI_KEY")
        if not settings.OPENAI_API_KEY:
            raise ConfigurationError("OpenAI API key not configured", config_key="OPENAI_API_KEY")
        
        # Initialize shared components
        try:
            self.api_client = TikTokAPIClient(settings.TIKTOK_RAPIDAPI_KEY)
            self.account_collector = AccountCollector(self.api_client)
            self.data_cleaner = TikTokDataCleaner()
            self.comment_collector = TikTokCommentCollector(self.api_client)
            self.ai_analyzer = TikTokAIAnalyzer()
            self.response_builder = TikTokResponseBuilder()
        except Exception as e:
            logger.error(f"Failed to initialize service components: {e}")
            raise ConfigurationError(f"Service initialization failed: {e}")
        
        logger.info("TikTok Account Service initialized with all components")
    
    async def analyze_account(self, request: TikTokAccountAnalysisRequest) -> Dict:
        """
        Perform complete account analysis.
        
        Args:
            request: Account analysis request with username, max_posts, max_comments_per_post
            
        Returns:
            Complete analysis response dictionary
        """
        # Basic security validation for internal use
        if not request.username or len(request.username.strip()) == 0:
            raise TikTokValidationError("Username cannot be empty", field="username")
        
        # Clean username (remove @ if present)
        clean_username = request.username.strip().lstrip('@')
        if not clean_username.replace('_', '').replace('.', '').isalnum():
            raise TikTokValidationError("Username contains invalid characters", field="username", value=request.username)
        
        logger.info(f"Starting account analysis for: @{clean_username}")
        pipeline_start_time = time.time()
        
        try:
            # Stage 1: Data Collection - Get account videos
            logger.info("Stage 1: Collecting account videos")
            videos_raw, videos_metadata = self.account_collector.collect_account_videos(
                username=clean_username,
                max_posts=request.max_posts
            )
            
            if not videos_raw:
                return self.response_builder.build_error_response(
                    f"No videos found for account: @{clean_username}",
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
                max_comments_per_video=request.max_comments_per_post
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
            
            # Stage 4: AI Analysis
            logger.info("Stage 4: AI analysis of videos and comments")
            
            # Use concurrent analysis if multiple videos, sequential if single video
            if len(videos_with_comments) > 1:
                analyzed_comments, ai_analysis_metadata = await self.ai_analyzer.analyze_videos_with_comments_concurrent(
                    videos_with_comments=videos_with_comments,
                    ai_analysis_prompt=request.ai_analysis_prompt
                )
            else:
                analyzed_comments, ai_analysis_metadata = self.ai_analyzer.analyze_videos_with_comments(
                    videos_with_comments=videos_with_comments,
                    ai_analysis_prompt=request.ai_analysis_prompt
                )
            
            if not analyzed_comments:
                return self.response_builder.build_error_response(
                    "AI analysis failed to return results",
                    error_code="AI_ANALYSIS_FAILED"
                )
            
            logger.info(f"Stage 4 complete: {len(analyzed_comments)} comments analyzed")
            
            # Stage 5: Response Assembly
            logger.info("Stage 5: Building unified response")
            
            total_pipeline_time = time.time() - pipeline_start_time
            
            # Prepare metadata for response building
            processing_metadata = {
                "pipeline_duration_seconds": round(total_pipeline_time, 2),
                "analysis_type": "account_analysis"
            }
            
            response = self.response_builder.build_analysis_response(
                analyzed_comments=analyzed_comments,
                hashtag=clean_username,  # Use username as the "hashtag" field for consistency
                videos_metadata={**videos_metadata, **cleaning_metadata},
                comments_metadata=comments_metadata,
                analysis_metadata=ai_analysis_metadata,
                processing_metadata=processing_metadata
            )
            
            logger.info(f"Account analysis complete for @{clean_username} in {total_pipeline_time:.2f}s")
            return response
            
        except TikTokValidationError:
            # Re-raise validation errors
            raise
        except TikTokDataCollectionError:
            # Re-raise data collection errors  
            raise
        except TikTokAnalysisError:
            # Re-raise analysis errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in account analysis: {e}")
            raise TikTokAnalysisError(
                message="Unexpected error during account analysis",
                model="unknown",
                analysis_type="account_analysis_pipeline"
            )
    
    def health_check(self) -> Dict:
        """
        Check the health of all service components.
        
        Returns:
            Health status dictionary
        """
        logger.info("Starting service health check")
        
        health_status = {
            "service": "TikTokAccountService",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {}
        }
        
        # Check each component
        components = [
            ("api_client", self.api_client),
            ("account_collector", self.account_collector),
            ("data_cleaner", self.data_cleaner),
            ("comment_collector", self.comment_collector),
            ("ai_analyzer", self.ai_analyzer),
            ("response_builder", self.response_builder)
        ]
        
        unhealthy_components = []
        
        for name, component in components:
            try:
                # Basic health check - verify component exists and is initialized
                if component is None:
                    health_status["components"][name] = "missing"
                    unhealthy_components.append(name)
                else:
                    health_status["components"][name] = "healthy"
            except Exception as e:
                health_status["components"][name] = f"error: {e}"
                unhealthy_components.append(name)
        
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
        
        logger.info("TikTok Account Service closed")


# Convenience function for external usage
async def analyze_account(request: TikTokAccountAnalysisRequest) -> Dict:
    """
    Convenience function to analyze an account.
    
    Args:
        request: Account analysis request
        
    Returns:
        Complete analysis response dictionary
    """
    with TikTokAccountService() as service:
        return await service.analyze_account(request)
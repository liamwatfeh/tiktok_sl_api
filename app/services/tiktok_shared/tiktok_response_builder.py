"""
TikTok Response Builder
=======================

Shared response assembly component for TikTok analysis endpoints.
Combines analyzed comments, metadata, and statistics into unified API responses.

This module provides:
- Standardized response format across all endpoints
- Comment analysis aggregation and statistics
- Metadata collection and normalization
- Response validation and error handling
- Threading analysis for comment relationships
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from statistics import mean, median
from collections import Counter

logger = logging.getLogger(__name__)


class TikTokResponseBuilder:
    """
    Builds unified API responses for TikTok analysis endpoints.
    
    This builder combines analyzed comments, video metadata, and processing
    statistics into the standardized response format used by all endpoints.
    """
    
    def __init__(self):
        """Initialize the response builder."""
        logger.info("TikTok Response Builder initialized")
    
    def build_analysis_response(
        self,
        analyzed_comments: List[Dict],
        hashtag: str,
        videos_metadata: Dict,
        comments_metadata: Dict,
        analysis_metadata: Dict,
        processing_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Build the complete analysis response.
        
        Args:
            analyzed_comments: List of AI-analyzed comment dictionaries
            hashtag: Hashtag that was analyzed
            videos_metadata: Metadata from video collection/cleaning
            comments_metadata: Metadata from comment collection
            analysis_metadata: Metadata from AI analysis
            processing_metadata: Optional additional processing info
            
        Returns:
            Complete API response dictionary
        """
        logger.info(f"Building analysis response for hashtag: {hashtag}")
        logger.info(f"Processing {len(analyzed_comments)} analyzed comments")
        
        try:
            # Calculate aggregated statistics
            stats = self._calculate_analysis_statistics(analyzed_comments)
            
            # Calculate threading statistics
            threading_stats = self._calculate_threading_statistics(analyzed_comments)
            
            # Calculate video engagement metrics
            engagement_stats = self._calculate_engagement_statistics(videos_metadata)
            
            # Build comprehensive metadata
            unified_metadata = self._build_unified_metadata(
                hashtag=hashtag,
                analyzed_comments=analyzed_comments,
                videos_metadata=videos_metadata,
                comments_metadata=comments_metadata,
                analysis_metadata=analysis_metadata,
                processing_metadata=processing_metadata,
                analysis_stats=stats,
                threading_stats=threading_stats,
                engagement_stats=engagement_stats
            )
            
            # Prepare final comment analyses for response
            formatted_comments = self._format_comment_analyses(analyzed_comments)
            
            # Build final response
            response = {
                "comment_analyses": formatted_comments,
                "metadata": unified_metadata
            }
            
            logger.info(f"Response built successfully: {len(formatted_comments)} comments, metadata complete")
            return response
            
        except Exception as e:
            logger.error(f"Failed to build analysis response: {e}")
            # Return error response
            return {
                "error": {
                    "message": "Failed to build analysis response",
                    "details": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
    
    def _calculate_analysis_statistics(self, analyzed_comments: List[Dict]) -> Dict:
        """Calculate statistics from analyzed comments."""
        if not analyzed_comments:
            return {
                "sentiment_distribution": {},
                "purchase_intent_distribution": {},
                "average_confidence": 0.0,
                "top_themes": [],
                "engagement_metrics": {}
            }
        
        # Sentiment distribution
        sentiments = [comment.get("sentiment", "neutral") for comment in analyzed_comments]
        sentiment_counts = Counter(sentiments)
        sentiment_distribution = {
            sentiment: count for sentiment, count in sentiment_counts.items()
        }
        
        # Purchase intent distribution
        purchase_intents = [comment.get("purchase_intent", "none") for comment in analyzed_comments]
        intent_counts = Counter(purchase_intents)
        intent_distribution = {
            intent: count for intent, count in intent_counts.items()
        }
        
        # Average confidence score
        confidence_scores = [
            comment.get("confidence_score", 0.0) 
            for comment in analyzed_comments 
            if comment.get("confidence_score") is not None
        ]
        avg_confidence = mean(confidence_scores) if confidence_scores else 0.0
        
        # Top themes
        themes = [comment.get("theme", "") for comment in analyzed_comments if comment.get("theme")]
        theme_counts = Counter(themes)
        top_themes = [
            {"theme": theme, "count": count} 
            for theme, count in theme_counts.most_common(10)
        ]
        
        # Engagement metrics (likes on analyzed comments)
        comment_likes = [comment.get("likes", 0) for comment in analyzed_comments]
        engagement_metrics = {
            "total_likes_on_analyzed_comments": sum(comment_likes),
            "average_likes_per_comment": mean(comment_likes) if comment_likes else 0.0,
            "median_likes_per_comment": median(comment_likes) if comment_likes else 0.0,
            "max_likes_single_comment": max(comment_likes) if comment_likes else 0
        }
        
        return {
            "sentiment_distribution": sentiment_distribution,
            "purchase_intent_distribution": intent_distribution,
            "average_confidence": round(avg_confidence, 3),
            "top_themes": top_themes,
            "engagement_metrics": engagement_metrics
        }
    
    def _calculate_threading_statistics(self, analyzed_comments: List[Dict]) -> Dict:
        """Calculate comment threading statistics."""
        if not analyzed_comments:
            return {
                "total_threaded_comments": 0,
                "top_level_comments": 0,
                "reply_comments": 0,
                "max_reply_depth": 0
            }
        
        # Count reply vs top-level comments
        reply_comments = sum(1 for comment in analyzed_comments if comment.get("is_reply", False))
        top_level_comments = len(analyzed_comments) - reply_comments
        
        return {
            "total_threaded_comments": len(analyzed_comments),
            "top_level_comments": top_level_comments,
            "reply_comments": reply_comments,
            "max_reply_depth": 1 if reply_comments > 0 else 0  # Simplified for now
        }
    
    def _calculate_engagement_statistics(self, videos_metadata: Dict) -> Dict:
        """Calculate video engagement statistics."""
        if not videos_metadata or "videos_cleaned" not in videos_metadata:
            return {
                "total_video_plays": 0,
                "total_video_likes": 0,
                "average_engagement_rate": 0.0
            }
        
        videos_cleaned = videos_metadata.get("videos_cleaned", 0)
        
        # These would be calculated from actual video data if available
        # For now, return placeholder structure
        return {
            "total_video_plays": 0,
            "total_video_likes": 0,
            "average_engagement_rate": 0.0,
            "videos_analyzed": videos_cleaned
        }
    
    def _build_unified_metadata(
        self,
        hashtag: str,
        analyzed_comments: List[Dict],
        videos_metadata: Dict,
        comments_metadata: Dict,
        analysis_metadata: Dict,
        processing_metadata: Optional[Dict],
        analysis_stats: Dict,
        threading_stats: Dict,
        engagement_stats: Dict
    ) -> Dict:
        """Build unified metadata from all processing stages."""
        
        # Calculate processing time
        total_processing_time = 0.0
        if analysis_metadata.get("processing_time_seconds"):
            total_processing_time += analysis_metadata["processing_time_seconds"]
        
        # Calculate API call counts
        hashtag_api_calls = videos_metadata.get("hashtag_api_calls", 1)  # At least 1 for hashtag call
        comments_api_calls = comments_metadata.get("comments_api_calls", 0)
        
        # Add AI analysis API calls (video-centric: 1 call per video)
        ai_analysis_calls = analysis_metadata.get("total_api_calls", 0)
        
        total_api_calls = hashtag_api_calls + comments_api_calls + ai_analysis_calls
        
        # Build comprehensive metadata
        metadata = {
            # Standard analysis metadata
            "total_videos_analyzed": videos_metadata.get("videos_cleaned", 0),
            "total_comments_found": comments_metadata.get("total_comments_collected", 0),
            "relevant_comments_extracted": len(analyzed_comments),
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "processing_time_seconds": round(total_processing_time, 2),
            "model_used": analysis_metadata.get("model_used", "unknown"),
            
            # TikTok-specific metadata (adjusted for single hashtag)
            "hashtag_analyzed": hashtag,
            "total_video_plays": engagement_stats.get("total_video_plays", 0),
            "total_video_likes": engagement_stats.get("total_video_likes", 0),
            "average_engagement_rate": engagement_stats.get("average_engagement_rate", 0.0),
            "hashtag_api_calls": hashtag_api_calls,
            "comments_api_calls": comments_api_calls,
            
            # Threading metadata
            "max_reply_depth": threading_stats.get("max_reply_depth", 0),
            "total_threaded_comments": threading_stats.get("total_threaded_comments", 0),
            "top_level_comments": threading_stats.get("top_level_comments", 0),
            "reply_comments": threading_stats.get("reply_comments", 0),
            
            # Analysis statistics
            "sentiment_distribution": analysis_stats.get("sentiment_distribution", {}),
            "purchase_intent_distribution": analysis_stats.get("purchase_intent_distribution", {}),
            "average_confidence_score": analysis_stats.get("average_confidence", 0.0),
            "top_themes": analysis_stats.get("top_themes", []),
            
            # Processing metadata
            "total_api_calls": total_api_calls,
            "ai_analysis_api_calls": ai_analysis_calls,
            "successful_analyses": analysis_metadata.get("successful_analyses", 0),
            "failed_analyses": analysis_metadata.get("failed_analyses", 0),
            "ai_analysis_prompt": analysis_metadata.get("ai_analysis_prompt", ""),
            
            # Additional context
            "endpoint_type": "hashtag_analysis",
            "api_version": "1.0.0"
        }
        
        return metadata
    
    def _format_comment_analyses(self, analyzed_comments: List[Dict]) -> List[Dict]:
        """Format analyzed comments for final response."""
        formatted_comments = []
        
        for comment in analyzed_comments:
            try:
                formatted_comment = {
                    "quote": comment.get("quote", ""),
                    "sentiment": comment.get("sentiment", "neutral"),
                    "theme": comment.get("theme", ""),
                    "purchase_intent": comment.get("purchase_intent", "none"),
                    "confidence_score": comment.get("confidence_score", 0.0)
                }
                
                formatted_comments.append(formatted_comment)
                
            except Exception as e:
                logger.warning(f"Failed to format comment: {e}")
                continue
        
        return formatted_comments
    
    def build_error_response(
        self, 
        error_message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> Dict:
        """
        Build standardized error response.
        
        Args:
            error_message: Human-readable error message
            error_code: Optional error code
            details: Optional error details
            
        Returns:
            Standardized error response
        """
        error_response = {
            "error": {
                "message": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "endpoint_type": "hashtag_analysis"
            }
        }
        
        if error_code:
            error_response["error"]["code"] = error_code
        
        if details:
            error_response["error"]["details"] = details
        
        logger.error(f"Built error response: {error_message}")
        return error_response


# Convenience function for external usage
def build_analysis_response(
    analyzed_comments: List[Dict],
    hashtag: str,
    videos_metadata: Dict,
    comments_metadata: Dict,
    analysis_metadata: Dict,
    processing_metadata: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to build analysis response.
    
    Args:
        analyzed_comments: List of AI-analyzed comments
        hashtag: Hashtag analyzed
        videos_metadata: Video collection metadata
        comments_metadata: Comment collection metadata  
        analysis_metadata: AI analysis metadata
        processing_metadata: Optional processing metadata
        
    Returns:
        Complete API response dictionary
    """
    builder = TikTokResponseBuilder()
    return builder.build_analysis_response(
        analyzed_comments,
        hashtag,
        videos_metadata,
        comments_metadata,
        analysis_metadata,
        processing_metadata
    )
"""
TikTok AI Analyzer
==================

Shared AI analysis component for TikTok comments using OpenAI's native structured outputs.
Processes comments with user-provided analysis prompts and returns structured results.

This module provides:
- OpenAI GPT-4 integration with structured outputs
- Custom prompt processing for flexible analysis criteria
- Batch comment analysis with rate limiting
- Error handling and retry logic
- Analysis result validation
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

import openai
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings
from app.core.exceptions import TikTokAnalysisError
from app.models.tiktok_schemas import TikTokCommentAnalysis

logger = logging.getLogger(__name__)


class TikTokAIAnalyzer:
    """
    AI analysis component for TikTok comments using OpenAI structured outputs.
    
    This analyzer processes comments with user-provided analysis criteria and returns
    structured results using OpenAI's native structured output capabilities.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the AI analyzer.
        
        Args:
            openai_api_key: OpenAI API key (defaults to settings)
            model: Model to use (defaults to settings)
        """
        self.api_key = openai_api_key or settings.OPENAI_API_KEY
        self.model = model or settings.DEFAULT_MODEL
        self.max_concurrent = getattr(settings, 'MAX_CONCURRENT_AGENTS', 3)  # Default to 3 concurrent
        self.request_delay = 0.2  # 200ms between requests for rate limiting
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Create semaphore for concurrent processing
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        logger.info(f"TikTok AI Analyzer initialized with model: {self.model}, max_concurrent: {self.max_concurrent}")
    
    def analyze_videos_with_comments(
        self,
        videos_with_comments: List[Dict],
        ai_analysis_prompt: str,
        max_quote_length: int = 200
    ) -> Tuple[List[Dict], Dict]:
        """
        Analyze multiple videos with their comments using video-centric approach.
        Each video + its comments processed in one API call for full context.
        
        Args:
            videos_with_comments: List of {video_data, comments} dictionaries
            ai_analysis_prompt: User-provided analysis criteria
            max_quote_length: Maximum length for extracted quotes
            
        Returns:
            Tuple of (analyzed_comments_list, analysis_metadata)
        """
        logger.info(f"Starting video-centric analysis of {len(videos_with_comments)} videos")
        start_time = time.time()
        
        try:
            if not videos_with_comments:
                logger.warning("No videos provided for analysis")
                return [], {"error": "no_videos"}
            
            analyzed_comments = []
            total_api_calls = 0
            successful_analyses = 0
            failed_analyses = 0
            
            # Process each video + comments in one API call
            for i, video_data in enumerate(videos_with_comments):
                logger.debug(f"Processing video {i+1}/{len(videos_with_comments)}: {video_data.get('video_id', 'unknown')}")
                
                try:
                    # Add rate limiting between videos
                    if total_api_calls > 0:
                        time.sleep(self.request_delay)
                    
                    video_results = self._analyze_video_with_comments(
                        video_data.get('video_data', {}),
                        video_data.get('comments', []), 
                        ai_analysis_prompt, 
                        max_quote_length
                    )
                    
                    analyzed_comments.extend(video_results)
                    successful_analyses += len(video_results)
                    total_api_calls += 1
                    
                    logger.debug(f"Video {i+1} completed: {len(video_results)} analyses")
                    
                except Exception as e:
                    logger.error(f"Failed to analyze video {i+1}: {e}")
                    failed_analyses += len(video_data.get('comments', []))
                    continue
            
            # Create analysis metadata
            end_time = time.time()
            processing_time = end_time - start_time
            total_comments = sum(len(v.get('comments', [])) for v in videos_with_comments)
            
            metadata = {
                "total_videos": len(videos_with_comments),
                "total_comments": total_comments,
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "total_api_calls": total_api_calls,
                "processing_time_seconds": round(processing_time, 2),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "model_used": self.model,
                "ai_analysis_prompt": ai_analysis_prompt,
                "max_quote_length": max_quote_length
            }
            
            logger.info(f"Video-centric analysis complete: {successful_analyses}/{total_comments} comments analyzed from {len(videos_with_comments)} videos in {processing_time:.2f}s")
            return analyzed_comments, metadata
            
        except Exception as e:
            logger.error(f"Critical error in video-centric analysis: {e}")
            raise TikTokAnalysisError(
                message="Failed to complete video-centric comment analysis",
                model_used=self.model,
                analysis_step="video_processing"
            )

    async def analyze_videos_with_comments_concurrent(
        self,
        videos_with_comments: List[Dict],
        ai_analysis_prompt: str,
        max_quote_length: int = 200
    ) -> Tuple[List[Dict], Dict]:
        """
        Analyze multiple videos with their comments using concurrent processing.
        Each video + its comments processed in parallel with rate limiting.
        
        Args:
            videos_with_comments: List of {video_data, comments} dictionaries
            ai_analysis_prompt: User-provided analysis criteria
            max_quote_length: Maximum length for extracted quotes
            
        Returns:
            Tuple of (analyzed_comments_list, analysis_metadata)
        """
        logger.info(f"Starting concurrent video-centric analysis of {len(videos_with_comments)} videos with {self.max_concurrent} agents")
        start_time = time.time()
        
        try:
            if not videos_with_comments:
                logger.warning("No videos provided for analysis")
                return [], {"error": "no_videos"}

            # Process videos concurrently using asyncio.gather
            tasks = []
            for i, video_data in enumerate(videos_with_comments):
                task = self._analyze_video_with_comments_async(
                    video_data.get('video_data', {}),
                    video_data.get('comments', []),
                    ai_analysis_prompt,
                    max_quote_length,
                    video_index=i
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and separate successful from failed
            analyzed_comments = []
            successful_analyses = 0
            failed_analyses = 0
            total_api_calls = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Video {i+1} failed: {result}")
                    failed_analyses += len(videos_with_comments[i].get('comments', []))
                else:
                    analyzed_comments.extend(result)
                    successful_analyses += len(result)
                    total_api_calls += 1
            
            # Create analysis metadata
            end_time = time.time()
            processing_time = end_time - start_time
            total_comments = sum(len(v.get('comments', [])) for v in videos_with_comments)
            
            metadata = {
                "total_videos": len(videos_with_comments),
                "total_comments": total_comments,
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "total_api_calls": total_api_calls,
                "processing_time_seconds": round(processing_time, 2),
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "model_used": self.model,
                "ai_analysis_prompt": ai_analysis_prompt,
                "max_quote_length": max_quote_length,
                "concurrent_agents": self.max_concurrent
            }
            
            logger.info(f"Concurrent video-centric analysis complete: {successful_analyses}/{total_comments} comments analyzed from {len(videos_with_comments)} videos in {processing_time:.2f}s")
            
            return analyzed_comments, metadata
            
        except Exception as e:
            logger.error(f"Unexpected error in concurrent video analysis processing: {e}")
            raise TikTokAnalysisError(
                message="Failed to complete concurrent video-centric comment analysis",
                model_used=self.model,
                analysis_step="concurrent_video_processing"
            )

    async def _analyze_video_with_comments_async(
        self,
        video_data: Dict,
        comments: List[Dict],
        ai_analysis_prompt: str,
        max_quote_length: int = 200,
        video_index: int = 0
    ) -> List[Dict]:
        """
        Async version of _analyze_video_with_comments with rate limiting.
        
        Args:
            video_data: Video metadata and content
            comments: List of comment dictionaries for this video
            ai_analysis_prompt: User-provided analysis criteria
            max_quote_length: Maximum length for extracted quotes
            video_index: Index of this video for logging
            
        Returns:
            List of analyzed comment/video content dictionaries
        """
        async with self.semaphore:  # Rate limiting with semaphore
            try:
                # Add staggered delay to prevent overwhelming OpenAI API
                await asyncio.sleep(self.request_delay * (video_index % self.max_concurrent))
                
                # Run the synchronous OpenAI call in a thread pool
                loop = asyncio.get_event_loop()
                from concurrent.futures import ThreadPoolExecutor
                with ThreadPoolExecutor() as executor:
                    result = await loop.run_in_executor(
                        executor,
                        self._analyze_video_with_comments,
                        video_data,
                        comments,
                        ai_analysis_prompt,
                        max_quote_length
                    )
                
                logger.debug(f"Video {video_index + 1} analysis completed: {len(result)} analyses")
                return result
                
            except Exception as e:
                logger.error(f"Failed to analyze video {video_index + 1} concurrently: {e}")
                raise
    
    def analyze_comments_batch(
        self, 
        comments: List[Dict], 
        ai_analysis_prompt: str,
        max_quote_length: int = 200
    ) -> Tuple[List[Dict], Dict]:
        """
        DEPRECATED: Legacy method for backward compatibility.
        This method is kept for compatibility but now groups comments by video
        and uses the new video-centric analysis approach.
        
        Args:
            comments: List of cleaned comment dictionaries
            ai_analysis_prompt: User-provided analysis criteria
            max_quote_length: Maximum length for extracted quotes
            
        Returns:
            Tuple of (analyzed_comments_list, analysis_metadata)
        """
        logger.warning("Using deprecated analyze_comments_batch method. Consider upgrading to analyze_videos_with_comments.")
        
        # Group comments by video_id for video-centric processing
        videos_with_comments = []
        comments_by_video = {}
        
        # Group comments by video
        for comment in comments:
            video_id = comment.get("aweme_id", "unknown")
            if video_id not in comments_by_video:
                comments_by_video[video_id] = []
            comments_by_video[video_id].append(comment)
        
        # Create video_data structure for each video
        for video_id, video_comments in comments_by_video.items():
            # Create minimal video_data from first comment
            first_comment = video_comments[0] if video_comments else {}
            video_data = {
                "post_id": video_id,
                "post_title": f"TikTok Video {video_id}",
                "post_content": "",  # No video content available in legacy mode
                "post_author": "Unknown",
                "post_score": 0,
                "play_count": 0,
                "share_count": 0
            }
            
            videos_with_comments.append({
                "video_data": video_data,
                "comments": video_comments
            })
        
        # Use new video-centric analysis
        return self.analyze_videos_with_comments(
            videos_with_comments,
            ai_analysis_prompt,
            max_quote_length
        )
    
    def _analyze_video_with_comments(
        self,
        video_data: Dict,
        comments: List[Dict], 
        ai_analysis_prompt: str,
        max_quote_length: int
    ) -> List[Dict]:
        """
        Analyze a single video with all its comments using OpenAI structured outputs.
        Video content (title/caption) included as potential quote source.
        
        Args:
            video_data: Video metadata (title, caption, engagement, etc.)
            comments: List of comment dictionaries for this video
            ai_analysis_prompt: Analysis criteria from user
            max_quote_length: Maximum quote length
            
        Returns:
            List of analyzed comment/video content dictionaries
        """
        try:
            # Prepare video content for analysis (map TikTok fields to expected format)
            video_stats = video_data.get("statistics", {})
            video_author = video_data.get("author", {})
            
            video_content = {
                "video_id": video_data.get("aweme_id", ""),
                "title": video_data.get("desc", ""),  # TikTok videos don't have separate titles
                "caption": video_data.get("desc", ""),  # Video description/caption
                "author": video_author.get("nickname", "") if isinstance(video_author, dict) else str(video_author),
                "likes": video_stats.get("digg_count", 0),
                "plays": video_stats.get("play_count", 0), 
                "shares": video_stats.get("share_count", 0)
            }
            
            # Prepare comment texts for analysis
            comment_texts = []
            for comment in comments:
                text = comment.get("text", "").strip()
                if text:
                    comment_texts.append({
                        "comment_id": comment.get("cid", ""),
                        "text": text,
                        "author": comment.get("user", {}).get("nickname", ""),
                        "likes": comment.get("digg_count", 0)
                    })
            
            if not comment_texts and not video_content.get("caption"):
                logger.debug("No valid content (video or comments) to analyze")
                return []
            
            # Build analysis prompt with video context
            system_prompt = self._build_system_prompt(ai_analysis_prompt, max_quote_length)
            user_prompt = self._build_video_analysis_prompt(video_content, comment_texts)
            
            # Call OpenAI with structured outputs
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=TikTokCommentAnalysisBatch,
                temperature=0.1,
                max_tokens=4000
            )
            
            # Extract structured results
            parsed_response = response.choices[0].message.parsed
            if not parsed_response or not parsed_response.analyses:
                logger.warning("OpenAI returned empty or invalid analysis")
                return []
            
                        # Convert to our expected format
            analyzed_comments = []
            for analysis in parsed_response.analyses:
                try:
                    # Determine if quote is from video or comment
                    matching_comment = None
                    is_video_content = False
                    
                    # First check if quote matches video content
                    video_caption = video_content.get("caption", "").strip()
                    if video_caption and analysis.quote.strip() in video_caption:
                        is_video_content = True
                    else:
                        # Find matching comment
                        for comment in comments:
                            if comment.get("text", "").strip() == analysis.quote.strip():
                                matching_comment = comment
                                break
                    
                    analyzed_comment = {
                        "quote": analysis.quote[:max_quote_length],
                        "sentiment": analysis.sentiment.lower(),
                        "theme": analysis.theme,
                        "purchase_intent": analysis.purchase_intent.lower(),
                        "confidence_score": analysis.confidence_score,
                        
                        # Source identification
                        "source_type": "video" if is_video_content else "comment",
                        
                        # Add metadata based on source
                        "comment_id": matching_comment.get("cid", "") if matching_comment else "",
                        "video_id": video_content.get("video_id", ""),
                        "author": matching_comment.get("user", {}).get("nickname", "") if matching_comment else video_content.get("author", ""),
                        "likes": matching_comment.get("digg_count", 0) if matching_comment else video_content.get("likes", 0),
                        "is_reply": matching_comment.get("is_reply", False) if matching_comment else False
                    }
                    
                    analyzed_comments.append(analyzed_comment)
                    
                except Exception as e:
                    logger.debug(f"Failed to process individual analysis: {e}")
                    continue
            
            logger.debug(f"Successfully analyzed {len(analyzed_comments)} items from video {video_content.get('video_id', 'unknown')}")
            return analyzed_comments
            
        except openai.RateLimitError:
            logger.warning("OpenAI rate limit hit - waiting before retry")
            time.sleep(1.0)
            raise TikTokAnalysisError(
                message="OpenAI rate limit exceeded",
                model_used=self.model,
                analysis_step="api_call"
            )
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise TikTokAnalysisError(
                message=f"OpenAI API error: {str(e)}",
                model_used=self.model,
                analysis_step="api_call"
            )
        except Exception as e:
            logger.error(f"Unexpected error in video analysis: {e}")
            raise TikTokAnalysisError(
                message="Failed to analyze video with comments",
                model_used=self.model,
                analysis_step="video_analysis"
            )
    
    def _build_system_prompt(self, ai_analysis_prompt: str, max_quote_length: int) -> str:
        """Build the system prompt for OpenAI analysis with video context."""
        return f"""You are a professional social media analyst specializing in TikTok content analysis. 

ANALYSIS CRITERIA:
{ai_analysis_prompt}

CONTENT SOURCES FOR ANALYSIS:
- Video Caption/Title: May contain creator's message, product mentions, or key themes
- User Comments: Community reactions, opinions, experiences, and discussions

INSTRUCTIONS:
- Analyze both video content and comments according to the criteria above
- Extract the most relevant quotes (max {max_quote_length} characters) from ANY source
- Video captions can be as valuable as comments for insights
- Determine sentiment: positive, negative, or neutral
- Identify the main theme/topic discussed
- Assess purchase intent: high, medium, low, or none
- Provide confidence score (0.0-1.0) for your analysis

QUOTE EXTRACTION PRIORITY:
1. Content that directly relates to the analysis criteria
2. Insights about user experiences, opinions, or intentions
3. Product mentions, brand discussions, or purchase signals
4. Most meaningful content regardless of whether it's from video or comments

IMPORTANT:
- Only analyze content that relates to the analysis criteria
- If content is irrelevant, skip it
- Be objective and consistent in your analysis
- Video captions and comments are equally valid sources for insights"""
    
    def _build_video_analysis_prompt(self, video_content: Dict, comment_texts: List[Dict]) -> str:
        """Build the user prompt with video and comment data."""
        prompt = "Analyze this TikTok video and its community discussion:\n\n"
        
        # Add video information
        prompt += "VIDEO CONTENT:\n"
        prompt += f"Video ID: {video_content.get('video_id', 'Unknown')}\n"
        prompt += f"Title: {video_content.get('title', 'No title')}\n"
        prompt += f"Caption: {video_content.get('caption', 'No caption')}\n"
        prompt += f"Creator: @{video_content.get('author', 'Unknown')}\n"
        prompt += f"Engagement: {video_content.get('likes', 0):,} likes, {video_content.get('plays', 0):,} plays, {video_content.get('shares', 0):,} shares\n\n"
        
        # Add comments
        if comment_texts:
            prompt += "COMMUNITY COMMENTS:\n"
            for i, comment in enumerate(comment_texts, 1):
                prompt += f"Comment {i}:\n"
                prompt += f"User: @{comment['author']}\n"
                prompt += f"Text: {comment['text']}\n"
                prompt += f"Likes: {comment['likes']:,}\n\n"
        else:
            prompt += "COMMUNITY COMMENTS: No comments available\n\n"
        
        prompt += "Please analyze both the video content and comments according to your instructions. Extract relevant insights from any source."
        return prompt


class TikTokCommentAnalysisBatch(BaseModel):
    """Pydantic model for OpenAI structured output - batch of comment analyses."""
    
    analyses: List[TikTokCommentAnalysis] = Field(
        ..., 
        description="List of analyzed comments matching the criteria"
    )


# Convenience function for external usage
def analyze_comments_batch(
    comments: List[Dict], 
    ai_analysis_prompt: str,
    max_quote_length: int = 200,
    openai_api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Tuple[List[Dict], Dict]:
    """
    Convenience function to analyze TikTok comments batch.
    
    Args:
        comments: List of cleaned comment dictionaries
        ai_analysis_prompt: User-provided analysis criteria
        max_quote_length: Maximum length for quotes
        openai_api_key: OpenAI API key (optional)
        model: Model to use (optional)
        
    Returns:
        Tuple of (analyzed_comments, metadata)
    """
    analyzer = TikTokAIAnalyzer(openai_api_key, model)
    return analyzer.analyze_comments_batch(comments, ai_analysis_prompt, max_quote_length)
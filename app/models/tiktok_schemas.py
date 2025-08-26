"""TikTok data models and schemas

This file contains Pydantic models for:
- Request schemas (TikTokHashtagAnalysisRequest, etc.)
- Response schemas (TikTokCommentAnalysis, TikTokAnalysisMetadata, etc.)
- Internal schemas (TikTokVideo, TikTokComment, PostWithComments, etc.)
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class TikTokHashtagAnalysisRequest(BaseModel):
    """Request schema for TikTok hashtag analysis (single hashtag per request)"""
    
    # Hashtag parameters  
    hashtag: str = Field(
        ..., 
        min_length=1,
        max_length=100,
        description="Hashtag to search (without # symbol)",
        example="bmwmotorrad"
    )
    posts_count: int = Field(
        default=20, 
        ge=1, 
        le=50,
        description="Number of posts to analyze for this hashtag"
    )
    
    # AI Analysis parameters
    ai_analysis_prompt: str = Field(
        ..., 
        min_length=10,
        max_length=1000,
        description="Custom AI analysis criteria for content evaluation",
        example="Analyze motorcycle discussions for sentiment about BMW motorcycles, purchase intent, and user experiences"
    )
    
    # Model configuration
    model: str = Field(
        default="gpt-4.1-2025-04-14",
        description="AI model to use for analysis"
    )
    
    # Output configuration
    max_quote_length: int = Field(
        default=200,
        ge=50,
        le=500,
        description="Maximum length of extracted quotes"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "hashtag": "bmwmotorrad",
                "posts_count": 25,
                "ai_analysis_prompt": "Analyze motorcycle discussions for sentiment about BMW motorcycles, purchase intent, and user experiences. Focus on comments expressing opinions about BMW bikes, pricing, or buying decisions.",
                "model": "gpt-4.1-2025-04-14",
                "max_quote_length": 200
            }
        }

# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class TikTokCommentAnalysis(BaseModel):
    """Individual TikTok comment analysis result"""
    
    # Core analysis fields
    video_id: str = Field(..., description="TikTok video ID (aweme_id)")
    video_url: Optional[str] = Field(None, description="TikTok video URL")
    quote: str = Field(..., description="Extracted comment text")
    sentiment: str = Field(..., description="positive/negative/neutral")
    theme: str = Field(..., description="Topic category")
    purchase_intent: str = Field(..., description="high/medium/low/none")
    date: str = Field(..., description="Comment date in ISO format")
    source: str = Field(default="tiktok", description="Data source")
    
    # Enhanced context fields
    conversation_context: str = Field(..., description="What this comment responds to")
    thread_context: str = Field(..., description="Broader discussion context")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence level")
    
    # TikTok-specific fields
    hashtag_source: str = Field(..., description="Which hashtag found this content")
    video_play_count: int = Field(default=0, description="Video play count")
    video_like_count: int = Field(default=0, description="Video like count")
    comment_like_count: int = Field(default=0, description="Comment like count")
    
    # Thread structure fields
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID if reply")
    thread_depth: int = Field(default=0, description="Reply depth level")
    is_reply: bool = Field(default=False, description="Whether this is a reply")

class TikTokAnalysisMetadata(BaseModel):
    """TikTok analysis metadata"""
    
    # Standard analysis metadata
    total_videos_analyzed: int = Field(..., description="Number of videos processed")
    total_comments_found: int = Field(..., description="Total comments collected")
    relevant_comments_extracted: int = Field(..., description="Comments matching criteria")
    analysis_timestamp: str = Field(..., description="When analysis completed")
    processing_time_seconds: float = Field(..., description="Total processing time")
    model_used: str = Field(..., description="AI model used")
    
    # TikTok-specific metadata (adjusted for single hashtag)
    hashtag_analyzed: str = Field(..., description="Hashtag processed")
    total_video_plays: int = Field(default=0, description="Sum of all video plays")
    total_video_likes: int = Field(default=0, description="Sum of all video likes")
    average_engagement_rate: float = Field(default=0.0, description="Average engagement percentage")
    hashtag_api_calls: int = Field(default=0, description="API calls for hashtag data")
    comments_api_calls: int = Field(default=0, description="API calls for comment data")
    
    # Threading metadata
    max_reply_depth: int = Field(default=0, description="Deepest reply thread found")
    total_threaded_comments: int = Field(default=0, description="Total comments with threading")
    top_level_comments: int = Field(default=0, description="Non-reply comments")
    reply_comments: int = Field(default=0, description="Reply comments")

class TikTokUnifiedAnalysisResponse(BaseModel):
    """Final TikTok analysis response"""
    comment_analyses: List[TikTokCommentAnalysis] = Field(..., description="List of analyzed comments")
    metadata: TikTokAnalysisMetadata = Field(..., description="Analysis metadata")

# =============================================================================
# INTERNAL SCHEMAS (TikTok API Responses)
# =============================================================================

class TikTokVideoAuthor(BaseModel):
    """TikTok video author information"""
    uid: str
    nickname: str
    unique_id: str
    avatar_thumb: Optional[dict] = None
    region: Optional[str] = None

class TikTokVideoStatistics(BaseModel):
    """TikTok video statistics"""
    digg_count: int = 0  # likes
    comment_count: int = 0
    play_count: int = 0
    share_count: int = 0

class TikTokHashtagInfo(BaseModel):
    """TikTok hashtag information"""
    cha_name: str
    type: int

class TikTokVideo(BaseModel):
    """TikTok video data structure"""
    aweme_id: str
    desc: str  # video caption
    create_time: int  # timestamp
    author: TikTokVideoAuthor
    statistics: TikTokVideoStatistics
    cha_list: List[TikTokHashtagInfo] = []
    share_url: Optional[str] = None
    video: Optional[dict] = None  # video metadata

class TikTokCommentUser(BaseModel):
    """TikTok comment user information"""
    uid: str
    nickname: str
    unique_id: str
    avatar_thumb: Optional[dict] = None

class TikTokComment(BaseModel):
    """TikTok comment data structure"""
    cid: str  # comment ID
    aweme_id: str  # video ID
    create_time: int  # timestamp
    text: str  # comment content
    digg_count: int = 0  # likes
    reply_id: str = "0"  # parent comment ID ("0" = top level)
    reply_to_reply_id: str = "0"
    user: TikTokCommentUser

# Internal processing schemas
class PostWithComments(BaseModel):
    """Internal structure for video with comments (reused from shared AI analyzer)"""
    post_id: str
    post_title: str
    post_content: str
    post_author: str
    post_score: int  # likes
    post_date: str
    subreddit: str  # hashtag name
    permalink: str
    url: str
    comments: List[dict]  # nested comment structure

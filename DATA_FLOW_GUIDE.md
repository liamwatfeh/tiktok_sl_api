# TikTok Hashtag Analysis API - Complete Data Flow Guide

> **For Undergraduate Software Engineers**: This guide explains exactly how data moves through our TikTok analysis API, from request to response, in simple terms.

## 🎯 **What This API Does**

When you send a request like "analyze 10 videos for #bmwmotorrad", the API:
1. **Collects** TikTok videos for that hashtag
2. **Collects** top 50 comments for each video  
3. **Cleans** all the messy data
4. **Analyzes** each video + its comments using AI (OpenAI)
5. **Returns** structured insights about sentiment, purchase intent, themes

---

## 📊 **High-Level Architecture**

```
📱 Client Request → 🔍 FastAPI → 🎬 Video Collection → 💬 Comment Collection → 🧹 Data Cleaning → 🤖 AI Analysis → 📋 Response Building → 📱 Client Response
```

**Key Principle**: **1 Video + Its Comments = 1 AI Analysis Call**
- 2 videos = 2 OpenAI calls
- 10 videos = 10 OpenAI calls  
- Each AI call gets full context (video caption + all its comments)

---

## 🚀 **Complete Data Flow Journey**

### **Step 1: Request Entry Point**
**File**: `app/main.py`  
**Function**: `analyze_hashtag_endpoint()`

**What happens:**
- User sends POST request to `/analyze-tiktok-hashtags`
- FastAPI receives the request
- Authentication check (Bearer token)
- Request validation

**Input Data:**
```json
{
  "hashtag": "bmwmotorrad",
  "posts_count": 2,
  "ai_analysis_prompt": "Analyze motorcycle discussions for sentiment..."
}
```

**Output Data:**
- Validated `TikTokHashtagAnalysisRequest` object
- Gets passed to the hashtag service

---

### **Step 2: Request Validation**
**File**: `app/models/tiktok_schemas.py`  
**Class**: `TikTokHashtagAnalysisRequest`

**What happens:**
- Pydantic validates all fields
- Ensures hashtag is valid, posts_count is reasonable
- AI prompt is long enough (minimum 10 characters)
- Sets default model if not provided

**Data Structure:**
```python
class TikTokHashtagAnalysisRequest:
    hashtag: str                    # "bmwmotorrad"
    posts_count: int               # 2 (max 50)
    ai_analysis_prompt: str        # "Analyze motorcycle discussions..."
    model: str                     # "gpt-4.1-2025-04-14"
    max_quote_length: int          # 200
```

---

### **Step 3: Service Orchestration**
**File**: `app/services/tiktok_hashtags/hashtag_service.py`  
**Function**: `analyze_hashtag()`

**What happens:**
- Main orchestrator that coordinates all steps
- Runs 4 sequential stages
- Handles errors and timeouts
- Manages resources (opens/closes connections)

**Pipeline Stages:**
1. **Stage 1**: Collect hashtag videos
2. **Stage 2**: Clean video data  
3. **Stage 3**: Collect & clean comments + AI analysis
4. **Stage 4**: Build final response

---

### **Step 4: Video Collection**
**File**: `app/services/tiktok_shared/tiktok_api_client.py`  
**Function**: `challenge_feed()`

**What happens:**
- Calls TikTok RapidAPI: `/challenge/{hashtag}/feed`
- Gets list of videos for the hashtag
- Limits to requested count (e.g., 2 videos)

**Raw TikTok API Response:**
```json
{
  "status": "ok",
  "data": {
    "aweme_list": [
      {
        "aweme_id": "7541522496688819478",
        "desc": "BMW GS Adventure setup for long trips 🏍️",
        "author": {
          "nickname": "bmw_rider_official",
          "uid": "123456789"
        },
        "statistics": {
          "play_count": 45230,
          "digg_count": 1250,
          "comment_count": 89,
          "share_count": 45
        },
        "create_time": 1693234567,
        "share_url": "https://tiktok.com/video/7541522496688819478"
      }
    ]
  }
}
```

---

### **Step 5: Video Data Cleaning**
**File**: `app/services/tiktok_shared/tiktok_data_cleaners.py`  
**Function**: `clean_hashtag_response()`

**What happens:**
- Removes invalid/broken videos
- Extracts key fields safely
- Normalizes text (HTML decode, whitespace cleanup)
- Calculates engagement rates
- Standardizes date formats

**Cleaned Video Data:**
```python
{
    "aweme_id": "7541522496688819478",
    "desc": "BMW GS Adventure setup for long trips 🏍️",
    "create_time": 1693234567,
    "create_date": "2023-08-28T14:22:47Z",
    "author": {
        "nickname": "bmw_rider_official",
        "uid": "123456789"
    },
    "statistics": {
        "play_count": 45230,
        "digg_count": 1250,
        "comment_count": 89,
        "share_count": 45
    },
    "engagement_rate": 2.76,  # Calculated: (likes+comments+shares)/views * 100
    "share_url": "https://tiktok.com/video/7541522496688819478",
    "hashtags": ["bmw", "motorcycle", "adventure"]
}
```

---

### **Step 6: Comment Collection**
**File**: `app/services/tiktok_shared/tiktok_comment_collector.py`  
**Function**: `collect_all_comments()`

**What happens:**
- For each video, call TikTok API: `/comments/{video_id}`
- Collect up to 50 comments per video (paginated)
- Handle rate limiting between requests
- Organize comments by video ID

**Raw Comment API Response:**
```json
{
  "status": "ok",
  "data": {
    "comments": [
      {
        "cid": "7541654832361685782",
        "text": "Ich wünsche dir eine Reise ohne Probleme allzeit gute Fahrt",
        "create_time": 1693235000,
        "digg_count": 5,
        "user": {
          "nickname": "motorcycle_fan",
          "uid": "987654321"
        },
        "reply_id": "0",
        "aweme_id": "7541522496688819478"
      }
    ],
    "has_more": true,
    "cursor": "50"
  }
}
```

---

### **Step 7: Comment Data Cleaning**
**File**: `app/services/tiktok_shared/tiktok_data_cleaners.py`  
**Function**: `clean_comments_response()`

**What happens:**
- Validates each comment has required fields (cid, text)
- Cleans text (removes control characters, keeps emojis)
- Extracts user information safely
- Converts timestamps to ISO format
- Identifies reply threads

**Cleaned Comment Data:**
```python
{
    "cid": "7541654832361685782",
    "aweme_id": "7541522496688819478",
    "text": "Ich wünsche dir eine Reise ohne Probleme allzeit gute Fahrt",
    "user": {
        "uid": "987654321",
        "nickname": "motorcycle_fan"
    },
    "create_time": 1693235000,
    "create_date": "2023-08-28T14:30:00Z",
    "digg_count": 5,
    "reply_id": "0",
    "is_reply": False,
    "text_length": 59
}
```

---

### **Step 8: Video-Comment Assembly**
**File**: `app/services/tiktok_hashtags/hashtag_service.py`  
**Function**: Stage 3b processing

**What happens:**
- Groups comments by video ID
- Creates video-centric data structure  
- Each video gets paired with its comments
- Prepares for AI analysis

**Video-Comments Structure:**
```python
videos_with_comments = [
    {
        "video_data": {
            "aweme_id": "7541522496688819478",
            "desc": "BMW GS Adventure setup for long trips 🏍️",
            "author": {"nickname": "bmw_rider_official"},
            "statistics": {"play_count": 45230, "digg_count": 1250}
            # ... other video fields
        },
        "comments": [
            {
                "cid": "7541654832361685782",
                "text": "Ich wünsche dir eine Reise ohne Probleme...",
                "user": {"nickname": "motorcycle_fan"}
                # ... other comment fields
            },
            # ... 49 more comments
        ]
    },
    # Video 2 with its comments...
]
```

---

### **Step 9: AI Analysis (Video-Centric)**
**File**: `app/services/tiktok_shared/tiktok_ai_analyzer.py`  
**Function**: `analyze_videos_with_comments()`

**What happens:**
- **Key Innovation**: Process each video + its comments in ONE OpenAI call
- For each video, call `_analyze_video_with_comments()`
- Build comprehensive prompt with video context + all comments
- Use OpenAI structured outputs for consistent results

**AI Prompt Structure:**
```
Analyze this TikTok video and its community discussion:

VIDEO CONTENT:
Video ID: 7541522496688819478
Title: BMW GS Adventure setup for long trips 🏍️
Caption: BMW GS Adventure setup for long trips 🏍️
Creator: @bmw_rider_official
Engagement: 1,250 likes, 45,230 plays, 45 shares

COMMUNITY COMMENTS:
Comment 1:
User: @motorcycle_fan
Text: Ich wünsche dir eine Reise ohne Probleme allzeit gute Fahrt
Likes: 5

Comment 2:
User: @adventure_rider
Text: würde eine ADAC Karte mitnehmen.. 😏
Likes: 3

[... up to 50 comments ...]

Please analyze both the video content and comments according to your instructions.
```

**OpenAI Structured Response:**
```json
{
  "analyses": [
    {
      "quote": "BMW GS Adventure setup for long trips 🏍️",
      "sentiment": "positive",
      "theme": "Adventure motorcycle preparation",
      "purchase_intent": "medium", 
      "confidence_score": 0.95
    },
    {
      "quote": "Ich wünsche dir eine Reise ohne Probleme allzeit gute Fahrt",
      "sentiment": "positive",
      "theme": "User experience/well wishes",
      "purchase_intent": "none",
      "confidence_score": 0.90
    }
  ]
}
```

---

### **Step 10: Analysis Result Processing**
**File**: `app/services/tiktok_shared/tiktok_ai_analyzer.py`  
**Function**: `_analyze_video_with_comments()` (continued)

**What happens:**
- Processes OpenAI structured response
- Identifies if quotes are from video content or comments
- Maps back to original source data
- Adds metadata (video_id, author, likes, etc.)

**Processed Analysis Data:**
```python
analyzed_comments = [
    {
        "quote": "BMW GS Adventure setup for long trips 🏍️",
        "sentiment": "positive",
        "theme": "Adventure motorcycle preparation", 
        "purchase_intent": "medium",
        "confidence_score": 0.95,
        "source_type": "video",           # NEW: Identifies source
        "video_id": "7541522496688819478",
        "author": "bmw_rider_official",
        "likes": 1250
    },
    {
        "quote": "Ich wünsche dir eine Reise ohne Probleme...",
        "sentiment": "positive", 
        "theme": "User experience/well wishes",
        "purchase_intent": "none",
        "confidence_score": 0.90,
        "source_type": "comment",         # NEW: Identifies source
        "comment_id": "7541654832361685782",
        "video_id": "7541522496688819478", 
        "author": "motorcycle_fan",
        "likes": 5
    }
]
```

---

### **Step 11: Response Building**
**File**: `app/services/tiktok_shared/tiktok_response_builder.py`  
**Function**: `build_analysis_response()`

**What happens:**
- Aggregates all analyzed data
- Calculates statistics (sentiment distribution, themes, etc.)
- Builds comprehensive metadata
- Creates final response structure

**Final Response Structure:**
```json
{
  "comment_analyses": [
    {
      "quote": "BMW GS Adventure setup for long trips 🏍️",
      "sentiment": "positive",
      "theme": "Adventure motorcycle preparation",
      "purchase_intent": "medium",
      "confidence_score": 0.95
    }
    // ... more analyses
  ],
  "metadata": {
    "total_videos_analyzed": 2,
    "total_comments_found": 100,
    "relevant_comments_extracted": 22,
    "processing_time_seconds": 51.18,
    "model_used": "gpt-4.1-2025-04-14",
    "hashtag_analyzed": "bmwmotorrad",
    
    // API Usage Stats
    "hashtag_api_calls": 1,      // 1 call to get videos
    "comments_api_calls": 2,     // 1 call per video for comments  
    "ai_analysis_api_calls": 2,  // 1 OpenAI call per video
    "total_api_calls": 5,
    
    // Analysis Stats
    "sentiment_distribution": {
      "positive": 15,
      "neutral": 5, 
      "negative": 2
    },
    "purchase_intent_distribution": {
      "high": 4,
      "medium": 8,
      "low": 3,
      "none": 7
    },
    "top_themes": [
      {"theme": "Adventure motorcycle preparation", "count": 3},
      {"theme": "User experience", "count": 5}
    ]
  }
}
```

---

## 🔧 **Key Technical Innovations**

### **1. Video-Centric AI Analysis**
**Before**: All comments batched together → multiple API calls → lost context  
**After**: Each video + its comments → 1 AI call → full conversational context

### **2. Dual Source Analysis** 
- **Video content** (caption/title) analyzed as potential quotes
- **Comments** analyzed for community sentiment
- AI can extract insights from either source

### **3. Structured Data Pipeline**
Each stage has clear input/output contracts:
- Raw API data → Cleaned data → Analyzed data → Final response
- Each transformation is isolated and testable

### **4. Efficient API Usage**
- **Predictable costs**: N videos = N OpenAI calls
- **Maximum context**: Each AI call gets full video conversation
- **Optimal performance**: 1M token context window fully utilized

---

## 📁 **File Responsibilities Summary**

| File | Role | Key Functions |
|------|------|---------------|
| `app/main.py` | API Gateway | `analyze_hashtag_endpoint()` - Entry point |
| `app/models/tiktok_schemas.py` | Data Validation | Request/Response schemas |
| `app/services/tiktok_hashtags/hashtag_service.py` | Pipeline Orchestrator | `analyze_hashtag()` - Main workflow |
| `app/services/tiktok_shared/tiktok_api_client.py` | External API Client | `challenge_feed()`, `video_comments()` |
| `app/services/tiktok_shared/tiktok_comment_collector.py` | Comment Aggregator | `collect_all_comments()` |
| `app/services/tiktok_shared/tiktok_data_cleaners.py` | Data Normalizer | `clean_hashtag_response()`, `clean_comments_response()` |
| `app/services/tiktok_shared/tiktok_ai_analyzer.py` | AI Analysis Engine | `analyze_videos_with_comments()` |
| `app/services/tiktok_shared/tiktok_response_builder.py` | Response Formatter | `build_analysis_response()` |

---

## 🎯 **Data Transformation Summary**

```
Raw JSON (TikTok API) 
    ↓ [Data Cleaning]
Normalized Python Objects
    ↓ [Video-Comment Assembly] 
Video-Centric Data Structure
    ↓ [AI Analysis]
Structured Analysis Results  
    ↓ [Response Building]
Final JSON Response
```

**Key Insight**: Each step adds value while maintaining data integrity and traceability back to original sources.

---

## 🚀 **Performance Characteristics**

- **Scalability**: Linear scaling (N videos = N OpenAI calls)
- **Reliability**: Each stage handles errors gracefully
- **Efficiency**: Optimal use of API quotas and context windows
- **Maintainability**: Clear separation of concerns, easy to test/debug

**Perfect for production use with predictable costs and performance!** 🎉

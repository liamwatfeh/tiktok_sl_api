# TikTok Social Listening API - Data Pipeline Flow

## Overview
This document explains how data flows through our TikTok Social Listening API from initial request to final response. The architecture follows an **80% shared, 20% unique** approach where most infrastructure is reusable across all three endpoints.

## 4-Stage Data Pipeline

### 🔄 **Stage 1: Data Collection** (UNIQUE per endpoint - 20%)
This is the only stage that differs between endpoints. Each endpoint has its own way of getting the initial video data.

#### **Hashtag Endpoint** (`/analyze-tiktok-hashtags`)
```
User Request: hashtag="bmw", posts_count=20, ai_analysis_prompt="analyze sentiment"
    ↓
Hashtag Collector (hashtag_collector.py)
    ↓
TikTok API Client: challenge_feed(challenge_name="bmw")
    ↓ 
RapidAPI TikTok Scraper: GET /challenge/bmw/feed
    ↓
Returns: List of 20 BMW-related TikTok videos
```

#### **Account Endpoint** (`/analyze-tiktok-accounts`) - Future
```
User Request: username="tesla", posts_count=15, ai_analysis_prompt="find complaints"
    ↓
Account Collector (account_collector.py)
    ↓
TikTok API Client: user_posts(username="tesla")
    ↓
RapidAPI TikTok Scraper: GET /user/tesla/posts
    ↓
Returns: List of 15 videos from Tesla's account
```

#### **Search Endpoint** (`/analyze-tiktok-search`) - Future
```
User Request: query="electric cars", posts_count=25, ai_analysis_prompt="identify trends"
    ↓
Search Collector (search_collector.py)
    ↓
TikTok API Client: search_videos(query="electric cars")
    ↓
RapidAPI TikTok Scraper: GET /search?query=electric+cars
    ↓
Returns: List of 25 videos matching "electric cars"
```

### 🧹 **Stage 2: Data Cleaning** (POTENTIALLY SHARED - 60-80%)
Once we have videos from any endpoint, the data goes through cleaning logic. **Note**: Each endpoint may return different JSON schemas, so cleaning logic might need endpoint-specific adaptations.

```
Raw TikTok Videos (from any endpoint above)
    ↓
Data Cleaners (tiktok_data_cleaners.py) - MOSTLY SHARED
    ↓
• Extract video metadata (ID, description, author, stats)
• Handle endpoint-specific JSON structure differences
• Validate required fields  
• Normalize text encoding
• Filter out corrupted/incomplete videos
    ↓
Clean Video Objects: Ready for comment collection
```

**⚠️ Schema Uncertainty**: We'll need to examine actual API responses from each endpoint to determine how much cleaning logic can be truly shared vs. endpoint-specific.

### 💬 **Stage 3: Comment Collection** (POTENTIALLY SHARED - 70-80%)
Every endpoint needs comments, but comment response schemas might differ. Logic should be mostly shared with potential adaptations.

```
Clean Video Objects
    ↓
Comment Collector (tiktok_comment_collector.py) - MOSTLY SHARED
    ↓
For each video:
    TikTok API Client: get_video_comments(video_id=video.aweme_id)
        ↓
    RapidAPI TikTok Scraper: GET /comments/{video_id}
        ↓
    Returns: Comments for this specific video
    ↓
Data Cleaners: Clean comment text, handle schema differences, filter spam - MOSTLY SHARED
    ↓
Videos + Comments: Combined dataset ready for AI
```

**⚠️ Schema Uncertainty**: Comment response format might vary. We'll need actual API responses to confirm how much logic can be shared.

### 🤖 **Stage 4: AI Analysis** (SHARED - 80%)
The AI analysis is completely reusable - it doesn't care where the data came from.

```
Videos + Comments (from any endpoint)
    ↓
AI Analyzer (tiktok_ai_analyzer.py) - SHARED
    ↓
For each video + comments combination:
    • Create analysis prompt using user's ai_analysis_prompt
    • Send to OpenAI GPT-4.1-2025-04-14
    • Use structured output (Pydantic schema)
    • Extract: sentiment, themes, purchase_intent, quotes
    ↓
AI Analysis Results: Structured insights for each video
```

### 📦 **Stage 5: Response Assembly** (SHARED - 80%)
Final response formatting is identical across all endpoints.

```
AI Analysis Results
    ↓
Response Builder (tiktok_response_builder.py) - SHARED
    ↓
• Aggregate insights across all videos
• Calculate summary statistics
• Format into standardized API response
• Add metadata (processing time, video count, etc.)
    ↓
Final JSON Response: Sent back to user
```

## What's Shared vs. What's Unique

### 🔄 **Unique (20% - Data Collection Only)**
Each endpoint has its own way of getting videos:

| Endpoint | Collector | TikTok API Method | What It Gets |
|----------|-----------|-------------------|--------------|
| Hashtags | `hashtag_collector.py` | `challenge_feed()` | Videos with specific hashtag |
| Accounts | `account_collector.py` | `user_posts()` | Videos from specific user |
| Search | `search_collector.py` | `search_videos()` | Videos matching search query |

### 🔗 **Shared (70-80% - Most Everything Else)**
These components are used by ALL endpoints, with potential schema-specific adaptations:

| Component | Purpose | Reusability |
|-----------|---------|-------------|
| `tiktok_api_client.py` | HTTP client to RapidAPI | 100% - Same base client |
| `tiktok_comment_collector.py` | Get comments for videos | 70-80% - May need schema adaptations |
| `tiktok_data_cleaners.py` | Clean/validate data | 60-80% - May need endpoint-specific logic |
| `tiktok_ai_analyzer.py` | OpenAI analysis | 100% - AI doesn't care about source |
| `tiktok_response_builder.py` | Format final response | 100% - Same response structure |

**⚠️ Note**: Percentages will be confirmed once we examine actual API response schemas from each endpoint.

## Data Flow Example: Hashtag Endpoint

```
1. USER SENDS REQUEST
   POST /analyze-tiktok-hashtags
   {
     "hashtag": "bmw",
     "posts_count": 20,
     "ai_analysis_prompt": "Analyze sentiment about BMW cars and identify purchase intent"
   }

2. HASHTAG COLLECTOR (UNIQUE)
   → Calls challenge_feed("bmw") 
   → Gets 20 BMW-related videos

3. DATA CLEANING (SHARED)
   → Cleans video metadata
   → Validates data integrity

4. COMMENT COLLECTION (SHARED)
   → For each video: get_video_comments(video_id)
   → Collects all comments
   → Cleans comment text

5. AI ANALYSIS (SHARED)
   → Sends videos + comments to OpenAI
   → Uses user's prompt about sentiment and purchase intent
   → Gets structured analysis back

6. RESPONSE BUILDING (SHARED)
   → Aggregates all insights
   → Calculates summary stats
   → Formats final JSON response

7. USER GETS RESPONSE
   {
     "summary": { sentiment stats, themes, etc. },
     "videos": [ analyzed video objects ],
     "metadata": { processing_time, etc. }
   }
```

## Key Benefits of This Architecture

### **🔄 Code Reusability**
- Write comment collection logic once, use everywhere
- Write AI analysis once, use everywhere  
- Write data cleaning once, use everywhere
- Only video collection logic changes per endpoint

### **🔧 Maintainability**
- Bug fixes in shared components benefit all endpoints
- New AI features automatically work for all endpoints
- Consistent data quality across all endpoints

### **⚡ Development Speed**
- Adding new endpoints is fast (only need new collector)
- Most of the complex logic (AI, comments, cleaning) already exists
- Testing is easier (test shared components once)

### **🎯 Consistency**
- All endpoints return same response format
- All endpoints use same AI analysis approach
- All endpoints handle errors the same way

## Current Implementation Status

✅ **Hashtag Endpoint**: Primary focus, being built first
🔄 **Account Endpoint**: Planned after hashtag is complete
🔄 **Search Endpoint**: Planned after account is complete

The beauty of this architecture is that once we finish the hashtag endpoint, we'll have built 80% of the infrastructure needed for the other two endpoints!

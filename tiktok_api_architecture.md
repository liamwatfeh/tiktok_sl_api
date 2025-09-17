# TikTok Social Media Analysis API - High-Level Architecture

## Architecture Overview

The TikTok API follows a **shared foundation with specialized endpoints** pattern, maximizing code reuse while maintaining clean separation of concerns. This design achieves 80% infrastructure reuse across all endpoints.

```
TikTok Analysis API
├── Shared Infrastructure (80% reusable)
│   ├── Core TikTok API Client
│   ├── Comment Collection Engine
│   ├── Data Cleaning & Structuring
│   ├── AI Analysis Engine
│   └── Response Assembly
└── Specialized Endpoints (20% unique)
    ├── /analyze-tiktok-hashtags    (BMW hashtag monitoring)
    ├── /analyze-tiktok-accounts    (Official account monitoring)
    └── /analyze-tiktok-search      (Model-specific searches)
```

---

## File Structure

```
app/
├── services/
│   ├── tiktok_shared/                    # Shared Infrastructure (80%)
│   │   ├── __init__.py
│   │   ├── tiktok_api_client.py         # RapidAPI TikTok client
│   │   ├── tiktok_comment_collector.py  # Comment collection logic
│   │   ├── tiktok_data_cleaners.py      # Data transformation
│   │   ├── tiktok_ai_analyzer.py        # OpenAI integration
│   │   └── tiktok_response_builder.py   # Response assembly
│   │
│   ├── tiktok_hashtags/                 # Hashtag Monitoring Silo
│   │   ├── __init__.py
│   │   ├── hashtag_collector.py         # Challenge Feed by Keyword
│   │   ├── hashtag_service.py           # Service orchestration
│   │   └── hashtag_schemas.py           # Request/response models
│   │
│   ├── tiktok_accounts/                 # Account Monitoring Silo
│   │   ├── __init__.py
│   │   ├── account_collector.py         # User Posts collection
│   │   ├── account_service.py           # Service orchestration
│   │   └── account_schemas.py           # Request/response models
│   │
│   └── tiktok_search/                   # Search Functionality Silo
│       ├── __init__.py
│       ├── search_collector.py          # General search queries
│       ├── search_service.py            # Service orchestration
│       └── search_schemas.py            # Request/response models
│
├── models/
│   └── tiktok_schemas.py                # Shared response models
│
└── main.py                              # FastAPI app with 3 endpoints
```

---

## 4-Stage Data Pipeline

Each endpoint follows an identical 4-stage pipeline with only Stage 1 being unique:

### Stage 1: Data Collection (UNIQUE per endpoint)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HASHTAGS      │    │    ACCOUNTS     │    │     SEARCH      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ Challenge Feed  │    │ User Posts API  │    │ Search Videos   │
│ by Keyword API  │    │ calls for each  │    │ API with query  │
│ calls for each  │    │ @bmwmotorrad    │    │ terms like      │
│ #bmwmotorrad    │    │ account         │    │ "R12GS BMW"     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
```

### Stage 2: Data Cleaning (SHARED across all endpoints)
```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED DATA CLEANING                     │
├─────────────────────────────────────────────────────────────┤
│ 1. collect_all_comments() - Get comments for each video     │
│ 2. clean_tiktok_videos() - Transform to standard format    │
│ 3. clean_tiktok_comments() - Build nested structure        │
│ 4. assemble_videos_with_comments() - Create PostWithComm.  │
└─────────────────────────────────────────────────────────────┘
                                 ▼
```

### Stage 3: AI Analysis (SHARED across all endpoints)
```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED AI ANALYSIS                       │
├─────────────────────────────────────────────────────────────┤
│ 1. TikTokAnalysisOrchestrator - Concurrent processing      │
│ 2. OpenAI GPT-4o integration with TikTok context          │
│ 3. Extract sentiment, themes, purchase intent              │
│ 4. Enhanced prompting for TikTok platform specifics       │
└─────────────────────────────────────────────────────────────┘
                                 ▼
```

### Stage 4: Response Assembly (SHARED across all endpoints)
```
┌─────────────────────────────────────────────────────────────┐
│                  SHARED RESPONSE ASSEMBLY                   │
├─────────────────────────────────────────────────────────────┤
│ 1. combine_analysis_results() - Flatten and combine        │
│ 2. Calculate endpoint-specific metadata                     │
│ 3. Build UnifiedAnalysisResponse with TikTok fields       │
│ 4. Include engagement metrics and thread analysis          │
└─────────────────────────────────────────────────────────────┘
```

---

## Shared Infrastructure Components

### 1. TikTok API Client (`tiktok_shared/tiktok_api_client.py`)
**Purpose**: Single HTTP client for all RapidAPI TikTok Scraper endpoints

**Key Methods**:
- `challenge_feed_by_keyword(keyword: str)` - Hashtag posts
- `user_posts(username: str)` - Account posts  
- `search_videos(query: str)` - Search functionality
- `get_video_comments(aweme_id: str)` - Comments (used by all)

**Reusability**: 100% - All endpoints use same base client

### 2. Comment Collection (`tiktok_shared/tiktok_comment_collector.py`)
**Purpose**: Collect and paginate through video comments

**Key Methods**:
- `collect_video_comments(aweme_id: str)` - Single video
- `collect_all_comments(videos: List[Dict])` - Batch processing
- Handle TikTok's reply threading system

**Reusability**: 100% - Identical logic regardless of video source

### 3. Data Cleaning (`tiktok_shared/tiktok_data_cleaners.py`)
**Purpose**: Transform TikTok data to Facebook-like structure

**Key Functions**:
- `clean_tiktok_video()` - Video metadata transformation
- `clean_tiktok_comments()` - Comment threading
- `assemble_videos_with_comments()` - Final structure

**Reusability**: 100% - Same transformation regardless of source

### 4. AI Analysis (`tiktok_shared/tiktok_ai_analyzer.py`) 
**Purpose**: OpenAI integration with TikTok-specific prompting

**Key Classes**:
- `TikTokCommentFilteringAgent` - AI agent with TikTok context
- `TikTokAnalysisOrchestrator` - Concurrent processing
- `TikTokResultsProcessor` - Result combination

**Reusability**: 100% - Same AI logic for all content types

### 5. Response Assembly (`tiktok_shared/tiktok_response_builder.py`)
**Purpose**: Build final UnifiedAnalysisResponse

**Key Methods**:
- `combine_analysis_results()` - Result aggregation
- `calculate_tiktok_metadata()` - TikTok-specific metrics
- `build_unified_response()` - Final response construction

**Reusability**: 95% - Minor metadata differences per endpoint

---

## Endpoint-Specific Components

### Hashtag Endpoint (`/analyze-tiktok-hashtags`)
**Use Case**: Track hashtags like #bmwmotorrad, #advrider during launches

**Unique Components**:
- `HashtagCollector` - Uses Challenge Feed by Keyword API
- `HashtagAnalysisRequest` - Accepts list of hashtags
- Metadata tracks hashtag-specific metrics

**Data Source**: RapidAPI Challenge Feed by Keyword

### Account Endpoint (`/analyze-tiktok-accounts`)
**Use Case**: Monitor @bmwmotorrad official accounts

**Unique Components**:
- `AccountCollector` - Uses User Posts API
- `AccountAnalysisRequest` - Accepts list of usernames
- Metadata tracks account-specific metrics  

**Data Source**: RapidAPI User Posts

### Search Endpoint (`/analyze-tiktok-search`)
**Use Case**: Find discussions about specific models like "R12GS"

**Unique Components**:
- `SearchCollector` - Uses Search Videos API
- `SearchAnalysisRequest` - Accepts search terms
- Metadata tracks search-specific metrics

**Data Source**: RapidAPI Search Videos

---

## Data Flow Architecture

```
┌─────────────────┐
│ HTTP REQUEST    │
│ (Endpoint-      │
│  Specific)      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ ENDPOINT SILO   │
│ - Validation    │
│ - Collection    │
│ - Orchestration │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ SHARED          │
│ INFRASTRUCTURE  │
│ - Comments      │
│ - Cleaning      │
│ - AI Analysis   │
│ - Response      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ UNIFIED         │
│ RESPONSE        │
│ (Same format    │
│  all endpoints) │
└─────────────────┘
```

---

## API Endpoints

### 1. Hashtag Monitoring
```
POST /analyze-tiktok-hashtags

Request:
{
  "hashtags": ["bmwmotorrad", "r12gs", "advrider"],
  "number_of_posts_per_hashtag": 20,
  "ai_analysis_prompt": "Analyze BMW motorcycle discussions...",
  "model": "gpt-4o-mini-2024-07-18",
  "max_quote_length": 200
}
```

### 2. Account Monitoring  
```
POST /analyze-tiktok-accounts

Request:
{
  "accounts": ["bmwmotorrad", "bmwmotorradusa"],
  "number_of_posts_per_account": 30,
  "ai_analysis_prompt": "Analyze reactions to BMW posts...",
  "model": "gpt-4o-mini-2024-07-18",
  "max_quote_length": 200
}
```

### 3. Search Analysis
```
POST /analyze-tiktok-search  

Request:
{
  "search_terms": ["R12GS BMW", "BMW G310R review"],
  "number_of_posts_per_term": 25,
  "ai_analysis_prompt": "Analyze model-specific discussions...",
  "model": "gpt-4o-mini-2024-07-18", 
  "max_quote_length": 200
}
```

**All endpoints return identical UnifiedAnalysisResponse format**

---

## Implementation Strategy

### Phase 1: Foundation (Weeks 1-2)
1. **Build Shared Infrastructure** (`tiktok_shared/`)
   - TikTok API client integration
   - Comment collection engine
   - Data cleaning pipeline
   - AI analysis framework
   - Response assembly

2. **Test with Single Endpoint**
   - Implement hashtag endpoint first
   - Validate entire pipeline works end-to-end
   - Prove shared infrastructure concept

### Phase 2: Endpoint Silos (Weeks 3-4)
1. **Add Remaining Endpoints**
   - Account monitoring (`tiktok_accounts/`)
   - Search functionality (`tiktok_search/`)
   - Each reuses 80% of foundation work

2. **Integration Testing**
   - Test all endpoints with BMW use cases
   - Performance optimization
   - Error handling validation

### Phase 3: Production Readiness (Week 5)
1. **Deployment & Monitoring**
   - Docker containerization
   - Rate limiting implementation
   - Health checks and metrics

---

## Architecture Benefits

### Code Reuse (80% shared)
- **Single API Client**: No duplicated HTTP logic
- **Unified Data Cleaning**: Same transformation across endpoints
- **Shared AI Engine**: Consistent analysis quality
- **Common Response Format**: Predictable API interface

### Maintainability
- **Bug Fixes**: Apply once, fix everywhere
- **Feature Additions**: Enhance shared components
- **Testing**: Test shared logic once
- **Documentation**: Single source of truth

### Scalability  
- **New Endpoints**: Easy to add with minimal code
- **Platform Extensions**: Instagram/YouTube silos possible
- **Feature Growth**: Shared infrastructure grows capabilities

### Consistency
- **Same Response Format**: All endpoints return UnifiedAnalysisResponse
- **Same Error Handling**: Consistent exception patterns  
- **Same Rate Limiting**: Unified approach to API limits
- **Same AI Quality**: Consistent analysis across endpoints

---

## Technical Specifications

### External Dependencies
- **RapidAPI TikTok Scraper**: Data source for all endpoints
- **OpenAI GPT-4o-mini**: AI analysis engine
- **FastAPI**: Web framework with 3 endpoints
- **Pydantic**: Request/response validation

### Performance Targets
- **Response Time**: < 60 seconds per request
- **Concurrency**: 3 concurrent AI analyses
- **Rate Limiting**: Respect TikTok API limits
- **Scalability**: Stateless design for horizontal scaling

This architecture provides maximum code reuse while maintaining clean separation of concerns, enabling rapid development of BMW's TikTok monitoring capabilities.
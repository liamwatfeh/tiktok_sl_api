# TikTok API - Additional Endpoints Implementation Plan

## 🎯 **Objective**
Implement `/analyze-tiktok-accounts` and `/analyze-tiktok-search` endpoints that reuse 80% of existing shared infrastructure while maintaining architectural consistency.

## 🎉 **MAJOR BREAKTHROUGH**
**Account API is 100% compatible!** The account endpoint response format (`test.json`) is **identical** to our existing hashtag endpoint. This means:
- ✅ **Zero transformation needed** for account API
- ✅ **Direct shared pipeline integration**
- ✅ **Accelerated implementation timeline**
- ✅ **Account endpoint ready to build immediately**

---

## 📊 **Current Architecture Analysis**

### ✅ **What We Have (Hashtag Endpoint)**
```
┌─────────────────┐    ┌─────────────────────────────────────┐
│ HASHTAG ENDPOINT│───▶│ challenge_feed() → SHARED PIPELINE  │
└─────────────────┘    └─────────────────────────────────────┘
                                     │
                       ┌─────────────▼─────────────┐
                       │ 1. Comment Collection     │
                       │ 2. Data Cleaning          │  
                       │ 3. AI Analysis            │
                       │ 4. Response Building      │
                       └───────────────────────────┘
```

### 🎯 **Target Architecture (All 3 Endpoints)**
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────────────────────────┐
│ HASHTAG ENDPOINT│───▶│ TRANSFORMER  │───▶│                                     │
└─────────────────┘    │ (if needed)  │    │                                     │
                       └──────────────┘    │                                     │
┌─────────────────┐    ┌──────────────┐    │         SHARED PIPELINE             │
│ ACCOUNT ENDPOINT│───▶│ TRANSFORMER  │───▶│ 1. Comment Collection               │
└─────────────────┘    │ (normalize)  │    │ 2. Data Cleaning                    │
                       └──────────────┘    │ 3. AI Analysis                      │
┌─────────────────┐    ┌──────────────┐    │ 4. Response Building                │
│ SEARCH ENDPOINT │───▶│ TRANSFORMER  │───▶│                                     │
└─────────────────┘    │ (normalize)  │    └─────────────────────────────────────┘
                       └──────────────┘
```

---

## 🗂️ **Expected File Structure After Implementation**

```
app/services/
├── tiktok_shared/                    # ✅ Existing Shared Infrastructure (80%)
│   ├── tiktok_api_client.py         # ✅ RapidAPI client (extend with new methods)
│   ├── tiktok_comment_collector.py  # ✅ Comment collection (unchanged)
│   ├── tiktok_data_cleaners.py      # ✅ Data transformation (unchanged)
│   ├── tiktok_ai_analyzer.py        # ✅ OpenAI integration (unchanged)
│   ├── tiktok_response_builder.py   # ✅ Response assembly (unchanged)
│   └── tiktok_transformers.py       # 🆕 NEW: Response format normalizers
│
├── tiktok_hashtags/                 # ✅ Existing Hashtag Endpoint
│   └── hashtag_service.py           # ✅ Working implementation
│
├── tiktok_accounts/                 # 🆕 NEW: Account Monitoring Endpoint
│   ├── account_collector.py         # 🆕 User Posts API integration
│   └── account_service.py           # 🆕 Service orchestration
│
└── tiktok_search/                   # 🆕 NEW: Search Analysis Endpoint
    ├── search_collector.py          # 🆕 Search Videos API integration
    └── search_service.py            # 🆕 Service orchestration
```

---

## 📋 **Implementation Plan**

### **Phase 1: Schema Analysis & Transformer Design**
**Status**: ✅ **COMPLETE for Account API - Search API Pending**

**🎉 MAJOR DISCOVERY**: Account API response format is **IDENTICAL** to hashtag endpoint!

**Account API Analysis** (`test.json`):
- ✅ **Response Structure**: Same `{status: "ok", data: {aweme_list: [...]}}`
- ✅ **Video Format**: Exact same `aweme_id`, `desc`, `author`, `statistics`, etc.
- ✅ **Field Mapping**: **NO TRANSFORMATION NEEDED!**

**Remaining Tasks**:
- [ ] Search API Response Schema analysis (pending user input)
- [x] Account transformer design: **PASS-THROUGH** (no changes needed)

**Deliverables**:
```python
# SIMPLIFIED: Account API already matches our StandardVideoFormat!
StandardVideoFormat = {
    "aweme_id": str,           # ✅ Already perfect in account API
    "desc": str,               # ✅ Already perfect in account API
    "author": {...},           # ✅ Already perfect in account API
    "statistics": {...},       # ✅ Already perfect in account API
    "create_time": int,        # ✅ Already perfect in account API
    "share_url": str,          # ✅ Already perfect in account API
    # All fields match perfectly! No normalization needed!
}

# Simplified transformer classes
class HashtagResponseTransformer    # ✅ Pass-through (existing)
class AccountResponseTransformer    # ✅ Pass-through (no changes needed!)  
class SearchResponseTransformer     # ❓ TBD (pending search API schema)
```

---

### **Phase 2: API Client Extensions**
**Status**: 🚀 **READY TO START** (Account API confirmed compatible)

**Tasks**:
- [ ] Verify `user_posts()` method exists in `tiktok_api_client.py` 
- [ ] Test account API endpoint returns expected format (should match `test.json`)
- [ ] ~~Add transformation logic~~ **NOT NEEDED** for account API!
- [ ] Search API method verification (pending search endpoint choice)

**Files to Modify**:
- `app/services/tiktok_shared/tiktok_api_client.py` (minimal changes)

**🎯 Account API Status**: **Ready for implementation** - response format confirmed compatible!

---

### **Phase 3: Account Endpoint Implementation**
**Status**: 🚀 **READY TO START** (No transformer needed!)

**Tasks**:
- [ ] Create `app/services/tiktok_accounts/account_collector.py`
- [ ] Create `app/services/tiktok_accounts/account_service.py`
- [ ] Implement account-specific data collection logic
- [ ] ~~Apply transformer~~ **SKIP** - Direct pass-through to shared pipeline!
- [ ] Plug into shared pipeline (comment collection → AI analysis → response building)

**🎉 SIMPLIFIED FLOW**:
```
Account API → account_collector.py → DIRECT to shared pipeline
(No transformation needed!)
```

**Expected Endpoint**:
```python
POST /analyze-tiktok-accounts

Request:
{
  "accounts": ["bmwmotorrad", "bmwmotorradusa"],
  "posts_per_account": 30,
  "ai_analysis_prompt": "Analyze reactions to BMW posts...",
  "model": "gpt-4.1-2025-04-14",
  "max_quote_length": 200
}
```

---

### **Phase 4: Search Endpoint Implementation**
**Status**: ⏳ **Pending Phase 1 & 2**

**Tasks**:
- [ ] Create `app/services/tiktok_search/search_collector.py`
- [ ] Create `app/services/tiktok_search/search_service.py`
- [ ] Implement search-specific data collection logic
- [ ] Apply transformer to normalize response format
- [ ] Plug into shared pipeline (comment collection → AI analysis → response building)

**Expected Endpoint**:
```python
POST /analyze-tiktok-search

Request:
{
  "search_terms": ["R12GS BMW", "BMW G310R review"],
  "posts_per_term": 25,
  "ai_analysis_prompt": "Analyze model-specific discussions...",
  "model": "gpt-4.1-2025-04-14",
  "max_quote_length": 200
}
```

---

### **Phase 5: FastAPI Integration**
**Status**: ⏳ **Pending Phase 3 & 4**

**Tasks**:
- [ ] Add new endpoints to `app/main.py`
- [ ] Create request/response schemas for new endpoints
- [ ] Apply same security, rate limiting, and error handling
- [ ] Update API documentation

**Files to Modify**:
- `app/main.py`
- `app/models/tiktok_schemas.py`

---

### **Phase 6: Testing & Validation**
**Status**: ⏳ **Pending Phase 5**

**Tasks**:
- [ ] Test all three endpoints with real API calls
- [ ] Verify 80% code reuse achieved
- [ ] Confirm consistent response format across endpoints
- [ ] Validate concurrent processing works for all endpoints
- [ ] Performance testing and optimization

---

## 🎯 **Success Criteria**

### **Code Reuse Target: 80%+ (Account: 95%!)**
- ✅ **Shared Infrastructure (80%)**:
  - Comment Collection Engine
  - Data Cleaning Pipeline  
  - AI Analysis Engine
  - Response Assembly
  - API Client (base)
  
- 🆕 **Endpoint-Specific (20%)**:
  - Data collection methods
  - ~~Response transformers~~ **ACCOUNT: SKIP** ✅
  - Service orchestration

- 🎆 **Account Endpoint: 95% Reuse** (No transformer needed!)

### **Consistent API Interface**
- ✅ All endpoints return `TikTokUnifiedAnalysisResponse`
- ✅ Same authentication and rate limiting
- ✅ Same error handling patterns
- ✅ Same concurrent AI processing

### **Performance Targets**
- ✅ Concurrent AI processing (3x speed improvement)
- ✅ < 60 seconds response time per endpoint
- ✅ Rate limit compliance across all APIs

---

## 📝 **Notes & Decisions**

### **Transformer Pattern Choice**
We're using the **Adapter Pattern** to normalize different API response formats into a common interface. This allows maximum reuse of the shared pipeline while accommodating API differences.

### **Concurrent Processing**
All endpoints will benefit from the existing concurrent AI processing implementation (3 agents with semaphore-based rate limiting).

### **Error Handling**
Existing comprehensive error handling will be extended to cover account and search API specific errors.

---

## 📋 **Next Steps**

1. **🚀 IMMEDIATE - Start Account Endpoint**: No transformer needed - can begin implementation now!
2. **Phase 2**: Verify `user_posts()` method in API client
3. **Phase 3**: Implement account endpoint services (simplified flow)
4. **Future**: Get Search API schema for search endpoint

## 🔥 **FAST TRACK: Account Endpoint**
With the identical response format discovered, we can implement the account endpoint **immediately** with minimal effort:

```python
# Simplified implementation path:
1. Verify/implement user_posts() in tiktok_api_client.py
2. Create account_service.py (copy hashtag pattern)
3. Direct integration with shared pipeline (no transformer!)
4. Add FastAPI endpoint
5. DONE! 🎆
```

---

**Last Updated**: [Current Date]
**Status**: Planning Phase - Awaiting Response Schemas

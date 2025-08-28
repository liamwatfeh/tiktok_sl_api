# TikTok Account Endpoint Implementation Plan

## 🎯 **Objective**
Implement `/analyze-tiktok-accounts` endpoint that monitors specific TikTok accounts using the identical shared pipeline infrastructure.

## 🎉 **Key Advantage**
Account API response format is **IDENTICAL** to hashtag endpoint → **95% code reuse** with minimal effort!

---

## 📋 **Implementation Steps**

### **Step 1: API Client Extension**
**File**: `app/services/tiktok_shared/tiktok_api_client.py`
**Status**: 🔍 **Verify Existing Method**

**Tasks**:
- [ ] Check if `user_posts()` method already exists
- [ ] If not, implement `user_posts(username: str, count: int = 20)` method
- [ ] Add mock data support for `user_posts()` (copy hashtag pattern)
- [ ] Test method returns same format as `test.json`

**Expected Method Signature**:
```python
async def user_posts(self, username: str, count: int = 20) -> dict:
    """
    Fetch user's posts from TikTok User Posts API
    
    Args:
        username: TikTok username (e.g., "bmw")
        count: Number of posts to fetch (default: 20, max: 100)
    
    Returns:
        Same format as challenge_feed() - no transformation needed!
    """
```

---

### **Step 2: Account Data Collector**
**File**: `app/services/tiktok_accounts/account_collector.py`
**Status**: 🚀 **Implement from Scratch**

**Tasks**:
- [ ] Create `AccountCollector` class (copy hashtag pattern)
- [ ] Implement `collect_account_videos(username, max_posts)` method
- [ ] Add input validation for username
- [ ] Add error handling with custom exceptions
- [ ] Add logging for account collection process

**Implementation Template**:
```python
from app.services.tiktok_shared.tiktok_api_client import TikTokAPIClient
from app.core.exceptions import TikTokValidationError, TikTokDataCollectionError
import logging

class AccountCollector:
    def __init__(self, api_client: TikTokAPIClient):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)

    async def collect_account_videos(self, username: str, max_posts: int = 20) -> dict:
        """
        Collect videos from a specific TikTok account
        
        Returns: Same format as hashtag collector - direct pipeline compatibility!
        """
        # Input validation
        # API call to user_posts()
        # Error handling
        # Return response (no transformation needed!)
```

---

### **Step 3: Account Analysis Service**
**File**: `app/services/tiktok_accounts/account_service.py`
**Status**: 🚀 **Implement from Scratch**

**Tasks**:
- [ ] Create `TikTokAccountService` class (copy hashtag service pattern)
- [ ] Implement `analyze_account(request)` method
- [ ] Integrate with shared pipeline (comment collector, AI analyzer, response builder)
- [ ] Add account-specific error handling
- [ ] Add context manager support

**Implementation Template**:
```python
from app.services.tiktok_accounts.account_collector import AccountCollector
from app.services.tiktok_shared.tiktok_comment_collector import TikTokCommentCollector
from app.services.tiktok_shared.tiktok_ai_analyzer import TikTokAIAnalyzer
from app.services.tiktok_shared.tiktok_response_builder import build_analysis_response

class TikTokAccountService:
    def __init__(self):
        # Initialize all shared components
        # Same pattern as hashtag service
        
    async def analyze_account(self, request: TikTokAccountAnalysisRequest) -> dict:
        """
        4-Stage Pipeline (identical to hashtag):
        1. Data Collection → AccountCollector.collect_account_videos()
        2. Comment Collection → Shared TikTokCommentCollector
        3. AI Analysis → Shared TikTokAIAnalyzer  
        4. Response Building → Shared build_analysis_response()
        """
```

---

### **Step 4: Request/Response Schemas**
**File**: `app/models/tiktok_schemas.py`
**Status**: 🆕 **Add New Schemas**

**Tasks**:
- [ ] Add `TikTokAccountAnalysisRequest` schema
- [ ] Reuse existing `TikTokUnifiedAnalysisResponse` (no changes needed!)
- [ ] Add username validation

**New Schema**:
```python
class TikTokAccountAnalysisRequest(BaseModel):
    username: str = Field(
        ..., 
        description="TikTok username to analyze (without @)",
        min_length=1,
        max_length=50
    )
    max_posts: int = Field(
        default=20,
        description="Maximum number of posts to analyze",
        ge=1,
        le=100
    )
    max_comments_per_post: int = Field(
        default=50,
        description="Maximum comments per post to analyze",
        ge=1,
        le=200
    )

# Response: Reuse existing TikTokUnifiedAnalysisResponse! 🎉
```

---

### **Step 5: FastAPI Endpoint**
**File**: `app/main.py`
**Status**: 🆕 **Add New Endpoint**

**Tasks**:
- [ ] Add `/analyze-tiktok-accounts` POST endpoint
- [ ] Import account service and schemas
- [ ] Add rate limiting and authentication
- [ ] Add error handling
- [ ] Add logging

**Endpoint Implementation**:
```python
@app.post("/analyze-tiktok-accounts", response_model=TikTokUnifiedAnalysisResponse)
@limiter.limit("5/minute")
async def analyze_tiktok_account(
    request: Request,
    request_data: TikTokAccountAnalysisRequest,
    authorization: str = Header(...)
):
    """
    Analyze TikTok account posts and comments
    Same response format as hashtag endpoint!
    """
    # Authentication check (same as hashtag)
    # Service call to account_service.analyze_account()
    # Error handling (same as hashtag)
    # Return response
```

---

### **Step 6: Service Registration & Imports**
**File**: Multiple files
**Status**: 🔗 **Wire Everything Together**

**Tasks**:
- [ ] Add imports to `app/main.py`
- [ ] Add convenience function (optional)
- [ ] Update any relevant documentation

---

## 🧪 **Testing Plan**

### **Step 7: Testing & Validation**
**Status**: ✅ **Ready to Test**

**Tasks**:
- [ ] Test with mock data first (`USE_MOCK_DATA=true`)
- [ ] Test with real API (`USE_MOCK_DATA=false`) 
- [ ] Verify response format matches hashtag endpoint
- [ ] Test concurrent processing works
- [ ] Test error handling

**Test Commands**:
```bash
# Mock data test
curl -X POST "http://localhost:8000/analyze-tiktok-accounts" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"username": "bmw", "max_posts": 1}'

# Real API test  
curl -X POST "http://localhost:8000/analyze-tiktok-accounts" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"username": "bmw", "max_posts": 2}'
```

---

## 📊 **Progress Tracking**

### **Phase 1: Foundation** ⏳
- [ ] Step 1: API Client Extension
- [ ] Step 2: Account Data Collector  
- [ ] Step 3: Account Analysis Service

### **Phase 2: Integration** ⏳  
- [ ] Step 4: Request/Response Schemas
- [ ] Step 5: FastAPI Endpoint
- [ ] Step 6: Service Registration

### **Phase 3: Validation** ⏳
- [ ] Step 7: Testing & Validation

---

## 🎯 **Success Criteria**

✅ **Endpoint Working**: `/analyze-tiktok-accounts` returns valid responses  
✅ **Code Reuse**: 95%+ shared infrastructure utilization  
✅ **Performance**: Concurrent AI processing works  
✅ **Compatibility**: Same response format as hashtag endpoint  
✅ **Error Handling**: Robust error responses  

---

## 🚀 **Estimated Timeline**

- **Phase 1**: 2-3 hours (straightforward copying/adapting)
- **Phase 2**: 1-2 hours (schema + endpoint)  
- **Phase 3**: 1 hour (testing)
- **Total**: ~4-6 hours 

**Key Accelerator**: No data transformation needed! 🎉

---

## 📝 **Notes**

- Account API response format identical to hashtag → **zero data mapping**
- All shared components work without modification
- Response format 100% compatible → consistent API experience  
- Mock data support enables testing without API limits
- Concurrent processing inherited from shared pipeline

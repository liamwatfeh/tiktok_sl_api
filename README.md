# TikTok Social Media Analysis API

AI-powered TikTok social media conversation analysis with shared infrastructure design.

## 🎯 Overview

This API provides comprehensive analysis of TikTok conversations across three specialized endpoints:
- **Hashtag Monitoring**: Track hashtag conversations (`/analyze-tiktok-hashtags`)
- **Account Monitoring**: Monitor official account engagement (`/analyze-tiktok-accounts`) 
- **Search Analysis**: Analyze search-based discussions (`/analyze-tiktok-search`)

## 🏗️ Architecture

Built with **80% shared infrastructure** and **20% endpoint-specific** components for maximum code reuse:

- **Shared Infrastructure**: TikTok API client, comment collection, data cleaning, AI analysis, response assembly
- **Endpoint Silos**: Specialized data collection logic per endpoint
- **4-Stage Pipeline**: Data Collection → Cleaning → AI Analysis → Response Assembly

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
TIKTOK_RAPIDAPI_KEY=your-rapidapi-key
OPENAI_API_KEY=your-openai-key  
SERVICE_API_KEY=your-service-key
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the API
```bash
uvicorn app.main:app --reload
```

## 📡 API Endpoints

### POST `/analyze-tiktok-hashtags`
Analyze conversations for a specific hashtag.

**Request:**
```json
{
  "hashtag": "bmwmotorrad",
  "number_of_posts": 20,
  "ai_analysis_prompt": "Analyze for BMW motorcycle sentiment and purchase intent",
  "model": "gpt-4.1-2025-04-14",
  "max_quote_length": 200
}
```

## 🧪 Development Status

- ✅ **Phase 1**: Project foundation and hashtag endpoint (Current)
- ⏳ **Phase 2**: Account monitoring endpoint  
- ⏳ **Phase 3**: Search analysis endpoint

## 📁 Project Structure

```
app/
├── core/              # Configuration and exceptions
├── models/            # Pydantic schemas
├── services/
│   ├── tiktok_shared/     # 80% shared infrastructure
│   ├── tiktok_hashtags/   # Hashtag endpoint (20% unique)
│   ├── tiktok_accounts/   # Account endpoint (20% unique)
│   └── tiktok_search/     # Search endpoint (20% unique)
└── utils/             # Helper functions

tests/                 # Comprehensive test suite
```

## 🔧 Configuration

Key settings in `app/core/config.py`:
- `MAX_POSTS_PER_REQUEST`: 50 (API limit)
- `DEFAULT_MODEL`: gpt-4.1-2025-04-14
- `REQUEST_TIMEOUT`: 250.0 seconds
- `MAX_CONCURRENT_AGENTS`: 3

## 📋 TODO

Implementation follows the detailed guide in `z_docs/tiktok_hashtag_ground_up.md`.

Current step: **Step 1.1 - Project Structure** ✅

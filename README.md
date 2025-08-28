# 🎯 TikTok Social Media Analysis API

> **Production-ready AI-powered TikTok conversation analysis with bulletproof error handling**

[![Railway Deploy](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)

## ✨ What This API Does

Transform TikTok conversations into actionable business insights using AI-powered analysis:

- 📊 **Hashtag Analysis** - Monitor hashtag conversations and sentiment
- 👤 **Account Analysis** - Track engagement on brand accounts  
- 🤖 **AI-Powered Insights** - Extract sentiment, themes, and purchase intent
- ⚡ **Production Ready** - Bulletproof error handling and rate limiting

## 🚀 Live Demo

Deploy to Railway in 60 seconds → [Deploy Now](https://railway.app)

Your API will be live at: `https://your-app.railway.app`

## 📡 API Endpoints

> **📖 [Complete API Documentation](API_DOCUMENTATION.md)** - Full reference with examples, schemas, and best practices

### 🏷️ Hashtag Analysis
**`POST /analyze-tiktok-hashtags`**

Analyze conversations and sentiment around specific hashtags.

```bash
curl -X POST "https://your-app.railway.app/analyze-tiktok-hashtags" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "hashtag": "bmwmotorrad",
    "max_posts": 20,
    "max_comments_per_post": 50,
    "ai_analysis_prompt": "Analyze motorcycle discussions for BMW sentiment and purchase intent",
    "model": "gpt-4.1-2025-04-14"
  }'
```

### 👤 Account Analysis  
**`POST /analyze-tiktok-accounts`**

Monitor engagement and sentiment on brand accounts.

```bash
curl -X POST "https://your-app.railway.app/analyze-tiktok-accounts" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bmw",
    "max_posts": 10,
    "max_comments_per_post": 50,
    "ai_analysis_prompt": "Analyze BMW customer feedback and brand sentiment"
  }'
```

### 🏥 Health Check
**`GET /health`** - API status monitoring

## 🔐 Authentication

All analysis endpoints require Bearer token authentication:

```bash
Authorization: Bearer YOUR_SERVICE_API_KEY
```

## 📊 Response Format

```json
{
  "comment_analyses": [
    {
      "quote": "Love my BMW R1250GS! Best investment ever.",
      "sentiment": "positive",
      "theme": "product satisfaction",
      "purchase_intent": "high",
      "confidence_score": 0.92,
      "video_id": "7234567890123456789",
      "author": "rider_enthusiast"
    }
  ],
  "metadata": {
    "total_videos_analyzed": 20,
    "relevant_comments_extracted": 15,
    "processing_time_seconds": 12.3,
    "model_used": "gpt-4.1-2025-04-14"
  }
}
```

## 🚂 Railway Deployment (Recommended)

### 1. **One-Click Deploy**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### 2. **Manual Deploy**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 3. **Set Environment Variables**
In your Railway dashboard, add:

```env
TIKTOK_RAPIDAPI_KEY=your_rapidapi_key
OPENAI_API_KEY=your_openai_key
SERVICE_API_KEY=your_auth_key
ENVIRONMENT=production
```

**That's it!** Railway auto-detects your Dockerfile and deploys everything.

## 💻 Local Development

### Prerequisites
- Python 3.11+
- TikTok RapidAPI key
- OpenAI API key

### Setup
```bash
# Clone and enter directory
git clone https://github.com/yourusername/tiktok_sl_api.git
cd tiktok_sl_api

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TIKTOK_RAPIDAPI_KEY="your_key"
export OPENAI_API_KEY="your_key"  
export SERVICE_API_KEY="your_auth_key"

# Run locally
uvicorn app.main:app --reload
```

Visit: `http://localhost:8000/docs` for interactive API documentation.

## 🧪 Testing

Run comprehensive bulletproof tests:

```bash
# Quick tests (30 seconds)
python test_endpoints_quick.py

# Comprehensive tests (2-3 minutes)  
python test_endpoints_comprehensive.py
```

**Test Results**: ✅ 100% success rate - endpoints are bulletproof!

## 🏗️ Architecture

**Clean, efficient design with 80% shared infrastructure:**

```
app/
├── core/              # Configuration & exceptions
├── models/            # Pydantic schemas  
├── services/
│   ├── tiktok_shared/     # 🔄 80% shared components
│   ├── tiktok_hashtags/   # 🏷️ Hashtag analysis (20% unique)
│   └── tiktok_accounts/   # 👤 Account analysis (20% unique)
└── main.py            # FastAPI application
```

**4-Stage Pipeline:**
1. **Data Collection** - TikTok API integration
2. **Data Cleaning** - Validation & sanitization  
3. **AI Analysis** - OpenAI structured outputs
4. **Response Assembly** - Unified JSON responses

## ⚙️ Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_POSTS_PER_REQUEST` | 50 | Maximum videos per request |
| `DEFAULT_MODEL` | gpt-4.1-2025-04-14 | OpenAI model |
| `REQUEST_TIMEOUT` | 250s | API timeout |
| `MAX_CONCURRENT_AGENTS` | 3 | Concurrent AI analysis |

## 🔒 Security Features

- 🛡️ **Bearer Token Authentication** - Secure API access
- 🚦 **Rate Limiting** - 10 req/min hashtags, 5 req/min accounts
- 🔐 **CORS Protection** - Production-ready CORS policy
- 🏥 **Health Monitoring** - Built-in health checks
- ⚡ **Input Validation** - Comprehensive request validation

## 📈 Rate Limits

| Endpoint | Rate Limit |
|----------|------------|
| Hashtag Analysis | 10 requests/minute |
| Account Analysis | 5 requests/minute |
| Health Check | 60 requests/minute |

## 🆘 Support

- 📖 **Documentation**: Visit `/docs` on your deployed API
- 🏥 **Health Check**: `GET /health` for API status
- 🔍 **Troubleshooting**: Check Railway logs for detailed error info

## 🎯 Use Cases

- **Brand Monitoring** - Track sentiment around your brand hashtags
- **Competitor Analysis** - Monitor competitor account engagement  
- **Market Research** - Understand customer opinions and trends
- **Campaign Analysis** - Measure hashtag campaign effectiveness
- **Customer Feedback** - Extract insights from brand account comments

## ⚡ Performance

- **Response Time**: ~10-30 seconds (depends on comment volume)
- **Concurrency**: Up to 3 concurrent AI analysis calls
- **Scalability**: Auto-scales on Railway based on demand
- **Reliability**: Bulletproof error handling with graceful fallbacks

## 🛠️ Built With

- **[FastAPI](https://fastapi.tiangolo.com)** - Modern Python web framework
- **[OpenAI](https://openai.com)** - AI-powered analysis with structured outputs  
- **[Railway](https://railway.app)** - Simple, powerful deployment platform
- **[TikTok RapidAPI](https://rapidapi.com)** - TikTok data collection
- **[Pydantic](https://pydantic.dev)** - Data validation and settings

---

**🚀 Ready to analyze TikTok conversations? Deploy now and start extracting insights!**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)
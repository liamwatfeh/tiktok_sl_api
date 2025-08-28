# TikTok Social Media Analysis API Documentation

A simple, powerful API that analyzes TikTok comments using AI to understand sentiment, themes, and purchase intent.

## 🚀 Quick Start

**Base URL**: `https://your-railway-app.railway.app`  
**Authentication**: Bearer token required in all requests

### Example Request
```bash
curl -X POST "https://your-railway-app.railway.app/analyze-tiktok-hashtags" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "hashtag": "bmwmotorrad",
    "max_posts": 10,
    "max_comments_per_post": 30,
    "ai_analysis_prompt": "Analyze motorcycle discussions for BMW sentiment"
  }'
```

---

## 🔑 Authentication

**Header**: `Authorization: Bearer YOUR_API_KEY`

- **Required**: Yes, for all endpoints
- **Format**: Bearer token
- **Get your key**: Contact your system administrator

---

## 📍 Available Endpoints

### 1. Analyze TikTok Hashtag
**POST** `/analyze-tiktok-hashtags`

Analyzes comments from videos using a specific hashtag.

#### Request Body
```json
{
  "hashtag": "bmwmotorrad",
  "max_posts": 20,
  "max_comments_per_post": 50,
  "ai_analysis_prompt": "Analyze motorcycle discussions for sentiment about BMW motorcycles, purchase intent, and user experiences.",
  "model": "gpt-4.1-2025-04-14",
  "max_quote_length": 200
}
```

#### Field Details
| Field | Type | Required | Default | Range | Description |
|-------|------|----------|---------|-------|-------------|
| `hashtag` | string | ✅ Yes | - | 1-100 chars | Hashtag to search (without # symbol) |
| `max_posts` | integer | ❌ No | 20 | 1-50 | Number of posts to analyze |
| `max_comments_per_post` | integer | ❌ No | 50 | 1-200 | Maximum comments per post to analyze |
| `ai_analysis_prompt` | string | ✅ Yes | - | 10+ chars | Instructions for AI analysis |
| `model` | string | ❌ No | gpt-4.1-2025-04-14 | - | OpenAI model to use |
| `max_quote_length` | integer | ❌ No | 200 | 50-500 | Maximum length for extracted quotes |

---

### 2. Analyze TikTok Account
**POST** `/analyze-tiktok-accounts`

Analyzes comments from videos posted by a specific TikTok account.

#### Request Body
```json
{
  "username": "bmwmotorrad",
  "max_posts": 15,
  "max_comments_per_post": 40,
  "ai_analysis_prompt": "Analyze comments on BMW motorcycle videos for customer sentiment and purchase intent.",
  "model": "gpt-4.1-2025-04-14",
  "max_quote_length": 250
}
```

#### Field Details
| Field | Type | Required | Default | Range | Description |
|-------|------|----------|---------|-------|-------------|
| `username` | string | ✅ Yes | - | 1-100 chars | TikTok username (without @ symbol) |
| `max_posts` | integer | ❌ No | 20 | 1-50 | Number of posts to analyze |
| `max_comments_per_post` | integer | ❌ No | 50 | 1-200 | Maximum comments per post to analyze |
| `ai_analysis_prompt` | string | ✅ Yes | - | 10+ chars | Instructions for AI analysis |
| `model` | string | ❌ No | gpt-4.1-2025-04-14 | - | OpenAI model to use |
| `max_quote_length` | integer | ❌ No | 200 | 50-500 | Maximum length for extracted quotes |

---

### 3. Health Check
**GET** `/health`

Quick health check to verify API status.

#### Response
```json
{
  "status": "healthy",
  "api_name": "TikTok Social Media Analysis API",
  "version": "1.0.0",
  "timestamp": 1703123456.789,
  "environment": "production"
}
```

---

### 4. API Information
**GET** `/`

Get basic API information and available endpoints.

#### Response
```json
{
  "api_name": "TikTok Social Media Analysis API",
  "version": "1.0.0",
  "description": "AI-powered TikTok hashtag conversation analysis",
  "endpoints": [
    "/analyze-tiktok-hashtags",
    "/analyze-tiktok-accounts",
    "/health",
    "/docs"
  ]
}
```

---

## 📊 Response Format

All analysis endpoints return the same unified response structure:

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "comment_analyses": [
      {
        "quote": "Love this BMW motorcycle! Thinking of buying one",
        "sentiment": "positive",
        "theme": "purchase consideration",
        "purchase_intent": "high",
        "confidence_score": 0.85
      },
      {
        "quote": "The price is too high for me",
        "sentiment": "negative",
        "theme": "pricing",
        "purchase_intent": "low",
        "confidence_score": 0.92
      }
    ],
    "metadata": {
      "hashtag_analyzed": "bmwmotorrad",
      "total_videos_analyzed": 10,
      "relevant_comments_extracted": 15,
      "processing_time_seconds": 12.5,
      "model_used": "gpt-4.1-2025-04-14",
      "total_api_calls": 8
    }
  }
}
```

### Error Response (4xx/5xx)
```json
{
  "success": false,
  "error": {
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid hashtag format",
    "field": "hashtag",
    "timestamp": 1703123456.789
  }
}
```

---

## 🔍 Response Field Details

### Comment Analysis
| Field | Type | Description |
|-------|------|-------------|
| `quote` | string | The actual comment text (truncated if needed) |
| `sentiment` | string | Overall sentiment: "positive", "negative", "neutral" |
| `theme` | string | Main topic/theme of the comment |
| `purchase_intent` | string | Purchase likelihood: "high", "medium", "low", "none" |
| `confidence_score` | float | AI confidence (0.0 to 1.0) |

### Metadata
| Field | Type | Description |
|-------|------|-------------|
| `hashtag_analyzed` | string | The hashtag that was analyzed |
| `total_videos_analyzed` | integer | Number of videos processed |
| `relevant_comments_extracted` | integer | Total comments analyzed |
| `processing_time_seconds` | float | Total processing time |
| `model_used` | string | OpenAI model used for analysis |
| `total_api_calls` | integer | Total API calls made |

---

## ⚡ Rate Limits

- **Health Check**: 60 requests per minute
- **Root Endpoint**: 30 requests per minute
- **Analysis Endpoints**: Subject to TikTok API and OpenAI rate limits

---

## 🚨 Common Error Codes

| Error Code | HTTP Status | Description | Solution |
|------------|-------------|-------------|----------|
| `VALIDATION_ERROR` | 400 | Invalid input parameters | Check field requirements and ranges |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing API key | Verify your Bearer token |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait and retry later |
| `DATA_COLLECTION_ERROR` | 502 | TikTok API issues | Try again later |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error | Contact support |

---

## 💡 Best Practices

### 1. **AI Analysis Prompts**
- Be specific about what you want to analyze
- Include context about your business goals
- Example: "Analyze comments for customer satisfaction, product complaints, and purchase intent"

### 2. **Comment Limits**
- Start with `max_comments_per_post: 30-50` for faster results
- Increase to 100-200 for comprehensive analysis
- Balance speed vs. depth based on your needs

### 3. **Post Limits**
- Start with `max_posts: 10-20` for testing
- Increase to 30-50 for production analysis
- Higher limits = more data but slower processing

### 4. **Error Handling**
- Always check the `success` field in responses
- Handle rate limiting gracefully with retry logic
- Log error details for debugging

---

## 🔧 Testing Examples

### Test with Minimal Data
```json
{
  "hashtag": "test",
  "max_posts": 5,
  "max_comments_per_post": 10,
  "ai_analysis_prompt": "Analyze these comments for general sentiment and themes."
}
```

### Production-Ready Request
```json
{
  "hashtag": "bmwmotorrad",
  "max_posts": 25,
  "max_comments_per_post": 75,
  "ai_analysis_prompt": "Analyze motorcycle discussions for: 1) Customer satisfaction with BMW bikes, 2) Common complaints or issues, 3) Purchase intent and buying decisions, 4) Brand perception and loyalty.",
  "model": "gpt-4.1-2025-04-14",
  "max_quote_length": 300
}
```

---

## 📞 Support

- **Documentation**: `/docs` (Swagger UI) - Available in development mode
- **Health Check**: `/health` - Monitor API status
- **Rate Limits**: Check response headers for current limits

---

## 🚀 Getting Started

1. **Get your API key** from your administrator
2. **Test the health endpoint**: `GET /health`
3. **Try a simple analysis**: Use the minimal test example above
4. **Scale up**: Increase limits based on your needs
5. **Monitor**: Check processing times and API call counts

**Happy analyzing! 🎯**

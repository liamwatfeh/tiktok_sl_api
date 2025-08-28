# 🚂 Railway Deployment Guide

## Quick Setup

### 1. **Railway Account Setup**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### 2. **Deploy to Railway**
```bash
# From your project directory
railway init
railway up
```

### 3. **Set Environment Variables**
Go to your Railway dashboard and set these **required** environment variables:

#### **🔑 Required API Keys**
```
TIKTOK_RAPIDAPI_KEY=your_rapidapi_key_here
OPENAI_API_KEY=your_openai_api_key_here  
SERVICE_API_KEY=your_service_authentication_key_here
```

#### **🌍 Environment Settings**
```
ENVIRONMENT=production
LOG_LEVEL=INFO
```

#### **⚙️ Optional Configuration** (use defaults if not set)
```
MAX_POSTS_PER_REQUEST=50
DEFAULT_POSTS_PER_REQUEST=20
MAX_COMMENTS_PER_VIDEO=100
DEFAULT_COMMENTS_PER_VIDEO=50
DEFAULT_MODEL=gpt-4.1-2025-04-14
MAX_CONCURRENT_AGENTS=3
REQUEST_TIMEOUT=250.0
```

**Note**: `PORT` is automatically set by Railway - don't set it manually.

## 📋 Pre-Deployment Checklist

### ✅ **Docker Ready**
- [x] Dockerfile uses dynamic `PORT` environment variable
- [x] Health check endpoint at `/health`
- [x] Production-ready configuration

### ✅ **API Keys Ready**
- [ ] TikTok RapidAPI key obtained
- [ ] OpenAI API key obtained  
- [ ] Service API key generated (for authentication)

### ✅ **Configuration Ready**
- [x] Environment variables documented
- [x] Production settings configured
- [x] Logging set to appropriate level

## 🚀 Deployment Steps

### **Step 1: Push to Git Repository**
```bash
git add .
git commit -m "Railway deployment ready"
git push origin main
```

### **Step 2: Connect to Railway**
1. Go to [Railway.app](https://railway.app)
2. Click "Start a New Project"
3. Connect your GitHub repository
4. Select your TikTok API repository

### **Step 3: Configure Environment Variables**
1. Go to your project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add all required environment variables listed above

### **Step 4: Deploy**
Railway will automatically deploy when you push to your connected branch.

## 🔍 Health Checks

Your API includes these monitoring endpoints:

- **Health Check**: `GET /health`
- **API Info**: `GET /`
- **Interactive Docs**: `GET /docs` (development only)

## 🐛 Troubleshooting

### **Common Issues**

#### **Port Issues**
- ✅ **Fixed**: App now uses Railway's dynamic `PORT` variable
- Railway assigns ports automatically - don't set `PORT` manually

#### **API Key Issues**
- Ensure all 3 required API keys are set in Railway environment variables
- Keys should not have quotes around them in Railway dashboard

#### **Health Check Failures**
- The app includes a `/health` endpoint that Railway uses for monitoring
- If health checks fail, check the logs in Railway dashboard

#### **Startup Issues**
- Check Railway logs for specific error messages
- Ensure `ENVIRONMENT=production` is set
- Verify all required dependencies are in `requirements.txt`

## 📊 Monitoring

### **Railway Dashboard**
- View logs in real-time
- Monitor resource usage
- Check deployment status
- View environment variables

### **API Endpoints for Monitoring**
```bash
# Check if API is running
curl https://your-app.railway.app/health

# Get API information
curl https://your-app.railway.app/

# Test hashtag endpoint (requires authentication)
curl -X POST https://your-app.railway.app/analyze-tiktok-hashtags \
  -H "Authorization: Bearer YOUR_SERVICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "hashtag": "test",
    "max_posts": 2,
    "ai_analysis_prompt": "Test analysis for deployment verification"
  }'
```

## 🔒 Security Notes

- Service requires Bearer token authentication for all analysis endpoints
- CORS is configured for production domains
- Security headers are automatically added
- Rate limiting is enabled (10 requests/minute for hashtags, 5 for accounts)

## 💰 Cost Optimization

- Railway charges based on usage
- Your app sleeps when not in use (saves money)
- Monitor usage in Railway dashboard
- Consider setting usage limits in Railway settings

---

**🎉 Your TikTok API is now Railway-ready!**

After deployment, your endpoints will be available at:
- `https://your-app.railway.app/analyze-tiktok-hashtags`
- `https://your-app.railway.app/analyze-tiktok-accounts`

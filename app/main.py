import time
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.exceptions import TikTokAPIException
from app.models.tiktok_schemas import TikTokHashtagAnalysisRequest, TikTokUnifiedAnalysisResponse
from app.services.tiktok_hashtags.hashtag_service import TikTokHashtagService

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify API key authentication.
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        Verified credentials
        
    Raises:
        HTTPException: If authentication fails
    """
    if credentials.credentials != settings.SERVICE_API_KEY:
        logger.warning(f"Invalid API key attempt: {credentials.credentials[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", summary="Health Check")
async def health_check():
    """
    Health check endpoint to verify API status and configuration.
    
    Returns:
        Health status with configuration details
    """
    return {
        "status": "healthy",
        "api_name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "timestamp": time.time(),
        "configuration": {
            "tiktok_api_configured": bool(settings.TIKTOK_RAPIDAPI_KEY),
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "service_auth_configured": bool(settings.SERVICE_API_KEY),
            "max_posts_per_request": settings.MAX_POSTS_PER_REQUEST,
            "log_level": settings.LOG_LEVEL
        }
    }

# Root endpoint
@app.get("/", summary="API Information")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    
    Returns:
        API overview and endpoint list
    """
    return {
        "api_name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "endpoints": [
            "/analyze-tiktok-hashtags",
            "/analyze-tiktok-accounts", 
            "/analyze-tiktok-search",
            "/health", 
            "/docs",
            "/redoc"
        ],
        "documentation": {
            "interactive_docs": "/docs",
            "alternative_docs": "/redoc"
        }
    }

# TikTok Analysis Endpoints

@app.post(
    "/analyze-tiktok-hashtags",
    response_model=dict,
    summary="Analyze TikTok Hashtag",
    description="Analyze TikTok comments for a specific hashtag using AI-powered sentiment and theme analysis",
    responses={
        200: {
            "description": "Successful analysis",
            "content": {
                "application/json": {
                    "example": {
                        "comment_analyses": [
                            {
                                "quote": "Love this BMW motorcycle! Thinking of buying one",
                                "sentiment": "positive",
                                "theme": "purchase consideration",
                                "purchase_intent": "high",
                                "confidence_score": 0.85
                            }
                        ],
                        "metadata": {
                            "hashtag_analyzed": "bmwmotorrad",
                            "total_videos_analyzed": 10,
                            "relevant_comments_extracted": 15,
                            "processing_time_seconds": 12.5,
                            "model_used": "gpt-4.1-2025-04-14"
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid request parameters"},
        401: {"description": "Invalid API key"},
        500: {"description": "Internal server error"}
    }
)
async def analyze_tiktok_hashtag(
    request: TikTokHashtagAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """
    Analyze TikTok hashtag for sentiment, themes, and purchase intent.
    
    This endpoint performs a complete analysis pipeline:
    1. Collects TikTok videos for the specified hashtag
    2. Extracts and cleans comments from those videos
    3. Analyzes comments using AI for sentiment, themes, and purchase intent
    4. Returns structured analysis results with comprehensive metadata
    
    **Authentication**: Requires Bearer token in Authorization header
    
    **Rate Limits**: Subject to TikTok API and OpenAI rate limits
    
    **Processing Time**: Typically 10-30 seconds depending on comment volume
    """
    logger.info(f"Hashtag analysis request received for: #{request.hashtag}")
    logger.info(f"Analysis prompt: {request.ai_analysis_prompt[:50]}...")
    
    try:
        # Initialize hashtag service and perform analysis
        with TikTokHashtagService() as service:
            result = service.analyze_hashtag(request)
        
        # Check if result contains an error
        if "error" in result:
            logger.error(f"Analysis failed: {result['error']['message']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Log successful completion
        metadata = result.get("metadata", {})
        logger.info(f"Analysis complete for #{request.hashtag}")
        logger.info(f"Results: {metadata.get('relevant_comments_extracted', 0)} comments analyzed in {metadata.get('processing_time_seconds', 0)}s")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
        
    except TikTokAPIException as e:
        logger.error(f"TikTok API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "TikTok analysis service error",
                "error_code": e.error_code,
                "details": e.to_dict()
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in hashtag analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An unexpected error occurred during analysis",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )

# TODO: Add additional endpoints in future phases
# - /analyze-tiktok-accounts (Phase 2)
# - /analyze-tiktok-search (Phase 3)

# Startup event handler
@app.on_event("startup")
async def startup_event():
    """
    Application startup handler.
    Logs startup information and validates configuration.
    """
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"TikTok API configured: {bool(settings.TIKTOK_RAPIDAPI_KEY)}")
    logger.info(f"OpenAI configured: {bool(settings.OPENAI_API_KEY)}")
    logger.info(f"Service auth configured: {bool(settings.SERVICE_API_KEY)}")

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown handler.
    Logs shutdown information and cleanup.
    """
    logger.info(f"Shutting down {settings.API_TITLE}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

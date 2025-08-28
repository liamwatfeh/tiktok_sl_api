import time
import logging
import secrets
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.exceptions import TikTokAPIException, AuthenticationError
from app.models.tiktok_schemas import (
    TikTokHashtagAnalysisRequest, 
    TikTokAccountAnalysisRequest,
    TikTokUnifiedAnalysisResponse
)
from app.services.tiktok_hashtags.hashtag_service import TikTokHashtagService
from app.services.tiktok_accounts.account_service import TikTokAccountService

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify API key authentication using timing-safe comparison.
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        Verified credentials
        
    Raises:
        AuthenticationError: If authentication fails
    """
    # Use timing-safe comparison to prevent timing attacks
    if not secrets.compare_digest(credentials.credentials, settings.SERVICE_API_KEY):
        logger.warning("Invalid API key attempt from authenticated request")
        raise AuthenticationError(
            "Invalid API key",
            auth_type="Bearer"
        )
    return credentials

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    
    # Validate critical configuration
    if not settings.TIKTOK_RAPIDAPI_KEY:
        logger.critical("TikTok API key not configured")
    if not settings.OPENAI_API_KEY:
        logger.critical("OpenAI API key not configured")
    if not settings.SERVICE_API_KEY:
        logger.critical("Service API key not configured")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.API_TITLE}")
    logger.info("Application shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.your-domain.com"] if settings.ENVIRONMENT == "production" else ["*"]
)

# CORS middleware with environment-specific configuration
if settings.ENVIRONMENT == "development":
    # Development: Allow localhost origins
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
else:
    # Production: Specific domains only
    allowed_origins = [
        "https://your-frontend-domain.com",
        "https://app.your-domain.com"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"]
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Health check endpoint
@app.get("/health", summary="Health Check")
@limiter.limit("60/minute")
async def health_check(request: Request) -> Dict[str, Any]:
    """
    Health check endpoint to verify API status.
    
    Returns:
        Basic health status without sensitive configuration details
    """
    return {
        "status": "healthy",
        "api_name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/", summary="API Information")
@limiter.limit("30/minute")
async def root(request: Request) -> Dict[str, Any]:
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
    response_model=TikTokUnifiedAnalysisResponse,
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
        422: {"description": "Request validation error"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        502: {"description": "External service error"},
        503: {"description": "Service temporarily unavailable"}
    }
)
@limiter.limit("10/minute")
async def analyze_tiktok_hashtag(
    request: Request,
    request_data: TikTokHashtagAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
) -> TikTokUnifiedAnalysisResponse:
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
    # Log request without sensitive details
    logger.info(f"Hashtag analysis request received for: #{request_data.hashtag}")
    logger.info(f"Requested posts: {request_data.max_posts}, Model: {request_data.model}")
    
    try:
        # Initialize hashtag service and perform analysis
        with TikTokHashtagService() as service:
            result = await service.analyze_hashtag(request_data)
        
        # Check if result contains an error
        if "error" in result:
            error_details = result["error"]
            logger.error(f"Analysis failed: {error_details.get('message', 'Unknown error')}")
            
            # Map error codes to appropriate HTTP status codes
            error_code = error_details.get('error_code', 'UNKNOWN_ERROR')
            if error_code in ['VALIDATION_ERROR', 'INVALID_HASHTAG']:
                status_code = status.HTTP_400_BAD_REQUEST
            elif error_code in ['AUTHENTICATION_ERROR']:
                status_code = status.HTTP_401_UNAUTHORIZED
            elif error_code in ['RATE_LIMIT_EXCEEDED']:
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif error_code in ['DATA_COLLECTION_ERROR', 'EXTERNAL_SERVICE_ERROR']:
                status_code = status.HTTP_502_BAD_GATEWAY
            elif error_code in ['ANALYSIS_ERROR']:
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            raise HTTPException(status_code=status_code, detail=error_details)
        
        # Log successful completion
        metadata = result.get("metadata", {})
        logger.info(f"Analysis complete for #{request_data.hashtag}")
        logger.info(f"Results: {metadata.get('relevant_comments_extracted', 0)} comments analyzed in {metadata.get('processing_time_seconds', 0):.2f}s")
        logger.info(f"API calls used: {metadata.get('total_api_calls', 0)}")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
        
    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.to_dict()
        )
        
    except TikTokAPIException as e:
        logger.error(f"TikTok API error: {e.error_code} - {e.message}")
        
        # Map exception types to HTTP status codes
        status_code_map = {
            "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
            "TIKTOK_DATA_COLLECTION": status.HTTP_502_BAD_GATEWAY,
            "TIKTOK_ANALYSIS": status.HTTP_503_SERVICE_UNAVAILABLE,
            "TIKTOK_TIMEOUT": status.HTTP_504_GATEWAY_TIMEOUT,
            "CONFIGURATION": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "EXTERNAL_SERVICE": status.HTTP_502_BAD_GATEWAY,
            "DATA_PROCESSING": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "RESOURCE_EXHAUSTED": status.HTTP_507_INSUFFICIENT_STORAGE
        }
        
        http_status = status_code_map.get(e.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        raise HTTPException(
            status_code=http_status,
            detail=e.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in hashtag analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during analysis",
                "timestamp": time.time()
            }
        )

@app.post(
    "/analyze-tiktok-accounts",
    response_model=TikTokUnifiedAnalysisResponse,
    summary="Analyze TikTok Account",
    description="Analyze TikTok comments from a specific account's posts using AI-powered sentiment and theme analysis",
    responses={
        200: {
            "description": "Successful analysis",
            "content": {
                "application/json": {
                    "example": {
                        "comment_analyses": [
                            {
                                "quote": "Love this BMW! Great quality and performance",
                                "sentiment": "positive",
                                "theme": "product quality",
                                "purchase_intent": "medium",
                                "confidence_score": 0.88
                            }
                        ],
                        "metadata": {
                            "hashtag_analyzed": "bmw",
                            "total_videos_analyzed": 5,
                            "relevant_comments_extracted": 12,
                            "processing_time_seconds": 8.3,
                            "model_used": "gpt-4.1-2025-04-14"
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid request parameters"},
        401: {"description": "Invalid API key"},
        422: {"description": "Request validation error"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        502: {"description": "External service error"},
        503: {"description": "Service temporarily unavailable"}
    }
)
@limiter.limit("5/minute")
async def analyze_tiktok_account(
    request: Request,
    request_data: TikTokAccountAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
) -> TikTokUnifiedAnalysisResponse:
    """
    Analyze TikTok account posts and comments for sentiment, themes, and purchase intent.
    
    This endpoint performs a complete analysis pipeline:
    1. Collects TikTok videos from the specified account
    2. Extracts and cleans comments from those videos
    3. Analyzes comments using AI for sentiment, themes, and purchase intent
    4. Returns structured analysis results with comprehensive metadata
    
    **Authentication**: Requires Bearer token in Authorization header
    
    **Rate Limits**: Subject to TikTok API and OpenAI rate limits
    
    **Processing Time**: Typically 10-30 seconds depending on comment volume
    """
    # Log request without sensitive details
    logger.info(f"Account analysis request received for: @{request_data.username}")
    logger.info(f"Requested posts: {request_data.max_posts}, Comments per post: {request_data.max_comments_per_post}, Model: {request_data.model}")
    
    try:
        # Initialize account service and perform analysis
        with TikTokAccountService() as service:
            result = await service.analyze_account(request_data)
        
        # Check if result contains an error
        if "error" in result:
            error_details = result["error"]
            logger.error(f"Analysis failed: {error_details.get('message', 'Unknown error')}")
            
            # Map error codes to appropriate HTTP status codes
            error_code = error_details.get('error_code', 'UNKNOWN_ERROR')
            if error_code in ['VALIDATION_ERROR', 'INVALID_USERNAME']:
                status_code = status.HTTP_400_BAD_REQUEST
            elif error_code in ['AUTHENTICATION_ERROR']:
                status_code = status.HTTP_401_UNAUTHORIZED
            elif error_code in ['RATE_LIMIT_EXCEEDED']:
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif error_code in ['DATA_COLLECTION_ERROR', 'EXTERNAL_SERVICE_ERROR']:
                status_code = status.HTTP_502_BAD_GATEWAY
            elif error_code in ['ANALYSIS_ERROR']:
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            raise HTTPException(status_code=status_code, detail=error_details)
        
        # Log successful completion
        metadata = result.get("metadata", {})
        logger.info(f"Analysis complete for @{request_data.username}")
        logger.info(f"Results: {metadata.get('relevant_comments_extracted', 0)} comments analyzed in {metadata.get('processing_time_seconds', 0):.2f}s")
        logger.info(f"API calls used: {metadata.get('total_api_calls', 0)}")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
        
    except AuthenticationError as e:
        logger.warning(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.to_dict()
        )
        
    except TikTokAPIException as e:
        logger.error(f"TikTok API error: {e.error_code} - {e.message}")
        
        # Map TikTok exception types to HTTP status codes
        if hasattr(e, 'http_status') and e.http_status:
            http_status = e.http_status
        elif e.error_code in ['VALIDATION_ERROR', 'INVALID_PARAMETERS']:
            http_status = status.HTTP_400_BAD_REQUEST
        elif e.error_code in ['RATE_LIMIT_EXCEEDED']:
            http_status = status.HTTP_429_TOO_MANY_REQUESTS
        elif e.error_code in ['DATA_COLLECTION_ERROR']:
            http_status = status.HTTP_502_BAD_GATEWAY
        else:
            http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        raise HTTPException(
            status_code=http_status,
            detail=e.to_dict()
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in account analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during analysis",
                "timestamp": time.time()
            }
        )

# TODO: Add additional endpoints in future phases
# - /analyze-tiktok-search (Phase 3)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Only add HSTS in production with HTTPS
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

if __name__ == "__main__":
    import uvicorn
    
    # Development vs Production configuration
    if settings.ENVIRONMENT == "development":
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",  # More secure for development
            port=settings.PORT, 
            reload=True,
            log_level=settings.LOG_LEVEL.lower()
        )
    else:
        # Production configuration (Railway/Docker)
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=settings.PORT,
            reload=False,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )

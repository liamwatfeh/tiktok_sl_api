from typing import Optional, Dict, Any

class TikTokAPIException(Exception):
    """Base exception for TikTok API errors."""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }

class ValidationError(TikTokAPIException):
    """Request validation error."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["provided_value"] = value
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(TikTokAPIException):
    """Authentication error."""
    
    def __init__(self, message: str, auth_type: str = None):
        details = {"auth_type": auth_type} if auth_type else {}
        super().__init__(message, status_code=401, details=details)

class ConfigurationError(TikTokAPIException):
    """Server configuration error."""
    
    def __init__(self, message: str, config_key: str = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, status_code=500, details=details)

class TikTokDataCollectionError(TikTokAPIException):
    """TikTok data collection error."""
    
    def __init__(self, message: str, api_endpoint: str = None, http_status: int = None):
        details = {}
        if api_endpoint:
            details["api_endpoint"] = api_endpoint
        if http_status:
            details["http_status"] = http_status
        super().__init__(message, status_code=502, details=details)

class TikTokAnalysisError(TikTokAPIException):
    """AI analysis error."""
    
    def __init__(self, message: str, model: str = None, video_id: str = None):
        details = {}
        if model:
            details["model"] = model
        if video_id:
            details["video_id"] = video_id
        super().__init__(message, status_code=503, details=details)

class RateLimitExceededError(TikTokAPIException):
    """Rate limit exceeded."""
    
    def __init__(self, message: str, service: str = None, retry_after: int = None):
        details = {}
        if service:
            details["service"] = service
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, status_code=429, details=details)

class TimeoutError(TikTokAPIException):
    """Request timeout error."""
    
    def __init__(self, message: str, operation: str = None, timeout_seconds: float = None):
        details = {}
        if operation:
            details["operation"] = operation
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(message, status_code=504, details=details)

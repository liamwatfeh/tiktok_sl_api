import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime

class TikTokAPIException(Exception):
    """
    Base exception for TikTok API errors.
    
    Provides structured error handling with HTTP status codes, error codes,
    and additional context details. All TikTok API exceptions inherit from this.
    
    Args:
        message: Human-readable error message
        status_code: HTTP status code (default: 500)
        error_code: Unique error identifier (auto-generated from class name if not provided)
        details: Additional context information
        log_level: Logging level for this error (default: ERROR)
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None,
        log_level: str = "ERROR"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self._generate_error_code()
        self.details = self._sanitize_details(details or {})
        self.log_level = log_level
        self.timestamp = datetime.utcnow().isoformat()
        
        # Log the exception
        logger = logging.getLogger(self.__class__.__module__)
        getattr(logger, log_level.lower(), logger.error)(
            f"{self.error_code}: {self.message}",
            extra={
                "error_code": self.error_code,
                "status_code": self.status_code,
                "details": self.details,
                "timestamp": self.timestamp
            }
        )
        
        super().__init__(self.message)
    
    def _generate_error_code(self) -> str:
        """Generate error code from class name, removing 'Error' suffix."""
        class_name = self.__class__.__name__
        if class_name.endswith('Error'):
            class_name = class_name[:-5]
        return class_name.upper()
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize details to prevent sensitive information leakage."""
        sanitized = {}
        sensitive_keys = {'password', 'token', 'key', 'secret', 'auth', 'api_key'}
        
        for key, value in details.items():
            # Check if key contains sensitive information
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 1000:
                # Truncate very long strings
                sanitized[key] = value[:1000] + "...[TRUNCATED]"
            else:
                sanitized[key] = value
                
        return sanitized
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "status_code": self.status_code
        }
    
    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', status_code={self.status_code}, error_code='{self.error_code}')"

class TikTokValidationError(TikTokAPIException):
    """Request validation error."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["provided_value"] = value
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(TikTokAPIException):
    """Authentication error - invalid or missing credentials."""
    
    def __init__(self, message: str, auth_type: Optional[str] = None):
        details = {"auth_type": auth_type} if auth_type else {}
        super().__init__(message, status_code=401, details=details, log_level="WARNING")

class ConfigurationError(TikTokAPIException):
    """Server configuration error - missing or invalid configuration."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, status_code=500, details=details, log_level="CRITICAL")

class TikTokDataCollectionError(TikTokAPIException):
    """TikTok data collection error - issues retrieving data from TikTok API."""
    
    def __init__(self, message: str, api_endpoint: Optional[str] = None, http_status: Optional[int] = None, retry_count: Optional[int] = None):
        details = {}
        if api_endpoint:
            details["api_endpoint"] = api_endpoint
        if http_status:
            details["http_status"] = http_status
        if retry_count is not None:
            details["retry_count"] = retry_count
        super().__init__(message, status_code=502, details=details)

class TikTokAnalysisError(TikTokAPIException):
    """AI analysis error - issues with OpenAI or analysis processing."""
    
    def __init__(self, message: str, model: Optional[str] = None, video_id: Optional[str] = None, analysis_type: Optional[str] = None):
        details = {}
        if model:
            details["model"] = model
        if video_id:
            details["video_id"] = video_id
        if analysis_type:
            details["analysis_type"] = analysis_type
        super().__init__(message, status_code=503, details=details)

class RateLimitExceededError(TikTokAPIException):
    """Rate limit exceeded - API quota or rate limit hit."""
    
    def __init__(self, message: str, service: Optional[str] = None, retry_after: Optional[int] = None, current_usage: Optional[int] = None):
        details = {}
        if service:
            details["service"] = service
        if retry_after:
            details["retry_after"] = retry_after
        if current_usage is not None:
            details["current_usage"] = current_usage
        super().__init__(message, status_code=429, details=details, log_level="WARNING")

class TikTokTimeoutError(TikTokAPIException):
    """Request timeout error - operation took too long to complete."""
    
    def __init__(self, message: str, operation: Optional[str] = None, timeout_seconds: Optional[float] = None, elapsed_seconds: Optional[float] = None):
        details = {}
        if operation:
            details["operation"] = operation
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        if elapsed_seconds:
            details["elapsed_seconds"] = elapsed_seconds
        super().__init__(message, status_code=504, details=details)


class DataProcessingError(TikTokAPIException):
    """Data processing error - issues with cleaning or transforming data."""
    
    def __init__(self, message: str, data_type: Optional[str] = None, stage: Optional[str] = None, record_count: Optional[int] = None):
        details = {}
        if data_type:
            details["data_type"] = data_type
        if stage:
            details["processing_stage"] = stage
        if record_count is not None:
            details["record_count"] = record_count
        super().__init__(message, status_code=422, details=details)


class ExternalServiceError(TikTokAPIException):
    """External service error - issues with third-party services."""
    
    def __init__(self, message: str, service_name: Optional[str] = None, service_status: Optional[int] = None, error_response: Optional[str] = None):
        details = {}
        if service_name:
            details["service_name"] = service_name
        if service_status:
            details["service_status"] = service_status
        if error_response:
            # Truncate long error responses
            details["error_response"] = error_response[:500] + "..." if len(error_response) > 500 else error_response
        super().__init__(message, status_code=502, details=details)


class ResourceExhaustedError(TikTokAPIException):
    """Resource exhausted error - system resources (memory, disk, etc.) exhausted."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, current_usage: Optional[str] = None, limit: Optional[str] = None):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if current_usage:
            details["current_usage"] = current_usage
        if limit:
            details["limit"] = limit
        super().__init__(message, status_code=507, details=details, log_level="CRITICAL")


class BusinessLogicError(TikTokAPIException):
    """Business logic error - request violates business rules."""
    
    def __init__(self, message: str, rule_violated: Optional[str] = None, suggested_action: Optional[str] = None):
        details = {}
        if rule_violated:
            details["rule_violated"] = rule_violated
        if suggested_action:
            details["suggested_action"] = suggested_action
        super().__init__(message, status_code=422, details=details, log_level="WARNING")


# Convenience aliases for backwards compatibility
ValidationError = TikTokValidationError
TimeoutError = TikTokTimeoutError

from functools import wraps
from typing import Callable, Any, Optional, Type, Tuple
import time
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log
)


logger = logging.getLogger(__name__)


class SycoBenchError(Exception):
    """Base exception for SycoBench"""
    pass


class APIError(SycoBenchError):
    """General API error"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    pass


class AuthenticationError(APIError):
    """Authentication failed error"""
    pass


class ModelNotFoundError(APIError):
    """Model not found or not accessible"""
    pass


class InvalidRequestError(APIError):
    """Invalid request parameters"""
    pass


class ServerError(APIError):
    """Server-side error (5xx)"""
    pass


def parse_api_error(exception: Exception, provider: str) -> APIError:
    """Parse provider-specific exceptions into standardized errors"""
    error_str = str(exception).lower()
    error_type = type(exception).__name__
    
    # Rate limit errors
    if any(x in error_str for x in ["rate_limit", "429", "quota", "too many requests"]):
        return RateLimitError(f"{provider} rate limit exceeded: {str(exception)}", 429)
    
    # Authentication errors
    if any(x in error_str for x in ["401", "403", "unauthorized", "forbidden", "invalid_api_key", "authentication"]):
        return AuthenticationError(f"{provider} authentication failed: {str(exception)}")
    
    # Model not found errors
    if any(x in error_str for x in ["model_not_found", "404", "not found", "does not exist"]):
        return ModelNotFoundError(f"{provider} model not found: {str(exception)}", 404)
    
    # Invalid request errors
    if any(x in error_str for x in ["400", "bad request", "invalid", "validation"]):
        return InvalidRequestError(f"{provider} invalid request: {str(exception)}", 400)
    
    # Server errors (including 529 overloaded)
    if any(x in error_str for x in ["500", "502", "503", "504", "529", "server_error", "internal", "overloaded"]):
        return ServerError(f"{provider} server error: {str(exception)}", 500)
    
    # Default to general API error
    return APIError(f"{provider} API error: {str(exception)}")


def handle_api_errors(provider: str, max_retries: int = 3):
    """Decorator to handle API errors with automatic retry logic"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Parse the error
                    api_error = parse_api_error(e, provider)
                    last_exception = api_error
                    
                    # Log the error
                    logger.warning(f"API error on attempt {attempt + 1}/{max_retries}: {api_error}")
                    
                    # Don't retry on authentication errors
                    if isinstance(api_error, AuthenticationError):
                        raise api_error
                    
                    # Don't retry on invalid requests (they won't succeed)
                    if isinstance(api_error, InvalidRequestError):
                        raise api_error
                    
                    # For rate limits, use exponential backoff
                    if isinstance(api_error, RateLimitError):
                        if attempt < max_retries - 1:
                            backoff_time = min(60, 2 ** (attempt + 1))
                            logger.info(f"Rate limited, waiting {backoff_time}s before retry")
                            time.sleep(backoff_time)
                            continue
                    
                    # For server errors (including overloaded), use backoff
                    if isinstance(api_error, ServerError):
                        if attempt < max_retries - 1:
                            backoff_time = min(30, 2 ** (attempt + 2))  # 4s, 8s, 16s
                            logger.info(f"Server error/overloaded, waiting {backoff_time}s before retry")
                            time.sleep(backoff_time)
                            continue
                    
                    # If it's the last attempt, raise
                    if attempt == max_retries - 1:
                        raise api_error
            
            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


# Using tenacity for more sophisticated retry logic
def create_retry_decorator(
    provider: str,
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 60.0
):
    """Create a retry decorator with exponential backoff using tenacity"""
    
    def should_retry(exception: Exception) -> bool:
        """Determine if we should retry based on the exception type"""
        api_error = parse_api_error(exception, provider)
        
        # Don't retry authentication or invalid request errors
        if isinstance(api_error, (AuthenticationError, InvalidRequestError, ModelNotFoundError)):
            return False
        
        # Retry rate limits and server errors
        return isinstance(api_error, (RateLimitError, ServerError))
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(Exception) if should_retry else retry_if_exception_type(type(None)),
        before=before_log(logger, logging.DEBUG),
        after=after_log(logger, logging.DEBUG)
    )


# Context manager for handling errors
class ErrorHandler:
    def __init__(self, provider: str, operation: str):
        self.provider = provider
        self.operation = operation
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            api_error = parse_api_error(exc_val, self.provider)
            logger.error(f"Error during {self.operation}: {api_error}")
            raise api_error
        return False


# Helper function to safely execute API calls
def safe_api_call(
    func: Callable,
    provider: str,
    operation: str,
    max_retries: int = 3,
    *args,
    **kwargs
) -> Any:
    """Safely execute an API call with error handling and retries"""
    
    @handle_api_errors(provider, max_retries)
    def _wrapped_call():
        with ErrorHandler(provider, operation):
            return func(*args, **kwargs)
    
    return _wrapped_call()
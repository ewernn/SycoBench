import time
import asyncio
from functools import wraps
from typing import Dict, Callable, Any
from collections import defaultdict
from datetime import datetime, timedelta
import threading


class RateLimiter:
    def __init__(self):
        self.last_call_times: Dict[str, float] = {}
        self.call_counts: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()
    
    def _clean_old_calls(self, model_type: str):
        """Remove calls older than 1 minute from tracking"""
        current_time = time.time()
        self.call_counts[model_type] = [
            call_time for call_time in self.call_counts[model_type]
            if current_time - call_time < 60
        ]
    
    def get_wait_time(self, model_type: str, rpm_limit: int) -> float:
        """Calculate how long to wait before the next call"""
        with self.lock:
            current_time = time.time()
            self._clean_old_calls(model_type)
            
            # Check if we've exceeded the rate limit
            if len(self.call_counts[model_type]) >= rpm_limit:
                # Find the oldest call in the current window
                oldest_call = min(self.call_counts[model_type])
                wait_time = 60 - (current_time - oldest_call) + 0.1  # Add small buffer
                return max(0, wait_time)
            
            # Calculate minimum interval between calls
            min_interval = 60.0 / rpm_limit
            
            if model_type in self.last_call_times:
                elapsed = current_time - self.last_call_times[model_type]
                if elapsed < min_interval:
                    return min_interval - elapsed
            
            return 0
    
    def record_call(self, model_type: str):
        """Record that a call was made"""
        with self.lock:
            current_time = time.time()
            self.last_call_times[model_type] = current_time
            self.call_counts[model_type].append(current_time)
            self._clean_old_calls(model_type)
    
    def limit(self, model_type: str, rpm_limit: int):
        """Decorator to rate limit function calls"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                wait_time = self.get_wait_time(model_type, rpm_limit)
                if wait_time > 0:
                    time.sleep(wait_time)
                
                result = func(*args, **kwargs)
                self.record_call(model_type)
                return result
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                wait_time = self.get_wait_time(model_type, rpm_limit)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                
                result = await func(*args, **kwargs)
                self.record_call(model_type)
                return result
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def get_stats(self, model_type: str) -> Dict[str, Any]:
        """Get current rate limiting statistics"""
        with self.lock:
            self._clean_old_calls(model_type)
            return {
                "model_type": model_type,
                "calls_in_last_minute": len(self.call_counts[model_type]),
                "last_call_time": self.last_call_times.get(model_type, None)
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


class ModelSpecificRateLimiter:
    """Rate limiter that automatically uses model-specific limits from config"""
    
    def __init__(self):
        self.rate_limiter = rate_limiter
    
    def limit_for_model(self, model_config):
        """Create a rate limiter decorator for a specific model configuration"""
        def decorator(func: Callable) -> Callable:
            return self.rate_limiter.limit(
                model_config.identifier,
                model_config.rate_limit_rpm
            )(func)
        return decorator


# Convenience function for rate limiting with automatic retry
def rate_limited_retry(model_type: str, rpm_limit: int, max_retries: int = 3):
    """Decorator that combines rate limiting with retry logic"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    # Apply rate limiting
                    wait_time = rate_limiter.get_wait_time(model_type, rpm_limit)
                    if wait_time > 0:
                        time.sleep(wait_time)
                    
                    # Try the function
                    result = func(*args, **kwargs)
                    rate_limiter.record_call(model_type)
                    return result
                
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Check if it's a rate limit error
                    if any(x in error_str for x in ["429", "rate_limit", "quota", "too many requests"]):
                        # Exponential backoff for rate limit errors
                        backoff_time = min(60, 2 ** attempt)
                        time.sleep(backoff_time)
                        continue
                    
                    # For other errors, shorter retry delay
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    else:
                        raise
            
            # If we exhausted all retries, raise the last exception
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator
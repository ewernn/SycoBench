"""
Async rate limiter using semaphores for parallel API calls.
"""
import asyncio
import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class AsyncRateLimiter:
    """
    Rate limiter for async API calls using token bucket algorithm.
    Thread-safe for async operations.
    """

    def __init__(self):
        self._limiters: Dict[str, 'ModelRateLimiter'] = {}

    def get_limiter(self, model_id: str, rpm: int) -> 'ModelRateLimiter':
        """Get or create a rate limiter for a specific model"""
        if model_id not in self._limiters:
            self._limiters[model_id] = ModelRateLimiter(model_id, rpm)
        return self._limiters[model_id]


class ModelRateLimiter:
    """
    Rate limiter for a specific model.
    Uses semaphore + time-based throttling.
    """

    def __init__(self, model_id: str, rpm: int):
        self.model_id = model_id
        self.rpm = rpm
        self.delay = 60.0 / rpm  # Seconds between requests
        self._semaphore = asyncio.Semaphore(rpm)  # Max concurrent requests
        self._last_call = 0.0
        self._lock = asyncio.Lock()

        logger.debug(f"Rate limiter created for {model_id}: {rpm} RPM, {self.delay:.3f}s delay")

    async def acquire(self):
        """
        Acquire permission to make an API call.
        Blocks until rate limit allows.
        """
        async with self._semaphore:
            async with self._lock:
                # Calculate time since last call
                now = time.time()
                time_since_last = now - self._last_call

                # If we need to wait, sleep
                if time_since_last < self.delay:
                    wait_time = self.delay - time_since_last
                    logger.debug(f"Rate limiting {self.model_id}: waiting {wait_time:.3f}s")
                    await asyncio.sleep(wait_time)

                self._last_call = time.time()


# Global async rate limiter instance
async_rate_limiter = AsyncRateLimiter()

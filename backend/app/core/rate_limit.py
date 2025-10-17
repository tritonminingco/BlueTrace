"""Redis-based rate limiting with sliding window."""

import time

import redis.asyncio as redis
from fastapi import Request

from app.core.config import settings
from app.core.errors import RateLimitError
from app.models.api_key import APIKey


class RateLimiter:
    """Redis-based sliding window rate limiter."""

    def __init__(self) -> None:
        """Initialize rate limiter with Redis connection."""
        self.redis_client: redis.Redis | None = None

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        self.redis_client = redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if request is within rate limit using sliding window.

        Args:
            key: Unique identifier for rate limit bucket
            limit: Maximum number of requests allowed
            window: Time window in seconds

        Returns:
            True if within limit, False otherwise
        """
        if not self.redis_client:
            # If Redis is not available, allow the request
            return True

        now = time.time()
        window_start = now - window

        # Redis key for this bucket
        bucket_key = f"rate_limit:{key}"

        try:
            # Remove old entries outside the window
            await self.redis_client.zremrangebyscore(bucket_key, 0, window_start)

            # Count current requests in window
            current_count = await self.redis_client.zcard(bucket_key)

            if current_count >= limit:
                return False

            # Add current request
            await self.redis_client.zadd(bucket_key, {str(now): now})

            # Set expiration on the key
            await self.redis_client.expire(bucket_key, window + 10)

            return True

        except Exception:
            # If Redis fails, allow the request
            return True

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        """
        Get remaining requests in current window.

        Args:
            key: Unique identifier for rate limit bucket
            limit: Maximum number of requests allowed
            window: Time window in seconds

        Returns:
            Number of requests remaining
        """
        if not self.redis_client:
            return limit

        now = time.time()
        window_start = now - window
        bucket_key = f"rate_limit:{key}"

        try:
            await self.redis_client.zremrangebyscore(bucket_key, 0, window_start)
            current_count = await self.redis_client.zcard(bucket_key)
            return max(0, limit - current_count)
        except Exception:
            return limit


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_api_rate_limit(request: Request, api_key: APIKey) -> None:
    """
    Dependency to check rate limits for API requests.

    Args:
        request: FastAPI request object
        api_key: Current API key

    Raises:
        RateLimitError: If rate limit is exceeded
    """
    # Get rate limit config for this plan
    rate_limits = settings.get_rate_limits()
    plan_config = rate_limits.get(api_key.plan)

    if not plan_config:
        # Default to free plan if unknown
        plan_config = rate_limits["free"]

    # Create rate limit key based on API key ID
    limit_key = f"api_key:{api_key.id}"

    # Check rate limit
    allowed = await rate_limiter.check_rate_limit(
        limit_key, plan_config.requests, plan_config.window
    )

    if not allowed:
        remaining = await rate_limiter.get_remaining(
            limit_key, plan_config.requests, plan_config.window
        )

        raise RateLimitError(
            message=f"Rate limit exceeded for {api_key.plan} plan",
            hint=f"Limit: {plan_config.requests} requests per {plan_config.window}s. "
            f"Remaining: {remaining}",
        )

"""
Async Redis client wrapper for Sentinel.

Design decisions:
  - All cache operations are silently fault-tolerant. If Redis is down, every
    function returns None/no-ops so the API degrades to direct PostgreSQL reads
    rather than returning 500. This is a deliberate trade-off: slightly stale
    or uncached data is better than a full dashboard outage.
  - JSON serialization keeps cached values human-readable and debuggable via
    `redis-cli GET sentinel:dashboard:summary` during an incident.

Why Redis for the dashboard summary:
  Building the summary requires N+1 queries (one per service for its latest
  health check). At 50 services polled every 30 s, that's ~100 DB roundtrips
  per refresh without caching. Redis reduces the dashboard read path to a
  single O(1) key lookup for the entire TTL window.
"""

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Module-level singleton — created once, reused across all requests
_client: aioredis.Redis | None = None

# ── Cache key constants ────────────────────────────────────────────────────────
DASHBOARD_SUMMARY_KEY = "sentinel:dashboard:summary"


def get_redis_client() -> aioredis.Redis:
    """Return (or create) the shared async Redis client."""
    global _client
    if _client is None:
        _client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _client


async def cache_get(key: str) -> Any | None:
    """
    Fetch a JSON-decoded value from Redis.
    Returns None on cache miss OR if Redis is unavailable (graceful fallback).
    """
    try:
        client = get_redis_client()
        raw = await client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Redis GET failed (key=%s): %s — falling back to DB", key, exc)
        return None


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    """
    Store a JSON-encoded value in Redis with optional TTL (seconds).
    Errors are logged and swallowed — a failed write must not break the response.
    """
    if ttl is None:
        ttl = settings.CACHE_TTL_SECONDS
    try:
        client = get_redis_client()
        await client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as exc:
        logger.warning("Redis SET failed (key=%s): %s", key, exc)


async def cache_delete(key: str) -> None:
    """
    Invalidate a cache entry.
    Called after maintenance mode changes so the dashboard reflects the new
    state immediately without waiting for TTL expiry.
    """
    try:
        client = get_redis_client()
        await client.delete(key)
    except Exception as exc:
        logger.warning("Redis DELETE failed (key=%s): %s", key, exc)

"""Caching service for analysis results"""

import json
import hashlib
import aioredis
import logging
from typing import Optional
from datetime import timedelta

from app.models import CROAnalysisResponse

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis = None
        self.memory_cache = {}  # Fallback in-memory cache
        self.cache_ttl = 24 * 60 * 60  # 24 hours
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis = await aioredis.from_url(redis_url)
            await self.redis.ping()
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.warning(f"⚠️  Redis not available, using memory cache: {e}")
            self.redis = None
    
    def _generate_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"cro:analysis:{url_hash}"
    
    async def get_cached_analysis(self, url: str) -> Optional[CROAnalysisResponse]:
        """Get cached analysis result"""
        cache_key = self._generate_cache_key(url)
        
        try:
            # Try Redis first
            if self.redis:
                cached_data = await self.redis.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    return CROAnalysisResponse(**data)
            
            # Fallback to memory cache
            if cache_key in self.memory_cache:
                return self.memory_cache[cache_key]
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    async def cache_analysis(self, url: str, analysis: CROAnalysisResponse):
        """Cache analysis result"""
        cache_key = self._generate_cache_key(url)
        
        try:
            # Cache in Redis
            if self.redis:
                cached_data = analysis.json()
                await self.redis.setex(cache_key, self.cache_ttl, cached_data)
            
            # Also cache in memory (with size limit)
            if len(self.memory_cache) < 100:  # Limit memory cache size
                self.memory_cache[cache_key] = analysis
            
            logger.info(f"📦 Cached analysis for {url}")
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def invalidate_cache(self, url: str):
        """Invalidate cached analysis"""
        cache_key = self._generate_cache_key(url)
        
        try:
            if self.redis:
                await self.redis.delete(cache_key)
            
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
                
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self.redis is not None
    
    async def close(self):
        """Close cache connections"""
        if self.redis:
            await self.redis.close()

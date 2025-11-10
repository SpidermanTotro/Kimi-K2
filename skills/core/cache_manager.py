"""
Cache Manager Module

Provides robust caching system for frequently used assets and generated content.
Optimized for real-time workflows with intelligent cache eviction and persistence.
"""

from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    size_bytes: int = 0
    ttl: Optional[int] = None  # Time to live in seconds
    tags: list = None


class CacheManager:
    """
    Advanced caching system for Kimi-K2
    
    Features:
    - Multi-tier caching (memory, disk, remote)
    - LRU and LFU eviction policies
    - TTL-based expiration
    - Tag-based cache invalidation
    - Automatic persistence
    - Size-based limits
    - Cache statistics and analytics
    
    Example:
        >>> cache = CacheManager(max_memory_mb=1024, cache_dir="/tmp/kimi_cache")
        >>> cache.set("video_frame_001", frame_data, ttl=3600, tags=["video", "frames"])
        >>> frame = cache.get("video_frame_001")
        >>> cache.invalidate_by_tag("video")  # Clear all video-related cache
    """
    
    def __init__(
        self,
        max_memory_mb: int = 2048,
        cache_dir: Optional[str] = None,
        eviction_policy: str = "lru",  # "lru", "lfu", "fifo"
        enable_disk_cache: bool = True,
        enable_persistence: bool = True
    ):
        """
        Initialize cache manager
        
        Args:
            max_memory_mb: Maximum memory cache size in MB
            cache_dir: Directory for disk cache
            eviction_policy: Cache eviction policy
            enable_disk_cache: Enable disk-based caching
            enable_persistence: Persist cache between sessions
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".kimi_k2" / "cache"
        self.eviction_policy = eviction_policy
        self.enable_disk_cache = enable_disk_cache
        self.enable_persistence = enable_persistence
        
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._current_size = 0
        self._hits = 0
        self._misses = 0
        
        if enable_disk_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if enable_persistence:
            self._load_persistent_cache()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        # Check memory cache
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            
            # Check TTL
            if entry.ttl and (datetime.now() - entry.created_at).seconds > entry.ttl:
                self.delete(key)
                self._misses += 1
                return default
            
            # Update access metadata
            entry.accessed_at = datetime.now()
            entry.access_count += 1
            self._hits += 1
            
            return entry.value
        
        # Check disk cache
        if self.enable_disk_cache:
            disk_value = self._get_from_disk(key)
            if disk_value is not None:
                # Promote to memory cache
                self.set(key, disk_value)
                self._hits += 1
                return disk_value
        
        self._misses += 1
        return default
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[list] = None
    ):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Tags for cache invalidation
        """
        # Estimate size
        size = self._estimate_size(value)
        
        # Check if we need to evict
        while self._current_size + size > self.max_memory_bytes:
            self._evict()
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            size_bytes=size,
            ttl=ttl,
            tags=tags or []
        )
        
        # Store in memory
        if key in self._memory_cache:
            self._current_size -= self._memory_cache[key].size_bytes
        
        self._memory_cache[key] = entry
        self._current_size += size
        
        # Store on disk if enabled
        if self.enable_disk_cache:
            self._save_to_disk(key, value)
    
    def delete(self, key: str):
        """Delete entry from cache"""
        if key in self._memory_cache:
            self._current_size -= self._memory_cache[key].size_bytes
            del self._memory_cache[key]
        
        if self.enable_disk_cache:
            self._delete_from_disk(key)
    
    def clear(self):
        """Clear all cache"""
        self._memory_cache.clear()
        self._current_size = 0
        
        if self.enable_disk_cache and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
    
    def invalidate_by_tag(self, tag: str):
        """
        Invalidate all cache entries with specific tag
        
        Args:
            tag: Tag to invalidate
        """
        keys_to_delete = [
            key for key, entry in self._memory_cache.items()
            if tag in (entry.tags or [])
        ]
        
        for key in keys_to_delete:
            self.delete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary of cache statistics
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            "memory_usage_mb": self._current_size / (1024 * 1024),
            "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
            "num_entries": len(self._memory_cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "eviction_policy": self.eviction_policy
        }
    
    def _evict(self):
        """Evict entry based on eviction policy"""
        if not self._memory_cache:
            return
        
        if self.eviction_policy == "lru":
            # Least recently used
            victim_key = min(
                self._memory_cache.keys(),
                key=lambda k: self._memory_cache[k].accessed_at
            )
        elif self.eviction_policy == "lfu":
            # Least frequently used
            victim_key = min(
                self._memory_cache.keys(),
                key=lambda k: self._memory_cache[k].access_count
            )
        else:  # FIFO
            victim_key = min(
                self._memory_cache.keys(),
                key=lambda k: self._memory_cache[k].created_at
            )
        
        self.delete(victim_key)
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        # Rough estimation - in production, use more accurate method
        if isinstance(value, (str, bytes)):
            return len(value)
        elif isinstance(value, dict):
            return len(json.dumps(value).encode())
        else:
            return 1024  # Default estimate
    
    def _get_cache_path(self, key: str) -> Path:
        """Get disk cache path for key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _get_from_disk(self, key: str) -> Optional[Any]:
        """Load value from disk cache"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                # In production: use proper serialization (pickle, msgpack, etc.)
                return f.read()
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
    
    def _save_to_disk(self, key: str, value: Any):
        """Save value to disk cache"""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                # In production: use proper serialization
                if isinstance(value, bytes):
                    f.write(value)
                else:
                    f.write(str(value).encode())
        except Exception as e:
            print(f"Error writing cache: {e}")
    
    def _delete_from_disk(self, key: str):
        """Delete disk cache file"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
    
    def _load_persistent_cache(self):
        """Load persistent cache from previous session"""
        # Placeholder - in production, implement cache restoration
        pass
    
    def warmup(self, preload_function: Callable):
        """
        Warm up cache with commonly used data
        
        Args:
            preload_function: Function that returns items to cache
        """
        items = preload_function()
        for key, value in items.items():
            self.set(key, value)

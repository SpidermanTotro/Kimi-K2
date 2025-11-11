"""
Optimization Helpers
Utilities for optimizing AI system performance
"""

from typing import Dict, List, Optional, Any, Callable
import functools


class OptimizationHelpers:
    """
    Helpers for optimizing AI system performance.
    
    Features:
    - Caching
    - Batch processing
    - Rate limiting
    - Resource management
    """
    
    def __init__(self):
        """Initialize optimization helpers."""
        self.cache: Dict[str, Any] = {}
        self.cache_stats = {"hits": 0, "misses": 0}
    
    @staticmethod
    def cache_response(ttl: Optional[int] = None):
        """
        Decorator to cache function responses.
        
        Args:
            ttl: Time-to-live in seconds (None = no expiration)
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable):
            cache = {}
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                key = str((args, tuple(sorted(kwargs.items()))))
                
                if key in cache:
                    return cache[key]
                
                result = func(*args, **kwargs)
                cache[key] = result
                
                return result
            
            wrapper.cache = cache
            wrapper.cache_clear = lambda: cache.clear()
            
            return wrapper
        
        return decorator
    
    def batch_process(
        self,
        items: List[Any],
        processor: Callable,
        batch_size: int = 10,
    ) -> List[Any]:
        """
        Process items in batches for efficiency.
        
        Args:
            items: Items to process
            processor: Function to process each batch
            batch_size: Size of each batch
            
        Returns:
            Processed results
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = processor(batch)
            
            if isinstance(batch_results, list):
                results.extend(batch_results)
            else:
                results.append(batch_results)
        
        return results
    
    @staticmethod
    def rate_limit(calls_per_second: int):
        """
        Decorator to rate limit function calls.
        
        Args:
            calls_per_second: Maximum calls per second
            
        Returns:
            Decorated function
        """
        import time
        
        def decorator(func: Callable):
            last_called = [0.0]
            min_interval = 1.0 / calls_per_second
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                elapsed = time.time() - last_called[0]
                
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)
                
                last_called[0] = time.time()
                return func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def parallel_process(
        self,
        items: List[Any],
        processor: Callable,
        max_workers: int = 4,
    ) -> List[Any]:
        """
        Process items in parallel.
        
        Args:
            items: Items to process
            processor: Function to process each item
            max_workers: Maximum parallel workers
            
        Returns:
            Processed results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {
                executor.submit(processor, item): item 
                for item in items
            }
            
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})
        
        return results
    
    def optimize_prompt(
        self,
        prompt: str,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Optimize prompt for efficiency.
        
        Args:
            prompt: Original prompt
            max_length: Maximum prompt length
            
        Returns:
            Optimized prompt
        """
        optimized = prompt.strip()
        
        # Remove extra whitespace
        optimized = " ".join(optimized.split())
        
        # Truncate if needed
        if max_length and len(optimized) > max_length:
            optimized = optimized[:max_length] + "..."
        
        return optimized
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def optimize_batch_requests(
        self,
        requests: List[Dict[str, Any]],
        max_tokens_per_batch: int = 4000,
    ) -> List[List[Dict[str, Any]]]:
        """
        Optimize batching of requests by token limits.
        
        Args:
            requests: List of requests
            max_tokens_per_batch: Maximum tokens per batch
            
        Returns:
            Optimized batches
        """
        batches = []
        current_batch = []
        current_tokens = 0
        
        for request in requests:
            # Estimate tokens
            request_text = str(request.get("content", ""))
            request_tokens = self.estimate_tokens(request_text)
            
            if current_tokens + request_tokens > max_tokens_per_batch and current_batch:
                batches.append(current_batch)
                current_batch = [request]
                current_tokens = request_tokens
            else:
                current_batch.append(request)
                current_tokens += request_tokens
        
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    @staticmethod
    def memoize_expensive_calls(func: Callable) -> Callable:
        """
        Memoize expensive function calls.
        
        Args:
            func: Function to memoize
            
        Returns:
            Memoized function
        """
        return functools.lru_cache(maxsize=128)(func)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get optimization statistics.
        
        Returns:
            Optimization stats
        """
        cache_total = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / cache_total 
            if cache_total > 0 else 0
        )
        
        return {
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "cache_hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        self.cache_stats = {"hits": 0, "misses": 0}

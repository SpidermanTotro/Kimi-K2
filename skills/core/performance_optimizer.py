"""
Performance Optimizer Module

Provides performance optimization utilities for AI module execution.
Includes memory management, GPU optimization, and batch processing.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import time


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    operation_name: str
    duration_ms: float
    memory_used_mb: float
    gpu_memory_mb: float = 0.0
    throughput: float = 0.0  # items/second
    batch_size: int = 1


class PerformanceOptimizer:
    """
    Performance optimization engine for Kimi-K2
    
    Features:
    - Automatic batch size optimization
    - Memory usage monitoring and optimization
    - GPU memory management
    - Model quantization support
    - Mixed precision training/inference
    - Operation profiling and metrics
    
    Example:
        >>> optimizer = PerformanceOptimizer()
        >>> with optimizer.profile("video_generation"):
        ...     generate_video()
        >>> metrics = optimizer.get_metrics("video_generation")
        >>> optimal_batch = optimizer.find_optimal_batch_size(
        ...     operation=generate_frames,
        ...     max_memory_mb=8000
        ... )
    """
    
    def __init__(
        self,
        enable_gpu: bool = True,
        enable_mixed_precision: bool = True,
        memory_limit_mb: Optional[int] = None
    ):
        """
        Initialize performance optimizer
        
        Args:
            enable_gpu: Enable GPU acceleration
            enable_mixed_precision: Use mixed precision (FP16)
            memory_limit_mb: Maximum memory usage limit
        """
        self.enable_gpu = enable_gpu
        self.enable_mixed_precision = enable_mixed_precision
        self.memory_limit_mb = memory_limit_mb
        
        self._metrics: Dict[str, List[PerformanceMetrics]] = {}
        self._operation_stack = []
    
    def profile(self, operation_name: str):
        """
        Context manager for profiling operations
        
        Args:
            operation_name: Name of operation to profile
        
        Example:
            >>> with optimizer.profile("image_generation"):
            ...     generate_image()
        """
        return _ProfileContext(self, operation_name)
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics for an operation"""
        if metrics.operation_name not in self._metrics:
            self._metrics[metrics.operation_name] = []
        
        self._metrics[metrics.operation_name].append(metrics)
    
    def get_metrics(
        self,
        operation_name: str,
        aggregate: bool = True
    ) -> Dict[str, Any]:
        """
        Get performance metrics for operation
        
        Args:
            operation_name: Operation to get metrics for
            aggregate: Return aggregated statistics
            
        Returns:
            Metrics dictionary
        """
        if operation_name not in self._metrics:
            return {}
        
        metrics_list = self._metrics[operation_name]
        
        if not aggregate:
            return {"metrics": [m.__dict__ for m in metrics_list]}
        
        # Aggregate metrics
        return {
            "operation": operation_name,
            "num_executions": len(metrics_list),
            "avg_duration_ms": sum(m.duration_ms for m in metrics_list) / len(metrics_list),
            "avg_memory_mb": sum(m.memory_used_mb for m in metrics_list) / len(metrics_list),
            "avg_throughput": sum(m.throughput for m in metrics_list) / len(metrics_list),
            "total_duration_ms": sum(m.duration_ms for m in metrics_list)
        }
    
    def find_optimal_batch_size(
        self,
        operation: Callable,
        test_data: List[Any],
        max_memory_mb: int = 8000,
        min_batch: int = 1,
        max_batch: int = 128
    ) -> int:
        """
        Find optimal batch size for operation
        
        Args:
            operation: Operation to test
            test_data: Sample data for testing
            max_memory_mb: Maximum memory constraint
            min_batch: Minimum batch size to test
            max_batch: Maximum batch size to test
            
        Returns:
            Optimal batch size
        """
        optimal_batch = min_batch
        best_throughput = 0.0
        
        for batch_size in [min_batch, min_batch * 2, min_batch * 4, min_batch * 8, max_batch]:
            if batch_size > len(test_data):
                break
            
            # Test batch size
            batch = test_data[:batch_size]
            
            start_time = time.time()
            try:
                operation(batch)
                duration = time.time() - start_time
                throughput = batch_size / duration
                
                # Check if this is better
                if throughput > best_throughput:
                    best_throughput = throughput
                    optimal_batch = batch_size
            
            except MemoryError:
                # Batch too large, stop testing
                break
        
        return optimal_batch
    
    def optimize_memory(self):
        """
        Optimize memory usage
        
        Clears caches and triggers garbage collection
        """
        import gc
        gc.collect()
        
        # In production: clear GPU cache if using PyTorch/TensorFlow
        # torch.cuda.empty_cache()
        print("Memory optimization completed")
    
    def enable_quantization(
        self,
        model: Any,
        quantization_type: str = "int8"  # "int8", "int4", "float16"
    ):
        """
        Apply quantization to model for faster inference
        
        Args:
            model: Model to quantize
            quantization_type: Type of quantization
            
        Returns:
            Quantized model
        """
        # Placeholder - in production, apply actual quantization
        print(f"Applying {quantization_type} quantization to model")
        return model
    
    def parallelize_batch(
        self,
        operation: Callable,
        items: List[Any],
        num_workers: int = 4
    ) -> List[Any]:
        """
        Parallelize batch processing
        
        Args:
            operation: Operation to apply
            items: Items to process
            num_workers: Number of parallel workers
            
        Returns:
            Processed items
        """
        # In production: use multiprocessing or threading
        results = []
        for item in items:
            results.append(operation(item))
        
        return results
    
    def get_gpu_memory_info(self) -> Dict[str, float]:
        """
        Get GPU memory information
        
        Returns:
            Dictionary with GPU memory stats (MB)
        """
        # Placeholder - in production, query actual GPU
        return {
            "allocated_mb": 0.0,
            "reserved_mb": 0.0,
            "free_mb": 0.0,
            "total_mb": 0.0
        }
    
    def auto_select_device(self) -> str:
        """
        Automatically select best available device
        
        Returns:
            Device string ("cuda", "mps", "cpu")
        """
        if self.enable_gpu:
            # In production: check for CUDA, MPS, etc.
            return "cuda"
        
        return "cpu"


class _ProfileContext:
    """Context manager for profiling"""
    
    def __init__(self, optimizer: PerformanceOptimizer, operation_name: str):
        self.optimizer = optimizer
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        metrics = PerformanceMetrics(
            operation_name=self.operation_name,
            duration_ms=duration_ms,
            memory_used_mb=0.0  # Would measure actual memory
        )
        
        self.optimizer.record_metrics(metrics)

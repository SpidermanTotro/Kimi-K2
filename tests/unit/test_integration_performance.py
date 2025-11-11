"""
Unit tests for Integration and Performance modules
"""

import pytest
from unittest.mock import Mock, patch
from kimi_k2.integration import MoonAIIntegration
from kimi_k2.performance import BenchmarkingTools, OptimizationHelpers
import time


class TestMoonAIIntegration:
    """Test suite for MoonAIIntegration."""
    
    @patch('kimi_k2.integration.moon_ai.KimiClient')
    def test_register_integration(self, mock_client_class):
        """Test registering an integration."""
        mock_client_class.return_value = Mock()
        
        integration = MoonAIIntegration()
        result = integration.register_integration("test_ai", {"endpoint": "test"})
        
        assert result["status"] == "success"
        assert result["integration"] == "test_ai"
        assert result["active"] is True
    
    @patch('kimi_k2.integration.moon_ai.KimiClient')
    def test_get_integration_status(self, mock_client_class):
        """Test getting integration status."""
        mock_client_class.return_value = Mock()
        
        integration = MoonAIIntegration()
        integration.register_integration("test_ai", {"endpoint": "test"})
        
        status = integration.get_integration_status()
        
        assert status["status"] == "success"
        assert "test_ai" in status["integrations"]
    
    @patch('kimi_k2.integration.moon_ai.KimiClient')
    def test_unified_query(self, mock_client_class):
        """Test unified query across systems."""
        mock_client = Mock()
        mock_client.simple_chat.return_value = "Kimi response"
        mock_client_class.return_value = mock_client
        
        integration = MoonAIIntegration(kimi_client=mock_client)
        integration.register_integration("system1", {})
        
        result = integration.unified_query("Test query", combine_results=False)
        
        assert result["status"] == "success"
        assert "kimi_k2" in result["results"]
    
    @patch('kimi_k2.integration.moon_ai.KimiClient')
    def test_enable_disable_integration(self, mock_client_class):
        """Test enabling and disabling integrations."""
        mock_client_class.return_value = Mock()
        
        integration = MoonAIIntegration()
        integration.register_integration("test_ai", {})
        
        # Disable
        result = integration.disable_integration("test_ai")
        assert result["active"] is False
        
        # Enable
        result = integration.enable_integration("test_ai")
        assert result["active"] is True


class TestBenchmarkingTools:
    """Test suite for BenchmarkingTools."""
    
    def test_measure_latency(self):
        """Test latency measurement."""
        benchmark = BenchmarkingTools()
        
        def test_func(x):
            time.sleep(0.01)
            return x * 2
        
        result = benchmark.measure_latency(test_func, 10, iterations=3)
        
        assert result["metric"] == "latency"
        assert result["iterations"] == 3
        assert result["average_ms"] > 0
        assert len(result["all_latencies_ms"]) == 3
    
    def test_measure_throughput(self):
        """Test throughput measurement."""
        benchmark = BenchmarkingTools()
        
        def test_func(x):
            return x * 2
        
        test_data = list(range(100))
        result = benchmark.measure_throughput(test_func, test_data)
        
        assert result["metric"] == "throughput"
        assert result["completed"] == 100
        assert result["errors"] == 0
        assert result["requests_per_second"] > 0
    
    def test_compare_performance(self):
        """Test performance comparison."""
        benchmark = BenchmarkingTools()
        
        systems = {
            "fast": lambda x: x * 2,
            "slow": lambda x: (time.sleep(0.001), x * 2)[1],
        }
        
        result = benchmark.compare_performance(systems, 100, iterations=2)
        
        assert "comparison" in result
        assert "ranked" in result
        assert result["fastest"] in ["fast", "slow"]
    
    def test_quality_benchmark(self):
        """Test quality benchmarking."""
        benchmark = BenchmarkingTools()
        
        def test_func(x):
            return x * 2
        
        def evaluator(result, expected):
            return 1.0 if result == expected else 0.0
        
        test_cases = [
            {"input": 2, "expected": 4},
            {"input": 5, "expected": 10},
            {"input": 10, "expected": 20},
        ]
        
        result = benchmark.quality_benchmark(test_func, test_cases, evaluator)
        
        assert result["metric"] == "quality"
        assert result["test_cases"] == 3
        assert result["average_score"] == 1.0
    
    def test_generate_report(self):
        """Test report generation."""
        benchmark = BenchmarkingTools()
        
        def test_func(x):
            return x * 2
        
        benchmark.measure_latency(test_func, 10, iterations=2)
        
        report = benchmark.generate_report()
        
        assert "Benchmark Report" in report
        assert "Latency Benchmarks" in report


class TestOptimizationHelpers:
    """Test suite for OptimizationHelpers."""
    
    def test_cache_response_decorator(self):
        """Test cache response decorator."""
        optimizer = OptimizationHelpers()
        
        call_count = [0]
        
        @optimizer.cache_response()
        def expensive_func(x):
            call_count[0] += 1
            return x * 2
        
        # First call
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count[0] == 1
        
        # Second call (cached)
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count[0] == 1  # Not incremented
        
        # Different input
        result3 = expensive_func(10)
        assert result3 == 20
        assert call_count[0] == 2
    
    def test_batch_process(self):
        """Test batch processing."""
        optimizer = OptimizationHelpers()
        
        items = list(range(25))
        
        def processor(batch):
            return [x * 2 for x in batch]
        
        results = optimizer.batch_process(items, processor, batch_size=10)
        
        assert len(results) == 25
        assert results[0] == 0
        assert results[24] == 48
    
    def test_optimize_prompt(self):
        """Test prompt optimization."""
        optimizer = OptimizationHelpers()
        
        long_prompt = "   This   has   extra   whitespace   " * 20
        optimized = optimizer.optimize_prompt(long_prompt, max_length=100)
        
        # Account for ellipsis added when truncating
        assert len(optimized) <= 103  # 100 + "..."
        assert "  " not in optimized  # No double spaces
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        optimizer = OptimizationHelpers()
        
        text = "This is a test"
        tokens = optimizer.estimate_tokens(text)
        
        assert tokens > 0
        assert tokens == len(text) // 4
    
    def test_optimize_batch_requests(self):
        """Test batch request optimization."""
        optimizer = OptimizationHelpers()
        
        requests = [
            {"content": "Short"},
            {"content": "A" * 1000},
            {"content": "Medium text here"},
            {"content": "B" * 1500},
        ]
        
        batches = optimizer.optimize_batch_requests(requests, max_tokens_per_batch=500)
        
        assert len(batches) > 1  # Should split into multiple batches
    
    def test_parallel_process(self):
        """Test parallel processing."""
        optimizer = OptimizationHelpers()
        
        items = list(range(10))
        
        def processor(x):
            return x * 2
        
        results = optimizer.parallel_process(items, processor, max_workers=2)
        
        assert len(results) == 10
        assert sorted(results) == [x * 2 for x in items]
    
    def test_get_optimization_stats(self):
        """Test optimization statistics."""
        optimizer = OptimizationHelpers()
        
        stats = optimizer.get_optimization_stats()
        
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "cache_hit_rate" in stats
    
    def test_clear_cache(self):
        """Test cache clearing."""
        optimizer = OptimizationHelpers()
        optimizer.cache["test"] = "value"
        
        optimizer.clear_cache()
        
        assert len(optimizer.cache) == 0
        assert optimizer.cache_stats["hits"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

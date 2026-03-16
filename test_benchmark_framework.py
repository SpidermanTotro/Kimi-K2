#!/usr/bin/env python3
"""
Tests for Benchmark Framework
==============================
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from benchmark_framework import (
    BenchmarkFramework,
    BenchmarkConfig,
    BenchmarkResult
)


class TestBenchmarkFramework(unittest.TestCase):
    """Test benchmark framework functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.framework = BenchmarkFramework(results_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_register_benchmark(self):
        """Test registering a benchmark"""
        config = BenchmarkConfig(
            name="test_benchmark",
            category="test",
            baseline=50.0,
            target=60.0,
            description="Test benchmark"
        )
        
        self.framework.register_benchmark(config)
        self.assertIn("test_benchmark", self.framework.benchmarks)
        self.assertEqual(self.framework.benchmarks["test_benchmark"].baseline, 50.0)
        
    def test_load_baseline_benchmarks(self):
        """Test loading baseline benchmarks"""
        self.framework.load_baseline_benchmarks()
        
        # Should have benchmarks in various categories
        self.assertGreater(len(self.framework.benchmarks), 0)
        
        # Check for specific benchmarks
        self.assertIn("LiveCodeBench_v6", self.framework.benchmarks)
        self.assertIn("AIME_2024", self.framework.benchmarks)
        self.assertIn("Tau2_retail", self.framework.benchmarks)
        
    def test_run_benchmark(self):
        """Test running a benchmark"""
        config = BenchmarkConfig(
            name="test_benchmark",
            category="test",
            baseline=50.0,
            target=60.0,
            description="Test benchmark"
        )
        
        self.framework.register_benchmark(config)
        result = self.framework.run_benchmark("test_benchmark", 55.0)
        
        self.assertEqual(result.name, "test_benchmark")
        self.assertEqual(result.score, 55.0)
        self.assertEqual(result.improvement, 5.0)
        self.assertFalse(result.target_met)
        
    def test_target_met(self):
        """Test target achievement detection"""
        config = BenchmarkConfig(
            name="test_benchmark",
            category="test",
            baseline=50.0,
            target=60.0,
            description="Test benchmark"
        )
        
        self.framework.register_benchmark(config)
        
        # Test score below target
        result1 = self.framework.run_benchmark("test_benchmark", 55.0)
        self.assertFalse(result1.target_met)
        
        # Test score at target
        result2 = self.framework.run_benchmark("test_benchmark", 60.0)
        self.assertTrue(result2.target_met)
        
        # Test score above target
        result3 = self.framework.run_benchmark("test_benchmark", 65.0)
        self.assertTrue(result3.target_met)
        
    def test_get_summary(self):
        """Test getting summary statistics"""
        self.framework.load_baseline_benchmarks()
        
        # Run some tests
        self.framework.run_benchmark("LiveCodeBench_v6", 58.0)
        self.framework.run_benchmark("AIME_2024", 72.0)
        
        summary = self.framework.get_summary()
        
        self.assertEqual(summary['tests_run'], 2)
        self.assertGreater(summary['total_benchmarks'], 0)
        self.assertIn('avg_improvement', summary)
        
    def test_get_results_by_category(self):
        """Test organizing results by category"""
        self.framework.load_baseline_benchmarks()
        
        self.framework.run_benchmark("LiveCodeBench_v6", 58.0)
        self.framework.run_benchmark("AIME_2024", 72.0)
        
        by_category = self.framework.get_results_by_category()
        
        self.assertIn("coding", by_category)
        self.assertIn("math", by_category)
        self.assertEqual(len(by_category["coding"]), 1)
        self.assertEqual(len(by_category["math"]), 1)
        
    def test_save_and_load_results(self):
        """Test saving and loading results"""
        self.framework.load_baseline_benchmarks()
        
        # Run some tests
        self.framework.run_benchmark("LiveCodeBench_v6", 58.0)
        self.framework.run_benchmark("AIME_2024", 72.0)
        
        # Save results
        filepath = self.framework.save_results("test_results.json")
        self.assertTrue(filepath.exists())
        
        # Create new framework and load results
        new_framework = BenchmarkFramework(results_dir=self.temp_dir)
        new_framework.load_results(filepath)
        
        self.assertEqual(len(new_framework.results), 2)
        
    def test_generate_report(self):
        """Test generating a report"""
        self.framework.load_baseline_benchmarks()
        
        self.framework.run_benchmark("LiveCodeBench_v6", 58.0)
        self.framework.run_benchmark("AIME_2024", 72.0)
        
        report = self.framework.generate_report()
        
        self.assertIn("BENCHMARK VALIDATION REPORT", report)
        self.assertIn("LiveCodeBench_v6", report)
        self.assertIn("AIME_2024", report)
        
    def test_improvement_percentage(self):
        """Test improvement percentage calculation"""
        result = BenchmarkResult(
            name="test",
            category="test",
            score=60.0,
            target=65.0,
            improvement=10.0,
            timestamp="2024-01-01",
            details={}
        )
        
        # improvement = 10.0, so baseline was 50.0
        # improvement_percentage = ((60 - 50) / 50) * 100 = 20%
        self.assertAlmostEqual(result.improvement_percentage, 20.0, places=1)


class TestBenchmarkConfig(unittest.TestCase):
    """Test BenchmarkConfig dataclass"""
    
    def test_config_creation(self):
        """Test creating a benchmark config"""
        config = BenchmarkConfig(
            name="test_benchmark",
            category="test",
            baseline=50.0,
            target=60.0,
            description="Test benchmark"
        )
        
        self.assertEqual(config.name, "test_benchmark")
        self.assertEqual(config.category, "test")
        self.assertEqual(config.baseline, 50.0)
        self.assertEqual(config.target, 60.0)


class TestBenchmarkResult(unittest.TestCase):
    """Test BenchmarkResult dataclass"""
    
    def test_result_creation(self):
        """Test creating a benchmark result"""
        result = BenchmarkResult(
            name="test_benchmark",
            category="test",
            score=55.0,
            target=60.0,
            improvement=5.0,
            timestamp="2024-01-01",
            details={"test_key": "test_value"}
        )
        
        self.assertEqual(result.name, "test_benchmark")
        self.assertEqual(result.score, 55.0)
        self.assertFalse(result.target_met)
        
    def test_target_met_property(self):
        """Test target_met property"""
        result = BenchmarkResult(
            name="test",
            category="test",
            score=60.0,
            target=60.0,
            improvement=0.0,
            timestamp="2024-01-01",
            details={}
        )
        
        self.assertTrue(result.target_met)


if __name__ == '__main__':
    unittest.main(verbosity=2)

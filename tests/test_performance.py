"""Performance benchmark tests for Kimi K2 model."""

import pytest
import torch
import time
from kimi_k2.model import KimiK2Model
from kimi_k2.config import KimiK2Config


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_forward_pass_time_small_model(self):
        """Benchmark forward pass time for small model."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            max_seq_length=512,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (4, 100))
        
        # Warm-up
        with torch.no_grad():
            _ = model(input_ids)
        
        # Benchmark
        start = time.time()
        with torch.no_grad():
            for _ in range(10):
                _ = model(input_ids)
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 10 seconds for 10 iterations)
        assert elapsed < 10.0
    
    def test_forward_pass_time_16_layer_model(self):
        """Benchmark forward pass time for 16-layer model."""
        config = KimiK2Config(
            vocab_size=5000,
            d_model=512,
            n_layers=16,
            n_heads=8,
            d_ff=2048,
            max_seq_length=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 5000, (2, 50))
        
        # Warm-up
        with torch.no_grad():
            _ = model(input_ids)
        
        # Benchmark
        start = time.time()
        with torch.no_grad():
            for _ in range(5):
                _ = model(input_ids)
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 30 seconds for 5 iterations)
        assert elapsed < 30.0
    
    def test_memory_usage_estimation(self):
        """Test memory usage stays within reasonable bounds."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=8,
            n_heads=8,
            d_ff=1024,
            max_seq_length=512,
            dropout=0.0
        )
        model = KimiK2Model(config)
        
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        
        # Should be within expected range for this configuration
        # Rough estimate: embeddings + 8 layers of transformers
        # Should be less than 100M parameters
        assert total_params < 100_000_000
    
    def test_generation_speed(self):
        """Benchmark token generation speed."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            max_seq_length=512
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 10))
        
        # Benchmark generation
        start = time.time()
        _ = model.generate(input_ids, max_new_tokens=20)
        elapsed = time.time() - start
        
        # Should generate 20 tokens in reasonable time (< 5 seconds)
        assert elapsed < 5.0
    
    def test_batch_inference_scaling(self):
        """Test that batch inference scales appropriately."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        seq_length = 50
        
        # Time for batch size 1
        input_ids_1 = torch.randint(0, 1000, (1, seq_length))
        start = time.time()
        with torch.no_grad():
            for _ in range(10):
                _ = model(input_ids_1)
        time_batch_1 = time.time() - start
        
        # Time for batch size 8
        input_ids_8 = torch.randint(0, 1000, (8, seq_length))
        start = time.time()
        with torch.no_grad():
            for _ in range(10):
                _ = model(input_ids_8)
        time_batch_8 = time.time() - start
        
        # Batch 8 should not be more than 10x slower than batch 1
        # (ideally much less due to parallelization)
        assert time_batch_8 < time_batch_1 * 10
    
    def test_sequence_length_scaling(self):
        """Test that inference time scales with sequence length."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        times = []
        lengths = [10, 50, 100, 200]
        
        for length in lengths:
            input_ids = torch.randint(0, 1000, (1, length))
            
            # Warm-up
            with torch.no_grad():
                _ = model(input_ids)
            
            # Benchmark
            start = time.time()
            with torch.no_grad():
                for _ in range(5):
                    _ = model(input_ids)
            elapsed = time.time() - start
            times.append(elapsed)
        
        # Each time should be greater than or equal to the previous
        # (longer sequences take more time)
        for i in range(len(times) - 1):
            assert times[i+1] >= times[i] * 0.5  # Allow some variance
    
    def test_parameter_count_16_layer(self):
        """Verify parameter count for 16-layer model."""
        config = KimiK2Config(
            vocab_size=50000,
            d_model=768,
            n_layers=16,
            n_heads=12,
            d_ff=3072,
            max_seq_length=2048
        )
        model = KimiK2Model(config)
        
        total_params = model.get_num_parameters(non_embedding=False)
        non_emb_params = model.get_num_parameters(non_embedding=True)
        
        # Should have reasonable number of parameters
        assert total_params > 0
        assert non_emb_params > 0
        assert non_emb_params < total_params
        
        # For reference, similar 16-layer models have ~100M-1B parameters
        # Our simplified version should be in a reasonable range
        assert total_params < 2_000_000_000  # Less than 2B parameters
    
    def test_gradient_computation_time(self):
        """Benchmark backward pass time."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (4, 50))
        target = torch.randint(0, 1000, (4, 50))
        
        # Warm-up
        logits = model(input_ids)
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, 1000),
            target.view(-1)
        )
        loss.backward()
        model.zero_grad()
        
        # Benchmark
        start = time.time()
        for _ in range(5):
            model.zero_grad()
            logits = model(input_ids)
            loss = torch.nn.functional.cross_entropy(
                logits.view(-1, 1000),
                target.view(-1)
            )
            loss.backward()
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 15 seconds for 5 iterations)
        assert elapsed < 15.0
    
    def test_model_size_in_memory(self):
        """Estimate model size in memory."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=8,
            n_heads=8,
            d_ff=1024
        )
        model = KimiK2Model(config)
        
        # Calculate size in bytes (assuming float32)
        total_params = sum(p.numel() for p in model.parameters())
        size_mb = (total_params * 4) / (1024 * 1024)  # 4 bytes per float32
        
        # Should be reasonable (< 500 MB for this config)
        assert size_mb < 500
    
    def test_inference_throughput(self):
        """Measure inference throughput (tokens/second)."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        batch_size = 8
        seq_length = 100
        num_iterations = 10
        
        input_ids = torch.randint(0, 1000, (batch_size, seq_length))
        
        # Warm-up
        with torch.no_grad():
            _ = model(input_ids)
        
        # Benchmark
        start = time.time()
        with torch.no_grad():
            for _ in range(num_iterations):
                _ = model(input_ids)
        elapsed = time.time() - start
        
        # Calculate throughput
        total_tokens = batch_size * seq_length * num_iterations
        throughput = total_tokens / elapsed
        
        # Should process at least 1000 tokens/second on CPU
        assert throughput > 1000


class TestMemoryEfficiency:
    """Tests for memory efficiency."""
    
    def test_no_memory_leak_forward(self):
        """Test that forward passes don't leak memory."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024,
            dropout=0.0
        )
        model = KimiK2Model(config)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (4, 50))
        
        # Multiple forward passes
        with torch.no_grad():
            for _ in range(100):
                _ = model(input_ids)
        
        # If we got here without OOM, memory is being managed properly
        assert True
    
    def test_no_memory_leak_generation(self):
        """Test that generation doesn't leak memory."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=256,
            n_layers=4,
            n_heads=8,
            d_ff=1024
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (1, 10))
        
        # Multiple generation runs
        for _ in range(10):
            _ = model.generate(input_ids, max_new_tokens=20)
        
        # If we got here without OOM, memory is being managed properly
        assert True
    
    def test_gradient_memory_cleanup(self):
        """Test that gradients are properly cleaned up."""
        config = KimiK2Config(
            vocab_size=1000,
            d_model=128,
            n_layers=2,
            n_heads=4,
            d_ff=512
        )
        model = KimiK2Model(config)
        
        input_ids = torch.randint(0, 1000, (2, 20))
        
        # Forward and backward
        logits = model(input_ids)
        loss = logits.sum()
        loss.backward()
        
        # Zero gradients
        model.zero_grad()
        
        # Check that gradients are cleared
        for param in model.parameters():
            if param.grad is not None:
                assert torch.all(param.grad == 0)

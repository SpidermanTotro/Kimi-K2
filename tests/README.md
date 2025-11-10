# Kimi K2 Test Suite

This directory contains comprehensive unit tests for the Kimi K2 transformer implementation.

## Test Coverage

Current test coverage: **100%** (273 statements, 108 branches)

## Test Categories

### 1. Component Tests (`test_*.py`)

#### `test_config.py` (17 tests)
- Configuration validation
- Edge cases for all configuration parameters
- Error handling for invalid configurations

#### `test_embeddings.py` (38 tests)
- Token embedding layer testing
- Positional encoding validation
- Combined embedding layer tests
- Edge cases: boundary values, invalid inputs

#### `test_attention.py` (26 tests)
- Multi-head self-attention mechanism
- Causal masking functionality
- Attention weight computation
- Edge cases: various mask shapes, sequence lengths, head counts

#### `test_feedforward.py` (25 tests)
- Feed-forward network tests
- Residual connection validation
- Layer normalization tests
- Edge cases: different dimensions, dropout values

#### `test_transformer.py` (15 tests)
- Transformer block integration
- Sequential block processing
- Gradient flow validation
- Mask effect on outputs

### 2. Integration Tests (`test_integration.py`, 30 tests)

- End-to-end pipeline testing
- 16-layer model validation
- Varying input length handling
- Batch processing tests
- Cumulative transformer block computation
- Temperature scaling in generation
- Training/eval mode consistency
- Boundary condition testing

### 3. Model Tests (`test_model.py`, 35 tests)

- Model initialization and forward pass
- Token generation with various parameters
- Temperature and top-k sampling
- Error handling for invalid inputs
- Parameter counting
- Gradient flow validation

### 4. Performance Benchmarks (`test_performance.py`, 13 tests)

- Forward pass timing
- Generation speed benchmarks
- Memory usage estimation
- Batch inference scaling
- Sequence length scaling
- Parameter count validation
- Gradient computation timing
- Memory leak detection

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage
```bash
pytest tests/ --cov=kimi_k2 --cov-report=term-missing --cov-branch
```

### Run specific test file
```bash
pytest tests/test_attention.py -v
```

### Run specific test class or function
```bash
pytest tests/test_model.py::TestKimiK2Model::test_forward_pass -v
```

### Run tests by category
```bash
# Integration tests only
pytest tests/test_integration.py -v

# Performance benchmarks only
pytest tests/test_performance.py -v
```

## Test Requirements

All required packages are listed in `requirements-test.txt`:
- pytest>=7.0.0
- pytest-cov>=4.0.0

Install with:
```bash
pip install -r requirements-test.txt
```

## Coverage Report

After running tests with coverage, view the detailed HTML report:
```bash
# Generate coverage report
pytest tests/ --cov=kimi_k2 --cov-report=html

# Open the report (Linux/Mac)
open htmlcov/index.html

# Or on Windows
start htmlcov/index.html
```

## Test Design Principles

1. **Comprehensive Coverage**: All components, edge cases, and error conditions are tested
2. **Isolation**: Each test is independent and doesn't rely on other tests
3. **Determinism**: Tests with dropout=0.0 ensure reproducible results
4. **Performance**: Benchmarks validate that the model performs within acceptable bounds
5. **Documentation**: Each test has a clear docstring explaining what it validates

## Key Test Scenarios

### Edge Cases Covered
- Empty and overly long sequences
- Single token/sequence length
- Minimum and maximum configuration values
- Invalid configurations (negative dimensions, incompatible parameters)
- Boundary values (exactly at max_seq_length)

### Integration Scenarios
- Full forward propagation with varying input lengths
- Sequential processing through all 16 transformer blocks
- Token generation with temperature scaling
- Batch processing at different sizes
- Training vs eval mode behavior

### Error Handling
- Invalid input dimensions
- Out-of-range token indices
- Sequence length exceeding maximum
- Invalid configuration parameters
- Negative or zero values where positive required

## Adding New Tests

When adding new functionality:
1. Add unit tests for the new component
2. Add integration tests for end-to-end behavior
3. Update edge case tests if applicable
4. Run coverage to ensure 95%+ coverage is maintained

Example test structure:
```python
class TestNewComponent:
    """Test cases for NewComponent."""
    
    def test_basic_functionality(self):
        """Test basic use case."""
        # Setup
        component = NewComponent(params)
        
        # Exercise
        result = component.forward(input)
        
        # Verify
        assert result.shape == expected_shape
    
    def test_edge_case(self):
        """Test specific edge case."""
        # Test implementation
        pass
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The full test suite completes in under 30 seconds on standard hardware.

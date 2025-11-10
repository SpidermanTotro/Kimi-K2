# Quick Start Guide

## Build the 16-Layer Go Model

This repository now includes a complete 16-layer transformer model implementation in Go!

### Installation

```bash
# Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# Download dependencies
go mod download
```

### Run the Example

```bash
cd example
go run main.go
```

Expected output:
```
=== Kimi-K2 16-Layer Transformer Model ===
Configuration:
  - Vocabulary Size: 50257
  - Hidden Size: 768
  - Number of Layers: 16
  - Number of Attention Heads: 12
  - Intermediate FFN Size: 3072
  - Max Sequence Length: 1024
  - Activation: gelu

Total Parameters: 190650961 (190.65M)
...
```

### Run Tests

```bash
cd model
go test -v
```

All 11 tests should pass with 85.9% code coverage.

### Build Standalone Binary

```bash
cd example
go build -o transformer-demo
./transformer-demo
```

## What's Included

- ✅ **Complete 16-layer transformer model** (~190M parameters)
- ✅ **Multi-head attention** with causal masking
- ✅ **Positional encoding** (sinusoidal)
- ✅ **Feed-forward networks** with GELU activation
- ✅ **Layer normalization** and residual connections
- ✅ **Comprehensive tests** (11 tests, all passing)
- ✅ **Example usage** program
- ✅ **Detailed documentation**

## Documentation

- **[GO_MODEL_README.md](GO_MODEL_README.md)** - User guide and API reference
- **[IMPLEMENTATION_DETAILS.md](IMPLEMENTATION_DETAILS.md)** - Technical deep dive
- **[README.md](README.md)** - Main Kimi-K2 project information

## Next Steps

1. Explore the code in the `model/` directory
2. Read the implementation details
3. Modify the configuration and experiment
4. Consider extending with training capabilities

## Support

For questions or issues, please open a GitHub issue.

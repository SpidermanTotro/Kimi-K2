# Quick Reference Guide - Kimi-K2 16GB GPT Model

## Quick Start

### Installation

```bash
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2
make install
```

### Build

```bash
make build
```

### Run Example

```bash
make run
```

### Run Tests

```bash
make test
```

## Basic Usage

### Create a Model

```go
import (
    "github.com/SpidermanTotro/Kimi-K2/pkg/config"
    "github.com/SpidermanTotro/Kimi-K2/pkg/model"
    "github.com/SpidermanTotro/Kimi-K2/pkg/tokenizer"
)

// Use 16GB config
cfg := config.Default16GBConfig()

// Or use small config for testing
cfg := config.SmallConfig()

// Create model
m, err := model.NewGPTModel(cfg)
```

### Tokenization

```go
// Create tokenizer
tok := tokenizer.NewTokenizer(cfg.VocabSize)

// Build vocabulary
texts := []string{"training text 1", "training text 2"}
tok.BuildVocab(texts)

// Encode
ids := tok.Encode("Hello, world!", true)  // with special tokens

// Decode
text := tok.Decode(ids, true)  // skip special tokens
```

### Generate Text

```go
// Encode prompt
promptIDs := tok.Encode("The quick brown", false)

// Generate
outputIDs, err := m.Generate(promptIDs, 50, 1.0)

// Decode
result := tok.Decode(outputIDs, false)
```

### Forward Pass

```go
inputIDs := []int{1, 2, 3, 4, 5}
logits, err := m.Forward(inputIDs, false)
```

## Configuration

### Model Sizes

**16GB Config** (Default):
- Vocab: 100K
- Hidden: 3072
- Layers: 28
- Memory: ~8-10GB

**Small Config** (Testing):
- Vocab: 50K
- Hidden: 1024
- Layers: 12
- Memory: ~0.5GB

### Custom Config

```go
cfg := &config.ModelConfig{
    VocabSize:         50000,
    HiddenDim:         1024,
    IntermediateDim:   2816,
    NumLayers:         12,
    NumHeads:          8,
    NumKVHeads:        4,
    MaxSeqLen:         2048,
    UseFP16:           true,
    UseFlashAttention: true,
    UseKVCache:        true,
    MaxMemoryGB:       4.0,
    NumWorkers:        4,
}
```

### Save/Load Config

```go
// Save
cfg.SaveToFile("config.json")

// Load
cfg, err := config.LoadFromFile("config.json")
```

## Benchmarking

```go
import "github.com/SpidermanTotro/Kimi-K2/pkg/benchmark"

// Create benchmark
bench, err := benchmark.NewModelBenchmark(cfg)

// Run all benchmarks
results := bench.RunAll()

// Print results
benchmark.PrintResults(results)

// Print system info
benchmark.PrintSystemInfo()
```

## Makefile Commands

```bash
make help       # Show all commands
make build      # Build binaries
make test       # Run tests
make bench      # Run benchmarks
make coverage   # Generate coverage report
make fmt        # Format code
make lint       # Run linter
make clean      # Clean build artifacts
make run        # Build and run example
```

## File Locations

- **Source Code**: `pkg/`
- **Examples**: `examples/`
- **Tests**: `pkg/*/`*_test.go`
- **Documentation**: `README_16GB.md`, `IMPLEMENTATION_SUMMARY.md`
- **Build Output**: `bin/`

## Common Tasks

### Estimate Memory Usage

```go
cfg := config.Default16GBConfig()
memoryGB := cfg.EstimateMemoryUsage()
fmt.Printf("Estimated: %.2f GB\n", memoryGB)
```

### Validate Configuration

```go
err := cfg.Validate()
if err != nil {
    log.Fatal(err)
}
```

### Save Tokenizer Vocabulary

```go
tok.SaveVocab("vocab.json")
```

### Load Tokenizer Vocabulary

```go
tok, err := tokenizer.LoadVocab("vocab.json")
```

## Performance Tips

1. **Use FlashAttention**: Set `UseFlashAttention: true`
2. **Enable KV Cache**: Set `UseKVCache: true`
3. **Use FP16**: Set `UseFP16: true`
4. **Adjust Workers**: Set `NumWorkers` based on CPU cores
5. **Optimize Sequence Length**: Use shorter sequences when possible

## Testing

```bash
# Run all tests
go test ./...

# Run with coverage
go test -coverprofile=coverage.out ./...

# View coverage
go tool cover -html=coverage.out

# Run benchmarks
go test -bench=. ./...

# Run specific package tests
go test ./pkg/config/
```

## Troubleshooting

**Build Errors**: Run `go mod tidy` then `make install`

**Memory Issues**: Use SmallConfig for testing

**Slow Performance**: Reduce sequence length or number of layers

**Test Failures**: Ensure all dependencies are installed with `make install`

## Resources

- **Full Documentation**: `README_16GB.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **API Reference**: See package documentation
- **Examples**: `examples/basic_usage.go`

## Getting Help

- Check documentation in `docs/`
- Review examples in `examples/`
- Run `make help` for available commands
- Check test files for usage examples

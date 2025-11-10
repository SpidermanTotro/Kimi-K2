# Kimi-K2 Go Language Model

A 16-layer transformer language model implementation in Go, based on the Kimi-K2 architecture. This is a pure Go implementation of transformer components suitable for learning, research, and experimentation.

## Features

- ✅ **16-layer transformer architecture** with configurable parameters
- ✅ **Multi-head attention mechanism** for capturing complex patterns
- ✅ **Position-wise feed-forward networks** with GELU activation
- ✅ **Layer normalization** for training stability
- ✅ **Sinusoidal positional encoding** for sequence position information
- ✅ **Token embeddings** with configurable vocabulary size
- ✅ **Comprehensive test coverage** for all components
- ✅ **Clean API** with extensive documentation

## Architecture

The model consists of the following components:

### Core Components

1. **Embedding Layer**: Maps token IDs to dense vector representations
2. **Positional Encoding**: Adds position information using sinusoidal functions
3. **Transformer Blocks** (16 layers):
   - Multi-head self-attention
   - Position-wise feed-forward network
   - Layer normalization (pre-norm architecture)
   - Residual connections
4. **Output Projection**: Maps hidden states to vocabulary logits

### Model Configuration

```go
type Config struct {
    VocabSize      int     // Size of the vocabulary
    HiddenSize     int     // Dimension of hidden states
    NumLayers      int     // Number of transformer layers (default: 16)
    NumHeads       int     // Number of attention heads
    FFNHiddenSize  int     // Hidden dimension in feed-forward network
    MaxSeqLen      int     // Maximum sequence length
    DropoutProb    float64 // Dropout probability
    EpsilonLN      float64 // Epsilon for layer normalization
    UsePositionEnc bool    // Whether to use positional encoding
}
```

## Installation

### Prerequisites

- Go 1.16 or higher

### Setup

```bash
# Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2/go-model

# Install dependencies
go mod tidy

# Build the project
go build ./...

# Run tests
go test ./...
```

## Usage

### Basic Usage

```go
package main

import (
    "fmt"
    "github.com/SpidermanTotro/Kimi-K2/go-model/model"
)

func main() {
    // Create a default 16-layer configuration
    config := model.NewDefaultConfig()

    // Create the transformer model
    transformer, err := model.NewTransformer(config)
    if err != nil {
        panic(err)
    }

    // Input token IDs (e.g., from a tokenizer)
    tokenIDs := []int{10, 25, 100, 250, 500}

    // Forward pass: get logits for all positions
    logits := transformer.Forward(tokenIDs)
    fmt.Printf("Output shape: %v\n", logits.Shape)

    // Predict next token probabilities
    probs := transformer.Predict(tokenIDs)

    // Get top-k predictions
    topK := transformer.GetTopK(probs, 5)
    fmt.Printf("Top 5 predictions: %v\n", topK)
}
```

### Custom Configuration

```go
// Create a custom configuration
customConfig := &model.Config{
    VocabSize:      30000,
    HiddenSize:     512,
    NumLayers:      16,    // 16 layers as per spec
    NumHeads:       8,
    FFNHiddenSize:  2048,
    MaxSeqLen:      256,
    DropoutProb:    0.1,
    EpsilonLN:      1e-12,
    UsePositionEnc: true,
}

// Validate configuration
if err := customConfig.Validate(); err != nil {
    panic(err)
}

// Create model with custom config
model, err := model.NewTransformer(customConfig)
```

### Running Examples

```bash
# Run the basic usage example
cd examples
go run basic_usage.go
```

## API Documentation

### Creating a Model

```go
// Use default configuration (16 layers)
config := model.NewDefaultConfig()
transformer, err := model.NewTransformer(config)
```

### Forward Pass

```go
// Forward pass returns logits for all positions
// Input: []int (token IDs)
// Output: *Tensor with shape [seq_len, vocab_size]
logits := transformer.Forward(tokenIDs)
```

### Prediction

```go
// Predict returns probability distribution for next token
// Input: []int (token IDs)
// Output: *Tensor with shape [vocab_size]
probs := transformer.Predict(tokenIDs)
```

### Top-K Selection

```go
// Get top-k most likely tokens
// Returns: []int (token IDs in descending probability order)
topK := transformer.GetTopK(probs, k)
```

### Model Information

```go
// Get total number of parameters
numParams := transformer.NumParameters()
```

## Testing

The implementation includes comprehensive tests for all components:

```bash
# Run all tests
go test ./...

# Run tests with verbose output
go test -v ./...

# Run tests with coverage
go test -cover ./...

# Run specific test
go test -v ./model -run TestTransformer16Layers
```

### Test Coverage

- ✅ Configuration validation
- ✅ Tensor operations (add, multiply, matmul, softmax, GELU, etc.)
- ✅ Layer normalization
- ✅ Positional encoding
- ✅ Multi-head attention
- ✅ Feed-forward network
- ✅ Embedding layer
- ✅ Transformer block
- ✅ Complete transformer model (16 layers)

## Architecture Details

### Multi-Head Attention

The multi-head attention mechanism splits the hidden dimension across multiple attention heads, allowing the model to attend to different aspects of the input simultaneously.

```
Number of heads: 12 (default)
Head dimension: hidden_size / num_heads
```

### Feed-Forward Network

Each transformer block contains a position-wise feed-forward network with GELU activation:

```
FFN(x) = GELU(xW1 + b1)W2 + b2
FFN hidden size: 4 × hidden_size (default)
```

### Layer Normalization

Pre-normalization is applied before each sub-layer (attention and FFN):

```
output = LayerNorm(x) → Sublayer → Add residual
```

### Positional Encoding

Sinusoidal positional encodings are added to input embeddings:

```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

## Default Model Specifications

| Parameter | Value |
|-----------|-------|
| Number of Layers | 16 |
| Hidden Size | 768 |
| Number of Heads | 12 |
| Head Dimension | 64 |
| FFN Hidden Size | 3072 |
| Vocabulary Size | 50,000 |
| Max Sequence Length | 512 |
| Dropout | 0.1 |
| Total Parameters | ~110M |

## Performance Considerations

### Memory Usage

The model allocates memory for:
- Embedding weights: `vocab_size × hidden_size`
- Transformer blocks: `num_layers × (4 × hidden_size² + 2 × hidden_size × ffn_hidden_size)`
- Output projection: `hidden_size × vocab_size`

### Computational Complexity

Per forward pass:
- Self-attention: O(seq_len² × hidden_size)
- Feed-forward: O(seq_len × hidden_size × ffn_hidden_size)
- Total: O(num_layers × seq_len × (seq_len × hidden_size + hidden_size × ffn_hidden_size))

## Limitations

This is a reference implementation designed for educational purposes and experimentation:

- **Tensor Operations**: Uses a basic tensor implementation. For production use, consider integrating with optimized tensor libraries.
- **Training**: This implementation focuses on inference. Training functionality (backpropagation, optimizers) is not included.
- **Performance**: Not optimized for production workloads. Consider using GPU-accelerated frameworks for large-scale applications.
- **Weight Initialization**: Uses simplified initialization. Production models should use proper initialization schemes (Xavier, He, etc.).

## Future Enhancements

Potential areas for extension:

- [ ] Training support with backpropagation
- [ ] Optimizers (Adam, SGD, etc.)
- [ ] GPU acceleration
- [ ] Beam search for generation
- [ ] Model serialization/deserialization
- [ ] Integration with optimized tensor libraries
- [ ] Distributed training support
- [ ] Mixed precision training
- [ ] Model quantization

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `go test ./...`
2. Code is properly formatted: `go fmt ./...`
3. Documentation is updated for new features
4. New functionality includes tests

## License

This project is licensed under the Modified MIT License. See the LICENSE file in the root directory for details.

## Citation

If you use this implementation in your research, please cite:

```bibtex
@misc{kimik2go2024,
  title={Kimi-K2 Go Language Model Implementation},
  author={Kimi-K2 Contributors},
  year={2024},
  howpublished={\url{https://github.com/SpidermanTotro/Kimi-K2}}
}
```

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) - Original Transformer paper
- [Kimi K2: Open Agentic Intelligence](https://arxiv.org/abs/2507.20534) - Kimi K2 Technical Report
- [Layer Normalization](https://arxiv.org/abs/1607.06450)
- [Gaussian Error Linear Units (GELUs)](https://arxiv.org/abs/1606.08415)

## Contact

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Note**: This is a simplified implementation for educational and research purposes. For production deployments of large language models, consider using established frameworks like PyTorch, TensorFlow, or JAX with proper hardware acceleration.

# Kimi-K2 16-Layer Go Model

This is a 16-layer transformer model implementation in Go, inspired by the Kimi-K2 architecture. This is a simplified educational implementation that demonstrates the core transformer architecture with 16 layers.

## Architecture

The model implements a standard transformer architecture with the following components:

- **16 Transformer Layers**: Each layer contains:
  - Multi-head self-attention mechanism
  - Position-wise feed-forward network
  - Layer normalization
  - Residual connections
  
- **Default Configuration**:
  - Vocabulary Size: 50,257 (GPT-2 compatible)
  - Hidden Size: 768
  - Number of Layers: 16
  - Number of Attention Heads: 12
  - Intermediate FFN Size: 3,072
  - Max Sequence Length: 1,024
  - Activation: GELU

## Project Structure

```
model/
├── config.go              # Model configuration
├── layers.go              # Basic neural network layers
├── attention.go           # Multi-head attention implementation
├── feedforward.go         # Feed-forward network
├── positional.go          # Positional encoding
├── transformer_block.go   # Single transformer layer
├── model.go              # Main model definition
└── model_test.go         # Unit tests

example/
└── main.go               # Example usage
```

## Installation

Make sure you have Go 1.21 or later installed.

```bash
# Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# Download dependencies
go mod download
```

## Usage

### Basic Example

```go
package main

import (
    "fmt"
    "log"
    "github.com/SpidermanTotro/Kimi-K2/model"
)

func main() {
    // Create a default configuration
    config := model.NewDefaultConfig()
    
    // Create the model
    transformer, err := model.NewTransformer16(config)
    if err != nil {
        log.Fatal(err)
    }
    
    // Run a forward pass
    tokens := []int{1, 2, 3, 4, 5}
    logits, err := transformer.Forward(tokens)
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Output shape: [%d, %d]\n", len(logits), len(logits[0]))
}
```

### Running the Example

```bash
cd example
go run main.go
```

### Running Tests

```bash
cd model
go test -v
```

## Model Parameters

The default configuration has approximately **~93 million parameters**:

- Token Embeddings: ~38M parameters
- 16 Transformer Layers: ~50M parameters
- LM Head: ~38M parameters

Each transformer layer contains:
- Multi-head Attention: ~2.4M parameters
- Feed-forward Network: ~4.7M parameters
- Layer Normalization: ~3K parameters

## Features

- ✅ Multi-head self-attention with causal masking
- ✅ Sinusoidal positional encoding
- ✅ Layer normalization with learnable parameters
- ✅ GELU activation function
- ✅ Residual connections
- ✅ Language modeling head for next-token prediction
- ✅ Configurable architecture
- ✅ Comprehensive unit tests

## Differences from Full Kimi-K2

This is a simplified educational implementation. The full Kimi-K2 model has:
- 1 trillion total parameters (this has ~93M)
- 61 layers with Mixture-of-Experts (this has 16 standard layers)
- 384 experts with 8 selected per token (this has no MoE)
- Multi-latent attention (this uses standard multi-head attention)
- Advanced optimization with Muon/MuonClip (this is inference-only)

## API Reference

### Config

```go
type Config struct {
    VocabSize        int     // Size of the vocabulary
    HiddenSize       int     // Hidden dimension size
    NumLayers        int     // Number of transformer layers (16)
    NumHeads         int     // Number of attention heads
    IntermediateSize int     // Size of FFN intermediate layer
    MaxSeqLength     int     // Maximum sequence length
    DropoutRate      float64 // Dropout probability
    LayerNormEps     float64 // Layer normalization epsilon
    ActivationType   string  // Activation function type
}
```

### Transformer16

```go
// Create a new model
model, err := NewTransformer16(config)

// Forward pass
logits, err := model.Forward(tokens []int) ([][]float64, error)

// Generate next token
nextToken, err := model.Generate(tokens []int, temperature float64) (int, error)

// Get number of parameters
numParams := model.NumParameters()
```

## Contributing

This is a reference implementation for educational purposes. Feel free to extend it with:
- Weight initialization strategies
- Training capabilities
- Optimization algorithms
- Checkpoint saving/loading
- Additional activation functions
- Mixture-of-Experts layers

## License

This implementation follows the Modified MIT License of the main Kimi-K2 project. See the [LICENSE](../LICENSE) file for details.

## References

- [Kimi-K2 Technical Report](https://www.arxiv.org/abs/2507.20534)
- [Kimi-K2 Main Repository](https://github.com/moonshotai/Kimi-K2)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)

## Contact

For questions about this implementation, please open an issue on GitHub.

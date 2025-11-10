# Kimi-K2 Skills Framework Examples

This directory contains example scripts demonstrating the capabilities of the Kimi-K2 Skills Framework.

## Quick Start

Run the comprehensive quick start example:

```bash
python quickstart.py
```

This example demonstrates:
- Voice synthesis in multiple languages
- Image generation
- Music composition
- Story writing
- Procedural content generation
- Workflow orchestration
- Performance optimization
- Caching system

## Available Examples

### Media Generation

- **Voice Synthesis**: Multi-language voice generation with emotional expression
- **Image Generation**: High-resolution image creation in various styles
- **Music Generation**: AI-composed music with dynamic mixing
- **Video Generation**: Full-length video with scene composition
- **Animation**: Cinematic-quality 3D animation

### AI Creativity

- **Story Writing**: Long-form narrative generation
- **Dialogue Generation**: Natural multi-character conversations
- **Procedural Generation**: Dynamic quest and world generation

### Core Utilities

- **Caching**: Intelligent asset caching
- **Performance**: Profiling and optimization
- **Workflows**: End-to-end production pipelines

## Running Individual Examples

Each module can be imported and used independently:

```python
from skills.media_generation import VoiceSynthesizer

synthesizer = VoiceSynthesizer(device="cuda")
# ... use synthesizer
```

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- 16GB+ RAM
- Model weights (see main documentation)

## Documentation

For complete documentation, see:
- [Skills Documentation](../docs/skills_documentation.md)
- [API Reference](../docs/api_reference.md)
- [Tutorials](../docs/tutorials.md)

## Support

For issues and questions, visit the [Kimi-K2 repository](https://github.com/moonshotai/Kimi-K2).

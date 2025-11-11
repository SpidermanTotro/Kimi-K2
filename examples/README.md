# Kimi K2 SDK Examples

This directory contains comprehensive examples demonstrating all features of the Kimi K2 SDK.

## Prerequisites

```bash
# Install the SDK
cd ..
pip install -r requirements.txt
python setup.py install

# Set your API key (required for actual API calls)
export MOONSHOT_API_KEY='your-api-key-here'
```

## Examples

### 1. basic_usage.py
**Basic client functionality and tool calling**

Demonstrates:
- Simple chat interactions
- Tool calling with automatic execution
- Structured conversations

Run:
```bash
python basic_usage.py
```

### 2. advanced_skills.py
**Advanced AI capabilities**

Demonstrates:
- Chain-of-thought reasoning
- Problem decomposition
- Text-to-image generation
- Contextual chat with history
- Specialized pipelines (education, healthcare)

Run:
```bash
python advanced_skills.py
```

### 3. interaction_features.py
**Conversation management and personalization**

Demonstrates:
- Multi-user conversation sessions
- User personalization and preferences
- Persistent memory storage
- Integrated workflow combining all features

Run:
```bash
python interaction_features.py
```

### 4. integration_performance.py
**Cross-AI integration and optimization**

Demonstrates:
- Moon AI integration
- Unified queries across multiple AI systems
- Performance benchmarking
- Optimization techniques (caching, batching)

Run:
```bash
python integration_performance.py
```

## Running Without API Key

The examples will indicate when they need an API key. Most features can be demonstrated with mock data:

```bash
# Run without API key - will show structure and mock responses
python basic_usage.py

# With API key - will make actual API calls
export MOONSHOT_API_KEY='your-key'
python basic_usage.py
```

## Example Output

When you run the examples with an API key, you'll see:
- Real responses from Kimi K2
- Tool execution results
- Performance metrics
- Memory and conversation state management

## Learn More

- [API Documentation](../docs/API_DOCUMENTATION.md)
- [Implementation Summary](../IMPLEMENTATION_SUMMARY.md)
- [Main README](../README.md)

## Troubleshooting

**"API key not set" error:**
```bash
export MOONSHOT_API_KEY='your-api-key'
```

**Import errors:**
```bash
pip install -e ..
```

**Module not found:**
```bash
cd .. && python setup.py install
```

## Quick Test

Verify everything works:
```bash
cd ..
python verify_sdk.py
```

This will run a comprehensive check of all SDK features.

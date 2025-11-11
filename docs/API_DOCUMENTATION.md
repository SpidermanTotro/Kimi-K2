# Kimi K2 SDK API Documentation

## Overview

The Kimi K2 SDK provides a comprehensive toolkit for integrating advanced AI capabilities into your applications. This SDK combines the power of Kimi K2 with features from Moon AI and other AI systems.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Skills Module](#skills-module)
5. [Interaction Module](#interaction-module)
6. [Integration Module](#integration-module)
7. [Performance Module](#performance-module)
8. [Examples](#examples)

## Installation

### Basic Installation

```bash
pip install -r requirements.txt
python setup.py install
```

### Development Installation

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

### With Image Generation Support

```bash
pip install -e ".[image]"
```

## Quick Start

### Simple Chat

```python
from kimi_k2 import KimiClient

client = KimiClient(api_key="your-api-key")
response = client.simple_chat("What are the features of Kimi K2?")
print(response)
```

### Tool Calling

```python
from kimi_k2 import KimiClient

def get_weather(city: str) -> dict:
    return {"temperature": "22°C", "condition": "Sunny"}

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {
            "type": "object",
            "required": ["city"],
            "properties": {"city": {"type": "string"}}
        }
    }
}]

client = KimiClient(api_key="your-api-key")
response = client.tool_chat(
    "What's the weather in Tokyo?",
    tools=tools,
    tool_map={"get_weather": get_weather}
)
```

## Core Components

### KimiClient

The main client for interacting with Kimi K2.

#### Constructor Parameters

- `api_key` (str, optional): API key for authentication
- `base_url` (str): Base URL for the API (default: "https://platform.moonshot.ai/v1")
- `model` (str): Model identifier (default: "kimi-k2-instruct")
- `temperature` (float): Response temperature (default: 0.6)

#### Methods

##### `chat(messages, temperature, max_tokens, stream, tools, **kwargs)`

Send a chat completion request.

**Parameters:**
- `messages` (list): List of message dictionaries
- `temperature` (float, optional): Override default temperature
- `max_tokens` (int): Maximum tokens to generate (default: 2048)
- `stream` (bool): Stream the response (default: False)
- `tools` (list, optional): Tool definitions
- `**kwargs`: Additional API parameters

**Returns:** Chat completion response

##### `simple_chat(user_message, system_prompt)`

Simple chat interface.

**Parameters:**
- `user_message` (str): User's message
- `system_prompt` (str, optional): System prompt override

**Returns:** Response string

##### `tool_chat(user_message, tools, tool_map, system_prompt, max_iterations)`

Chat with automatic tool calling.

**Parameters:**
- `user_message` (str): User's message
- `tools` (list): Tool definitions
- `tool_map` (dict): Mapping of tool names to implementations
- `system_prompt` (str, optional): System prompt override
- `max_iterations` (int): Maximum tool call iterations (default: 10)

**Returns:** Final response string

## Skills Module

### AdvancedReasoning

Advanced reasoning capabilities for complex problem solving.

#### Methods

##### `chain_of_thought(problem, domain)`

Perform chain-of-thought reasoning.

**Example:**
```python
from kimi_k2.skills import AdvancedReasoning

reasoning = AdvancedReasoning()
result = reasoning.chain_of_thought(
    "If a car travels 120km in 2 hours...",
    domain="math"
)
```

##### `decompose_problem(complex_problem)`

Decompose a complex problem into sub-problems.

##### `multi_hop_reasoning(question, context)`

Perform multi-hop reasoning across contexts.

##### `analyze_step_by_step(task, requirements)`

Analyze a task step-by-step.

### TextToImageGenerator

Text-to-image generation integration.

#### Constructor

```python
from kimi_k2.skills import TextToImageGenerator

generator = TextToImageGenerator(
    backend="dalle",  # or "stable-diffusion"
    api_key="your-api-key"
)
```

#### Methods

##### `generate(prompt, size, quality, num_images, style)`

Generate images from text.

##### `enhance_prompt(simple_prompt, client)`

Enhance a prompt using Kimi K2.

### ContextualChat

Context-aware conversation handling.

#### Methods

##### `chat_with_context(user_message, context, maintain_history)`

Chat with contextual awareness.

**Example:**
```python
from kimi_k2.skills import ContextualChat

chat = ContextualChat()
result = chat.chat_with_context(
    "How do I learn Python?",
    context={"user_info": "beginner programmer"},
    maintain_history=True
)
```

##### `detect_topic_change(user_message)`

Detect if the conversation topic changed.

##### `summarize_conversation()`

Summarize the current conversation.

##### `clear_context()`

Clear conversation context.

### SpecializedPipeline

Domain-specific AI pipelines.

#### Supported Domains

- `healthcare`: Medical information and analysis
- `education`: Tutoring and learning
- `legal`: Legal research and information
- `finance`: Financial analysis

#### Methods

##### `education_tutor(subject, topic, student_level, question)`

Educational tutoring.

**Example:**
```python
from kimi_k2.skills import SpecializedPipeline

pipeline = SpecializedPipeline("education")
result = pipeline.education_tutor(
    subject="mathematics",
    topic="algebra",
    student_level="high",
    question="How do I solve quadratic equations?"
)
```

##### `healthcare_analysis(symptoms, patient_info)`

Healthcare symptom analysis (educational purposes).

##### `legal_research(legal_question, jurisdiction)`

Legal research assistance.

##### `financial_analysis(data_description, analysis_type)`

Financial data analysis.

## Interaction Module

### ConversationManager

Multi-user conversation management.

#### Methods

##### `create_session(session_id, metadata)`

Create a new conversation session.

##### `add_user_to_session(session_id, user_id, user_info)`

Add a user to a session.

##### `add_message(session_id, user_id, message, message_type)`

Add a message to a session.

##### `get_session_history(session_id, limit, user_id)`

Get conversation history.

**Example:**
```python
from kimi_k2.interaction import ConversationManager

manager = ConversationManager()
manager.create_session("session_001")
manager.add_user_to_session("session_001", "user_alice")
manager.add_message("session_001", "user_alice", "Hello!", "user")
```

### PersonalizationEngine

User personalization and preference management.

#### Methods

##### `create_profile(user_id, preferences)`

Create a user profile.

##### `update_preferences(user_id, preferences, merge)`

Update user preferences.

##### `record_interaction(user_id, interaction_type, data)`

Record user interaction for learning.

##### `get_adaptive_settings(user_id, context)`

Get adaptive settings based on user profile.

**Example:**
```python
from kimi_k2.interaction import PersonalizationEngine

engine = PersonalizationEngine()
engine.create_profile("user_001", preferences={"style": "concise"})
engine.record_interaction("user_001", "query", {"topics": ["AI", "ML"]})
```

### MemoryModule

Persistent memory for session recall.

#### Methods

##### `store_memory(user_id, content, category, tags, metadata)`

Store a memory.

##### `recall_memories(user_id, category, tags, limit)`

Recall memories.

##### `search_memories(user_id, query, limit)`

Search memories by content.

##### `consolidate_memories(user_id, category)`

Consolidate related memories.

**Example:**
```python
from kimi_k2.interaction import MemoryModule

memory = MemoryModule()
memory.store_memory(
    "user_001",
    "User is learning PyTorch",
    category="learning",
    tags=["pytorch", "ml"]
)
memories = memory.recall_memories("user_001", category="learning")
```

## Integration Module

### MoonAIIntegration

Cross-AI system integration.

#### Methods

##### `register_integration(integration_name, config)`

Register a new AI system integration.

##### `unified_query(query, target_systems, combine_results)`

Query multiple AI systems.

##### `create_ai_pipeline(pipeline_steps)`

Create a pipeline across AI systems.

**Example:**
```python
from kimi_k2.integration import MoonAIIntegration

integration = MoonAIIntegration()
integration.register_integration("custom_ai", {"endpoint": "..."})
result = integration.unified_query("What is AI?", combine_results=True)
```

## Performance Module

### BenchmarkingTools

Performance measurement utilities.

#### Methods

##### `measure_latency(func, *args, iterations, **kwargs)`

Measure function latency.

##### `measure_throughput(func, test_data, duration_seconds)`

Measure throughput.

##### `compare_performance(systems, test_input, iterations)`

Compare performance across systems.

##### `generate_report()`

Generate a benchmark report.

**Example:**
```python
from kimi_k2.performance import BenchmarkingTools

benchmark = BenchmarkingTools()
result = benchmark.measure_latency(my_function, arg1, iterations=5)
print(f"Average latency: {result['average_ms']}ms")
```

### OptimizationHelpers

Performance optimization utilities.

#### Methods

##### `cache_response(ttl)` (decorator)

Cache function responses.

##### `batch_process(items, processor, batch_size)`

Process items in batches.

##### `parallel_process(items, processor, max_workers)`

Process items in parallel.

##### `optimize_prompt(prompt, max_length)`

Optimize prompt for efficiency.

**Example:**
```python
from kimi_k2.performance import OptimizationHelpers

optimizer = OptimizationHelpers()

@optimizer.cache_response()
def expensive_function(x):
    return x * 2

# First call is computed, second is cached
result1 = expensive_function(5)
result2 = expensive_function(5)  # Cached
```

## Examples

Complete examples are available in the `examples/` directory:

- `basic_usage.py`: Basic client usage and tool calling
- `advanced_skills.py`: Advanced reasoning and specialized pipelines
- `interaction_features.py`: Conversation management and personalization
- `integration_performance.py`: Cross-AI integration and optimization

## Testing

Run the test suite:

```bash
pytest tests/unit/ -v
```

Run with coverage:

```bash
pytest tests/unit/ --cov=kimi_k2 --cov-report=html
```

## Security

All integrations should be tested for security vulnerabilities. The SDK includes:

- Input validation
- Secure API key handling
- Rate limiting support
- Error handling

## License

This SDK is released under the Modified MIT License. See LICENSE file for details.

## Support

For issues and questions:
- Email: support@moonshot.cn
- GitHub Issues: https://github.com/moonshotai/Kimi-K2/issues

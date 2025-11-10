# Advanced Usage Guide

This guide covers advanced usage patterns and best practices for Kimi-K2.

## Table of Contents

1. [Configuration and Optimization](#configuration-and-optimization)
2. [Advanced Tool Calling](#advanced-tool-calling)
3. [Streaming and Real-time Applications](#streaming-and-real-time-applications)
4. [Multi-turn Conversations](#multi-turn-conversations)
5. [Agentic Workflows](#agentic-workflows)
6. [Performance Optimization](#performance-optimization)
7. [Error Handling and Retry Logic](#error-handling-and-retry-logic)

## Configuration and Optimization

### Temperature Settings

Kimi-K2 performs best with `temperature=0.6` for most tasks:

```python
from kimi_k2.client import KimiClient

# Recommended for general use
client = KimiClient(
    base_url="http://localhost:8000",
    temperature=0.6
)

# For more creative tasks
creative_client = KimiClient(
    base_url="http://localhost:8000",
    temperature=0.8
)

# For deterministic outputs
deterministic_client = KimiClient(
    base_url="http://localhost:8000",
    temperature=0.3
)
```

### Token Management

Control output length and manage context windows:

```python
# Short responses
client = KimiClient(
    base_url="http://localhost:8000",
    max_tokens=512
)

# Long-form content
long_form_client = KimiClient(
    base_url="http://localhost:8000",
    max_tokens=4096
)

# Override per request
response = client.chat(messages, max_tokens=1024)
```

## Advanced Tool Calling

### Complex Tool Schemas

Define tools with nested parameters:

```python
from kimi_k2.tools import ToolManager

tm = ToolManager()

# Manual schema with complex types
complex_tool = {
    "type": "function",
    "function": {
        "name": "process_data",
        "description": "Process structured data",
        "parameters": {
            "type": "object",
            "required": ["data", "operation"],
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Array of data objects"
                },
                "operation": {
                    "type": "string",
                    "enum": ["sum", "average", "max", "min"],
                    "description": "Operation to perform"
                },
                "filters": {
                    "type": "object",
                    "properties": {
                        "min_value": {"type": "number"},
                        "max_value": {"type": "number"}
                    }
                }
            }
        }
    }
}
```

### Error Handling in Tools

Implement robust error handling:

```python
@tm.register(description="Safe API call")
def call_external_api(endpoint: str) -> dict:
    try:
        # Make API call
        result = requests.get(endpoint, timeout=5)
        result.raise_for_status()
        return {"status": "success", "data": result.json()}
    except requests.Timeout:
        return {"status": "error", "message": "Request timed out"}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}
```

### Tool Call Monitoring

Log and monitor tool calls:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitored_tool(client, messages, tools, tool_map):
    """Tool calling with monitoring."""
    original_tools = tool_map.copy()
    
    # Wrap tools with logging
    monitored_map = {}
    for name, func in original_tools.items():
        def logged_func(*args, _name=name, _func=func, **kwargs):
            logger.info(f"Calling tool: {_name}")
            logger.info(f"Arguments: {args}, {kwargs}")
            result = _func(*args, **kwargs)
            logger.info(f"Result: {result}")
            return result
        
        monitored_map[name] = logged_func
    
    return client.chat_with_tools(messages, tools, monitored_map)
```

## Streaming and Real-time Applications

### Progressive Rendering

Stream responses for better UX:

```python
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console()

def stream_with_rendering(client, messages):
    """Stream with live rendering."""
    accumulated = ""
    
    with Live(console=console, auto_refresh=True) as live:
        for chunk in client.chat(messages, stream=True):
            accumulated += chunk
            live.update(Markdown(accumulated))
    
    return accumulated
```

### Async Streaming

Use async for concurrent operations:

```python
import asyncio
import aiohttp

async def async_chat_stream(client, messages):
    """Async streaming implementation."""
    # This would require an async version of the client
    # Implementation depends on the inference engine's async API
    pass
```

## Multi-turn Conversations

### Conversation Management

Manage long conversations efficiently:

```python
class ConversationManager:
    """Manage multi-turn conversations."""
    
    def __init__(self, client, max_history=10):
        self.client = client
        self.messages = []
        self.max_history = max_history
    
    def add_system_message(self, content):
        """Add system message."""
        self.messages.append({"role": "system", "content": content})
    
    def send(self, user_message):
        """Send a message and get response."""
        self.messages.append({"role": "user", "content": user_message})
        
        # Trim history if needed
        if len(self.messages) > self.max_history * 2:
            # Keep system message and recent history
            system_msgs = [m for m in self.messages if m["role"] == "system"]
            recent_msgs = self.messages[-(self.max_history * 2):]
            self.messages = system_msgs + recent_msgs
        
        response = self.client.chat(self.messages)
        self.messages.append({"role": "assistant", "content": response})
        
        return response
    
    def clear(self):
        """Clear conversation history."""
        self.messages = []

# Usage
manager = ConversationManager(client)
manager.add_system_message("You are a helpful assistant.")
response1 = manager.send("What is Python?")
response2 = manager.send("Can you show me an example?")
```

## Agentic Workflows

### Multi-step Planning

Implement complex agentic workflows:

```python
class AgenticWorkflow:
    """Execute multi-step agentic workflows."""
    
    def __init__(self, client):
        self.client = client
    
    def plan_and_execute(self, goal):
        """Plan steps and execute them."""
        # Step 1: Create plan
        plan_prompt = f"""
        Create a detailed step-by-step plan to accomplish this goal:
        {goal}
        
        Format your response as a numbered list of steps.
        """
        
        plan = self.client.simple_chat(plan_prompt)
        print(f"Plan:\n{plan}\n")
        
        # Step 2: Execute each step
        results = []
        for step in self._parse_steps(plan):
            result = self._execute_step(step)
            results.append(result)
        
        # Step 3: Synthesize results
        synthesis_prompt = f"""
        Based on these results:
        {chr(10).join(results)}
        
        Provide a final answer for: {goal}
        """
        
        return self.client.simple_chat(synthesis_prompt)
    
    def _parse_steps(self, plan):
        """Parse steps from plan."""
        # Simple parsing - could be more sophisticated
        lines = plan.split('\n')
        steps = [l.strip() for l in lines if l.strip() and l.strip()[0].isdigit()]
        return steps
    
    def _execute_step(self, step):
        """Execute a single step."""
        return self.client.simple_chat(f"Execute this step: {step}")
```

### Reflection and Self-Correction

Implement self-correction mechanisms:

```python
def generate_with_reflection(client, task, max_iterations=3):
    """Generate output with self-reflection."""
    
    for i in range(max_iterations):
        # Generate
        output = client.simple_chat(f"Task: {task}")
        
        # Reflect
        reflection_prompt = f"""
        Review this output for the task '{task}':
        
        {output}
        
        Is this correct and complete? If not, what needs to be fixed?
        Respond with either "APPROVED" or explain what needs fixing.
        """
        
        reflection = client.simple_chat(reflection_prompt)
        
        if "APPROVED" in reflection.upper():
            return output
        
        # Revise
        task = f"{task}\n\nPrevious attempt:\n{output}\n\nFeedback:\n{reflection}\n\nPlease revise."
    
    return output
```

## Performance Optimization

### Batch Processing

Process multiple requests efficiently:

```python
import concurrent.futures

def batch_process(client, prompts, max_workers=5):
    """Process multiple prompts in parallel."""
    
    def process_single(prompt):
        return client.simple_chat(prompt)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single, p) for p in prompts]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    return results
```

### Caching Responses

Implement response caching:

```python
from functools import lru_cache
import hashlib

class CachedClient:
    """Client with response caching."""
    
    def __init__(self, client):
        self.client = client
        self.cache = {}
    
    def chat(self, messages, use_cache=True):
        """Chat with caching."""
        if not use_cache:
            return self.client.chat(messages)
        
        # Create cache key
        key = hashlib.md5(str(messages).encode()).hexdigest()
        
        if key in self.cache:
            return self.cache[key]
        
        response = self.client.chat(messages)
        self.cache[key] = response
        
        return response
```

## Error Handling and Retry Logic

### Robust Error Handling

Implement comprehensive error handling:

```python
import time
from typing import Optional

class RobustClient:
    """Client with retry logic and error handling."""
    
    def __init__(self, client, max_retries=3, backoff_factor=2):
        self.client = client
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def chat_with_retry(self, messages, **kwargs):
        """Chat with automatic retry on failure."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return self.client.chat(messages, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        raise Exception(f"All {self.max_retries} attempts failed. Last error: {last_error}")
```

### Timeout Management

Handle long-running requests:

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def chat_with_timeout(client, messages, timeout_seconds=30):
    """Execute chat with timeout."""
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(client.chat, messages)
        try:
            return future.result(timeout=timeout_seconds)
        except TimeoutError:
            return "Request timed out. Please try again with a simpler prompt."
```

## Best Practices

1. **Always use recommended temperature** (0.6) unless you have a specific reason to change it
2. **Implement proper error handling** for production applications
3. **Monitor token usage** to optimize costs and performance
4. **Use streaming** for better user experience in interactive applications
5. **Cache responses** when appropriate to reduce latency
6. **Implement retry logic** for robustness
7. **Use tool calling** for dynamic, data-driven applications
8. **Manage conversation history** to stay within context limits
9. **Log and monitor** tool calls and API usage
10. **Test thoroughly** with edge cases and error conditions

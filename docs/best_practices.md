# Best Practices for Kimi-K2

This guide provides recommendations and best practices for using Kimi-K2 effectively.

## Table of Contents

1. [Model Configuration](#model-configuration)
2. [Prompt Engineering](#prompt-engineering)
3. [Tool Design](#tool-design)
4. [Performance Optimization](#performance-optimization)
5. [Error Handling](#error-handling)
6. [Security Considerations](#security-considerations)
7. [Production Deployment](#production-deployment)

---

## Model Configuration

### Temperature Settings

**Recommended:** `temperature=0.6` for Kimi-K2

```python
# Good: Balanced creativity and coherence
client = KimiClient(base_url="...", temperature=0.6)

# More deterministic for code/facts
client = KimiClient(base_url="...", temperature=0.3)

# More creative for stories/brainstorming
client = KimiClient(base_url="...", temperature=0.8)
```

**Guidelines:**
- **0.0-0.3**: Highly deterministic, good for factual tasks, code generation
- **0.4-0.7**: Balanced, recommended for most use cases (0.6 optimal for Kimi-K2)
- **0.8-1.0**: Creative, good for brainstorming, storytelling

### Token Management

```python
# Conservative for chat
client = KimiClient(max_tokens=512)

# Standard for most tasks
client = KimiClient(max_tokens=2048)

# Long-form content
client = KimiClient(max_tokens=4096)
```

**Best Practices:**
- Start with smaller token limits and increase if needed
- Monitor token usage to optimize costs
- Use streaming for long responses to improve perceived performance

---

## Prompt Engineering

### System Messages

**Good System Messages:**
```python
# Specific and clear
"You are an expert Python developer specializing in async programming."

# With constraints
"You are a helpful assistant. Keep responses under 100 words."

# With output format
"You are a JSON API. Always respond with valid JSON only."
```

**Poor System Messages:**
```python
# Too vague
"Be helpful"

# Contradictory
"Be brief but provide lots of detail"

# Overly complex
"You are X but also Y unless Z in which case A..."
```

### User Prompts

**Effective Prompts:**

```python
# Clear and specific
"Write a Python function to merge two sorted lists. Include type hints and docstring."

# With context
"Given this data structure: {data}, write code to extract all unique email addresses."

# With examples
"Convert temperatures like this: Input: '72F' -> Output: '22.2C'"
```

**Less Effective:**

```python
# Too vague
"Help with code"

# Missing context
"Fix this bug"  # without showing the code

# Ambiguous
"Make it better"  # without specifying what to improve
```

### Multi-turn Conversations

```python
# Good: Build context gradually
messages = [
    {"role": "system", "content": "You are a math tutor."},
    {"role": "user", "content": "Explain derivatives"},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "Show me an example"},  # References previous
]

# Manage conversation length
MAX_HISTORY = 10  # Keep last 10 messages
messages = messages[-MAX_HISTORY:]
```

---

## Tool Design

### Function Design

**Good Tool Functions:**

```python
@tool_manager.register(description="Get weather forecast for a city")
def get_weather(city: str, days: int = 3) -> dict:
    """
    Get weather forecast.
    
    Args:
        city: Name of the city
        days: Number of days (1-7), default 3
        
    Returns:
        Weather data dict with temperature and conditions
    """
    # Validate inputs
    if not city:
        return {"error": "City name required"}
    if not 1 <= days <= 7:
        return {"error": "Days must be between 1 and 7"}
    
    try:
        # Make API call
        result = fetch_weather(city, days)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

**Key Principles:**
1. **Clear descriptions**: Help the model know when to use the tool
2. **Type hints**: Enable automatic schema generation
3. **Input validation**: Validate parameters before processing
4. **Error handling**: Return structured errors, don't raise exceptions
5. **Consistent output**: Use consistent dict structure for all tools

### Tool Descriptions

```python
# Good: Clear, specific, with usage hints
@tool_manager.register(
    description="Search academic papers by keyword. Call this when user asks about research or papers."
)
def search_papers(query: str, max_results: int = 10) -> dict:
    pass

# Poor: Too vague
@tool_manager.register(description="Search")
def search(q: str) -> dict:
    pass
```

### Tool Composition

```python
# Good: Atomic, single-purpose tools
@tool_manager.register(description="Fetch user data")
def get_user(user_id: int) -> dict:
    pass

@tool_manager.register(description="Update user data")
def update_user(user_id: int, data: dict) -> dict:
    pass

# Avoid: Multi-purpose tools
@tool_manager.register(description="Manage users")
def manage_user(action: str, user_id: int, data: dict = None) -> dict:
    # Too complex, model may struggle to use correctly
    pass
```

---

## Performance Optimization

### Streaming for Better UX

```python
# Good: Stream long responses
print("Response: ", end="", flush=True)
for chunk in client.chat(messages, stream=True):
    print(chunk, end="", flush=True)
print()

# Avoid: Waiting for complete response for long content
response = client.chat(long_prompt)  # User waits entire time
print(response)
```

### Batch Processing

```python
# Good: Process multiple requests concurrently
from concurrent.futures import ThreadPoolExecutor

def process_batch(prompts: List[str], client: KimiClient):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(client.simple_chat, prompt)
            for prompt in prompts
        ]
        return [f.result() for f in futures]

# Avoid: Sequential processing when order doesn't matter
results = [client.simple_chat(p) for p in prompts]  # Slow
```

### Caching

```python
from functools import lru_cache
import hashlib

class CachedClient:
    def __init__(self, client):
        self.client = client
        self.cache = {}
    
    def chat(self, messages):
        # Create cache key
        key = hashlib.md5(str(messages).encode()).hexdigest()
        
        if key in self.cache:
            return self.cache[key]
        
        result = self.client.chat(messages)
        self.cache[key] = result
        return result
```

### Context Window Management

```python
def manage_context(messages: List[dict], max_tokens: int = 4000):
    """Keep conversation within token limit."""
    # Simple approach: keep last N messages
    MAX_MESSAGES = 20
    
    # Always keep system message
    system_msgs = [m for m in messages if m["role"] == "system"]
    recent_msgs = messages[-MAX_MESSAGES:]
    
    return system_msgs + recent_msgs

# Use in conversation
messages = manage_context(messages)
response = client.chat(messages)
```

---

## Error Handling

### Robust Client Usage

```python
import time
from typing import Optional

def chat_with_retry(
    client: KimiClient,
    messages: List[dict],
    max_retries: int = 3
) -> Optional[str]:
    """Chat with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            return client.chat(messages)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                return None
            
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    return None
```

### Timeout Handling

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def chat_with_timeout(
    client: KimiClient,
    messages: List[dict],
    timeout: int = 30
) -> str:
    """Execute chat with timeout."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(client.chat, messages)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            return "Request timed out. Please try again."
```

### Graceful Degradation

```python
def chat_with_fallback(
    client: KimiClient,
    messages: List[dict],
    fallback: str = "I'm sorry, I'm having trouble responding right now."
) -> str:
    """Chat with fallback message."""
    try:
        return client.chat(messages)
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        return fallback
```

---

## Security Considerations

### Input Validation

```python
def validate_input(user_input: str) -> bool:
    """Validate user input."""
    # Length check
    if len(user_input) > 10000:
        return False
    
    # Content check (example)
    dangerous_patterns = ["<script>", "DROP TABLE", "eval("]
    if any(pattern in user_input.lower() for pattern in dangerous_patterns):
        return False
    
    return True

# Use validation
if validate_input(user_input):
    response = client.simple_chat(user_input)
else:
    response = "Invalid input. Please try again."
```

### Tool Safety

```python
# Good: Sandboxed tool execution
@tool_manager.register(description="Execute safe calculation")
def calculate(expression: str) -> dict:
    """Execute math calculation safely."""
    try:
        # Whitelist allowed functions
        allowed = {"__builtins__": {}}
        result = eval(expression, allowed)
        return {"result": result}
    except Exception as e:
        return {"error": "Invalid expression"}

# Dangerous: Unrestricted execution
@tool_manager.register(description="Execute code")  # DON'T DO THIS
def execute_code(code: str) -> dict:
    exec(code)  # DANGEROUS: Arbitrary code execution
```

### API Key Management

```python
# Good: Use environment variables
import os
from kimi_k2.client import KimiClient

api_key = os.environ.get("KIMI_API_KEY", "dummy")
client = KimiClient(
    base_url=os.environ.get("KIMI_BASE_URL"),
    api_key=api_key
)

# Bad: Hardcoded credentials
client = KimiClient(
    base_url="http://server",
    api_key="secret-key-123"  # DON'T DO THIS
)
```

---

## Production Deployment

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Chat request from user {user_id}")
logger.info(f"Tool called: {tool_name} with args: {args}")
logger.error(f"Failed to process request: {error}")
```

### Monitoring

```python
import time
from typing import Dict, Any

class MonitoredClient:
    """Client with monitoring."""
    
    def __init__(self, client):
        self.client = client
        self.metrics = {
            "total_requests": 0,
            "failed_requests": 0,
            "total_latency": 0.0
        }
    
    def chat(self, messages: List[dict]) -> str:
        """Chat with monitoring."""
        start = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            result = self.client.chat(messages)
            latency = time.time() - start
            self.metrics["total_latency"] += latency
            return result
        except Exception as e:
            self.metrics["failed_requests"] += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get monitoring metrics."""
        avg_latency = (
            self.metrics["total_latency"] / self.metrics["total_requests"]
            if self.metrics["total_requests"] > 0 else 0
        )
        
        return {
            **self.metrics,
            "average_latency": avg_latency,
            "error_rate": (
                self.metrics["failed_requests"] / self.metrics["total_requests"]
                if self.metrics["total_requests"] > 0 else 0
            )
        }
```

### Health Checks

```python
def health_check(client: KimiClient) -> bool:
    """Check if service is healthy."""
    try:
        response = client.simple_chat("test", max_tokens=5)
        return len(response) > 0
    except Exception:
        return False

# Use in production
if not health_check(client):
    # Alert, failover, or retry
    logger.error("Health check failed")
```

### Rate Limiting

```python
import time
from collections import deque

class RateLimitedClient:
    """Client with rate limiting."""
    
    def __init__(self, client, max_requests_per_minute: int = 60):
        self.client = client
        self.max_requests = max_requests_per_minute
        self.requests = deque()
    
    def chat(self, messages: List[dict]) -> str:
        """Chat with rate limiting."""
        now = time.time()
        
        # Remove requests older than 1 minute
        while self.requests and self.requests[0] < now - 60:
            self.requests.popleft()
        
        # Check rate limit
        if len(self.requests) >= self.max_requests:
            wait_time = 60 - (now - self.requests[0])
            raise Exception(f"Rate limit exceeded. Wait {wait_time:.1f}s")
        
        self.requests.append(now)
        return self.client.chat(messages)
```

---

## Summary

**Key Takeaways:**

1. **Use temperature=0.6** for Kimi-K2 (optimal balance)
2. **Write clear, specific prompts** with context
3. **Design atomic, single-purpose tools** with good error handling
4. **Stream long responses** for better UX
5. **Implement retry logic** and timeouts
6. **Validate inputs** and sanitize tool execution
7. **Log and monitor** in production
8. **Cache when appropriate** to reduce latency
9. **Manage context windows** to stay within limits
10. **Use environment variables** for sensitive data

Following these practices will help you build robust, efficient, and secure applications with Kimi-K2.

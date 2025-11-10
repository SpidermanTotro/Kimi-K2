# Troubleshooting Guide

Common issues and solutions when working with Kimi-K2 utilities.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Connection Problems](#connection-problems)
3. [Performance Issues](#performance-issues)
4. [Tool Calling Issues](#tool-calling-issues)
5. [Memory Issues](#memory-issues)
6. [Common Errors](#common-errors)

---

## Installation Issues

### Issue: pip install fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions:**

1. Update pip:
```bash
pip install --upgrade pip
```

2. Use Python 3.8+:
```bash
python --version  # Should be 3.8 or higher
```

3. Install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Issue: Module not found after installation

**Symptoms:**
```python
ModuleNotFoundError: No module named 'kimi_k2'
```

**Solutions:**

1. Install in editable mode:
```bash
pip install -e .
```

2. Check installation:
```bash
pip list | grep kimi
```

3. Verify Python path:
```python
import sys
print(sys.path)
```

---

## Connection Problems

### Issue: Cannot connect to service

**Symptoms:**
```
ConnectionError: Cannot connect to http://localhost:8000
```

**Solutions:**

1. Check if service is running:
```bash
curl http://localhost:8000/health
```

2. Verify URL:
```python
import requests
response = requests.get("http://localhost:8000/v1/models")
print(response.status_code)
```

3. Check firewall/network:
```bash
# Test from command line
telnet localhost 8000
```

4. Try different base URL formats:
```python
# Try with /v1
client = KimiClient(base_url="http://localhost:8000/v1")

# Try without path
client = KimiClient(base_url="http://localhost:8000")
```

### Issue: SSL/TLS errors

**Symptoms:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**

1. For development (not production):
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

2. Use HTTP instead of HTTPS for local:
```python
client = KimiClient(base_url="http://localhost:8000")
```

---

## Performance Issues

### Issue: Slow responses

**Symptoms:**
- Long wait times for responses
- Timeouts

**Solutions:**

1. Check GPU utilization:
```bash
nvidia-smi
```

2. Reduce max_tokens:
```python
client = KimiClient(max_tokens=512)  # Instead of 2048
```

3. Use streaming:
```python
for chunk in client.chat(messages, stream=True):
    print(chunk, end="")
```

4. Monitor latency:
```python
from kimi_k2.benchmark.runner import BenchmarkRunner
runner = BenchmarkRunner(client)
stats = runner.run_latency_test(["test"], num_runs=5)
print(stats)
```

### Issue: High memory usage

**Symptoms:**
- Out of memory errors
- Slow performance

**Solutions:**

1. Limit conversation history:
```python
# Keep only last 10 messages
messages = messages[-10:]
```

2. Reduce batch size in deployment config

3. Clear cache periodically:
```python
import gc
gc.collect()
```

---

## Tool Calling Issues

### Issue: Tools not being called

**Symptoms:**
- Model doesn't use available tools
- Tries to answer without tools

**Solutions:**

1. Improve tool descriptions:
```python
@tm.register(
    description="Get weather for a city. Call this when user asks about weather or temperature."
)
def get_weather(city: str):
    pass
```

2. Be explicit in prompt:
```python
messages = [{
    "role": "user",
    "content": "What's the weather in Tokyo? Use the weather tool to check."
}]
```

3. Verify tool schemas:
```python
schemas = tm.get_tool_schemas()
print(json.dumps(schemas, indent=2))
```

### Issue: Tool call errors

**Symptoms:**
```
KeyError: 'tool_name'
TypeError: missing required argument
```

**Solutions:**

1. Check tool registration:
```python
print(tm.get_tool_map().keys())
```

2. Verify function signature matches schema:
```python
import inspect
sig = inspect.signature(my_tool)
print(sig)
```

3. Add error handling in tools:
```python
@tm.register()
def my_tool(arg: str) -> dict:
    try:
        # Tool logic
        return {"result": "success"}
    except Exception as e:
        return {"error": str(e)}
```

### Issue: Infinite tool calling loop

**Symptoms:**
- Reaches max_iterations
- Same tool called repeatedly

**Solutions:**

1. Reduce max_iterations:
```python
response = client.chat_with_tools(
    messages=messages,
    tools=tools,
    tool_map=tool_map,
    max_iterations=3  # Reduce from default 10
)
```

2. Improve tool responses:
```python
# Bad: Vague response
return {"status": "ok"}

# Good: Informative response
return {
    "status": "success",
    "data": actual_data,
    "message": "Weather data retrieved successfully"
}
```

---

## Memory Issues

### Issue: Out of memory (OOM)

**Symptoms:**
```
RuntimeError: CUDA out of memory
MemoryError
```

**Solutions:**

1. Reduce max_tokens:
```python
client = KimiClient(max_tokens=1024)
```

2. Clear conversation history:
```python
messages = messages[-5:]  # Keep only recent messages
```

3. Use smaller batch sizes in deployment

4. Check GPU memory:
```bash
nvidia-smi
```

### Issue: Memory leaks

**Symptoms:**
- Memory usage grows over time
- Performance degrades

**Solutions:**

1. Clear caches:
```python
import gc
gc.collect()
```

2. Recreate client periodically:
```python
# After N requests
if request_count % 1000 == 0:
    client = KimiClient(base_url=url)
```

---

## Common Errors

### Error: "finish_reason != 'tool_calls'"

**Issue:**
Tool calling expected but didn't happen

**Solution:**
```python
# Check if response is valid
response = client.chat_with_tools(messages, tools, tool_map)
if response is None:
    print("No response received")
elif "Maximum" in response:
    print("Hit iteration limit")
```

### Error: "Temperature must be between 0 and 2"

**Issue:**
Invalid temperature value

**Solution:**
```python
# Use valid range
client = KimiClient(temperature=0.6)  # Good
# client = KimiClient(temperature=3.0)  # Bad
```

### Error: "Invalid JSON in function arguments"

**Issue:**
Tool received malformed JSON

**Solution:**
```python
import json

def safe_tool(args_str: str):
    try:
        args = json.loads(args_str)
        # Process args
    except json.JSONDecodeError:
        return {"error": "Invalid JSON arguments"}
```

### Error: "Context length exceeded"

**Issue:**
Messages too long for model

**Solution:**
```python
def truncate_messages(messages, max_tokens=4000):
    """Keep conversation within limit."""
    # Estimate ~4 chars per token
    max_chars = max_tokens * 4
    
    # Keep system + recent messages
    system = [m for m in messages if m["role"] == "system"]
    others = [m for m in messages if m["role"] != "system"]
    
    # Truncate from oldest
    while sum(len(m["content"]) for m in others) > max_chars:
        if others:
            others.pop(0)
    
    return system + others

messages = truncate_messages(messages)
```

---

## Debug Mode

### Enable verbose logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now all kimi_k2 operations will log
client = KimiClient(base_url="http://localhost:8000")
```

### Test with minimal example

```python
from kimi_k2.client import KimiClient

# Simplest possible test
client = KimiClient(base_url="http://localhost:8000")
try:
    response = client.simple_chat("Hello")
    print(f"Success: {response}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

### Verify tool schemas

```python
from kimi_k2.tools import ToolManager
import json

tm = ToolManager()

@tm.register(description="Test tool")
def test_tool(arg: str) -> dict:
    return {"result": arg}

# Print schema to verify
print(json.dumps(tm.get_tool_schemas(), indent=2))
```

---

## Getting Help

If you're still stuck:

1. **Check logs**: Enable DEBUG logging to see detailed errors
2. **Minimal reproduction**: Create smallest example that shows the issue
3. **Check version**: Ensure you're using latest version
4. **Search issues**: Look for similar issues on GitHub
5. **Ask community**: Post on Discord or GitHub Discussions
6. **File issue**: Create detailed bug report with reproduction steps

### Bug Report Template

```markdown
**Environment:**
- Python version: 
- kimi_k2 version: 
- OS: 

**Issue:**
Brief description

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. ...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Code:**
```python
# Minimal reproduction
```

**Error Message:**
```
Full error traceback
```
```

---

## Additional Resources

- **Documentation**: See [docs/](../) directory
- **Examples**: See [src/kimi_k2/examples/](../src/kimi_k2/examples/)
- **Tests**: See [tests/](../tests/) for working examples
- **Discord**: Join community for help
- **GitHub Issues**: Report bugs and request features

# Kimi K3 Skills and Examples Guide

This guide demonstrates Kimi K3's powerful AI capabilities through practical before-and-after examples and real-world coding scenarios. Learn how to leverage Kimi K3's agentic intelligence for various development tasks.

## Table of Contents
- [AI Skills Overview](#ai-skills-overview)
- [Before & After Examples](#before--after-examples)
- [Real Coding Examples](#real-coding-examples)
- [Tool Use Demonstrations](#tool-use-demonstrations)
- [Advanced Agentic Workflows](#advanced-agentic-workflows)

---

## AI Skills Overview

Kimi K3 excels in several key areas:

1. **Coding & Development**: Write, debug, and optimize code across multiple languages
2. **Reasoning & Problem Solving**: Break down complex problems into manageable steps
3. **Tool Usage**: Intelligently use external tools and APIs to accomplish tasks
4. **Agentic Intelligence**: Autonomous decision-making and multi-step task execution
5. **Mathematical Reasoning**: Solve complex mathematical and logical problems

---

## Before & After Examples

### Example 1: Code Refactoring

**Before: Inefficient Data Processing**
```python
# Original code - inefficient and hard to read
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result

data = [1, -2, 3, -4, 5]
print(process_data(data))
```

**After: Using Kimi K3 for Optimization**
```python
# Kimi K3 refactored - efficient and readable
def process_data(data):
    """Process data by doubling positive values.
    
    Args:
        data: List of numeric values
        
    Returns:
        List of doubled positive values
    """
    return [x * 2 for x in data if x > 0]

data = [1, -2, 3, -4, 5]
print(process_data(data))  # Output: [2, 6, 10]
```

**Improvements:**
- ✅ Added comprehensive docstring
- ✅ Used list comprehension for better performance
- ✅ More Pythonic and readable code
- ✅ Same functionality with cleaner implementation

---

### Example 2: Bug Detection and Fix

**Before: Code with Subtle Bug**
```javascript
// Original code - contains off-by-one error
function findMaxValue(arr) {
    let max = arr[0];
    for (let i = 0; i < arr.length - 1; i++) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    return max;
}

console.log(findMaxValue([1, 5, 3, 9, 2])); // Returns 5, should be 9!
```

**After: Kimi K3 Identified and Fixed**
```javascript
// Kimi K3 fixed version
function findMaxValue(arr) {
    if (!arr || arr.length === 0) {
        throw new Error('Array must not be empty');
    }
    
    let max = arr[0];
    for (let i = 1; i < arr.length; i++) {  // Fixed: i < arr.length instead of arr.length - 1
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    return max;
}

console.log(findMaxValue([1, 5, 3, 9, 2])); // Correctly returns 9
```

**Improvements:**
- ✅ Fixed off-by-one error (was missing last element)
- ✅ Added input validation
- ✅ Added error handling for edge cases
- ✅ Started loop at index 1 (optimization)

---

### Example 3: Algorithm Improvement

**Before: Inefficient Search**
```python
# Original - O(n²) complexity
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates

numbers = [1, 2, 3, 2, 4, 5, 1, 6]
print(find_duplicates(numbers))
```

**After: Kimi K3 Optimized**
```python
# Kimi K3 optimized - O(n) complexity
def find_duplicates(arr):
    """Find all duplicate elements in an array.
    
    Args:
        arr: List of elements
        
    Returns:
        List of elements that appear more than once
    """
    seen = set()
    duplicates = set()
    
    for item in arr:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    
    return list(duplicates)

numbers = [1, 2, 3, 2, 4, 5, 1, 6]
print(find_duplicates(numbers))  # Output: [1, 2]
```

**Improvements:**
- ✅ Reduced time complexity from O(n²) to O(n)
- ✅ Used sets for constant-time lookups
- ✅ More efficient memory usage
- ✅ Added clear documentation

---

## Real Coding Examples

### Example 1: Building a REST API with Error Handling

**Task**: Create a robust REST API endpoint with proper error handling and validation.

```python
from flask import Flask, request, jsonify
from typing import Dict, Any
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data store (in production, use a database)
users_db: Dict[int, Dict[str, Any]] = {}
user_id_counter = 1

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user with validation and error handling."""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Required fields validation
        required_fields = ['name', 'email']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Email validation
        if '@' not in data['email']:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Create user
        global user_id_counter
        user_id = user_id_counter
        user_id_counter += 1
        
        user = {
            'id': user_id,
            'name': data['name'],
            'email': data['email'],
            'age': data.get('age')
        }
        
        users_db[user_id] = user
        logger.info(f'User created: {user_id}')
        
        return jsonify(user), 201
        
    except Exception as e:
        logger.error(f'Error creating user: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """Retrieve a user by ID."""
    try:
        user = users_db.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user), 200
        
    except Exception as e:
        logger.error(f'Error retrieving user {user_id}: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Key Features:**
- ✅ Input validation and sanitization
- ✅ Proper HTTP status codes
- ✅ Error handling and logging
- ✅ Type hints for better code clarity
- ✅ RESTful design principles

---

### Example 2: Asynchronous Data Processing Pipeline

**Task**: Build an efficient async pipeline for processing large datasets.

```python
import asyncio
import aiohttp
from typing import List, Dict, Any
import json

async def fetch_data(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """Fetch data from a URL asynchronously."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {'error': f'Status {response.status}'}
    except Exception as e:
        return {'error': str(e)}

async def process_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single data item."""
    # Simulate processing time
    await asyncio.sleep(0.1)
    
    # Example processing: extract and transform data
    return {
        'id': item.get('id'),
        'processed': True,
        'data': item.get('data', '').upper()
    }

async def process_batch(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process a batch of items concurrently."""
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)

async def data_pipeline(urls: List[str]) -> List[Dict[str, Any]]:
    """Main pipeline: fetch and process data from multiple sources."""
    all_results = []
    
    async with aiohttp.ClientSession() as session:
        # Fetch all data concurrently
        fetch_tasks = [fetch_data(session, url) for url in urls]
        fetched_data = await asyncio.gather(*fetch_tasks)
        
        # Filter out errors
        valid_data = [d for d in fetched_data if 'error' not in d]
        
        # Process in batches
        batch_size = 10
        for i in range(0, len(valid_data), batch_size):
            batch = valid_data[i:i + batch_size]
            processed = await process_batch(batch)
            all_results.extend(processed)
    
    return all_results

# Example usage
async def main():
    urls = [
        'https://api.example.com/data/1',
        'https://api.example.com/data/2',
        'https://api.example.com/data/3'
    ]
    
    results = await data_pipeline(urls)
    print(f'Processed {len(results)} items')
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
```

**Key Features:**
- ✅ Asynchronous I/O for better performance
- ✅ Concurrent processing of multiple items
- ✅ Error handling at multiple levels
- ✅ Batch processing for efficiency
- ✅ Type hints and documentation

---

### Example 3: Test-Driven Development Example

**Task**: Implement a calculator with comprehensive tests.

```python
# calculator.py
from typing import Union

class Calculator:
    """A simple calculator with basic operations."""
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Divide a by b.
        
        Raises:
            ValueError: If b is zero.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
        """Raise base to the power of exponent."""
        return base ** exponent


# test_calculator.py
import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    """Test suite for Calculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calc = Calculator()
    
    def test_add(self):
        """Test addition operation."""
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(0.1, 0.2), 0.30000000000000004)  # Float precision
    
    def test_subtract(self):
        """Test subtraction operation."""
        self.assertEqual(self.calc.subtract(5, 3), 2)
        self.assertEqual(self.calc.subtract(3, 5), -2)
        self.assertEqual(self.calc.subtract(0, 0), 0)
    
    def test_multiply(self):
        """Test multiplication operation."""
        self.assertEqual(self.calc.multiply(3, 4), 12)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
        self.assertEqual(self.calc.multiply(0, 100), 0)
    
    def test_divide(self):
        """Test division operation."""
        self.assertEqual(self.calc.divide(10, 2), 5.0)
        self.assertEqual(self.calc.divide(7, 2), 3.5)
        self.assertAlmostEqual(self.calc.divide(1, 3), 0.333333, places=5)
    
    def test_divide_by_zero(self):
        """Test division by zero raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.calc.divide(10, 0)
        self.assertIn("Cannot divide by zero", str(context.exception))
    
    def test_power(self):
        """Test power operation."""
        self.assertEqual(self.calc.power(2, 3), 8)
        self.assertEqual(self.calc.power(5, 0), 1)
        self.assertEqual(self.calc.power(4, 0.5), 2.0)

if __name__ == '__main__':
    unittest.main()
```

**Key Features:**
- ✅ Complete test coverage
- ✅ Edge case testing
- ✅ Proper exception handling
- ✅ Clear documentation
- ✅ Type hints throughout

---

## Tool Use Demonstrations

### Example 1: Weather Information Tool

**Scenario**: Create an AI assistant that uses a weather API to provide information.

```python
import json
from openai import OpenAI

# Initialize client (pointing to Kimi K3)
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"
)

# Define the weather tool
def get_weather(city: str, units: str = "celsius") -> dict:
    """
    Simulate getting weather information for a city.
    In production, this would call a real weather API.
    """
    # Mock data for demonstration
    weather_data = {
        "Beijing": {"temp": 15, "condition": "Sunny", "humidity": 45},
        "New York": {"temp": 22, "condition": "Cloudy", "humidity": 60},
        "London": {"temp": 12, "condition": "Rainy", "humidity": 80},
        "Tokyo": {"temp": 18, "condition": "Clear", "humidity": 55}
    }
    
    data = weather_data.get(city, {"temp": 20, "condition": "Unknown", "humidity": 50})
    data["units"] = units
    data["city"] = city
    return data

# Tool schema for Kimi K3
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather information for a city. Use this when the user asks about weather conditions.",
        "parameters": {
            "type": "object",
            "required": ["city"],
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name (e.g., 'Beijing', 'New York')"
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature units",
                    "default": "celsius"
                }
            }
        }
    }
}]

# Map tool names to functions
tool_map = {
    "get_weather": get_weather
}

def chat_with_weather_tool(user_message: str):
    """Chat with Kimi K3 using weather tool."""
    messages = [
        {"role": "system", "content": "You are a helpful weather assistant. When users ask about weather, use the available tool to get accurate information."},
        {"role": "user", "content": user_message}
    ]
    
    finish_reason = None
    
    # Tool calling loop
    while finish_reason is None or finish_reason == "tool_calls":
        response = client.chat.completions.create(
            model="kimi-k3",
            messages=messages,
            temperature=0.6,
            tools=tools,
            tool_choice="auto"
        )
        
        choice = response.choices[0]
        finish_reason = choice.finish_reason
        
        if finish_reason == "tool_calls":
            # Add assistant's message with tool calls
            messages.append(choice.message)
            
            # Execute each tool call
            for tool_call in choice.message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"\n🔧 Tool Call: {function_name}")
                print(f"   Arguments: {function_args}")
                
                # Execute the function
                function_to_call = tool_map[function_name]
                function_result = function_to_call(**function_args)
                
                print(f"   Result: {function_result}")
                
                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
    
    # Print final response
    print(f"\n💬 Assistant: {choice.message.content}")
    return choice.message.content

# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Weather Assistant Demo")
    print("=" * 60)
    
    # Example 1: Single city
    chat_with_weather_tool("What's the weather like in Beijing?")
    
    print("\n" + "=" * 60 + "\n")
    
    # Example 2: Multiple cities
    chat_with_weather_tool("Can you compare the weather in Tokyo and London?")
```

**Output Example:**
```
============================================================
Weather Assistant Demo
============================================================

🔧 Tool Call: get_weather
   Arguments: {'city': 'Beijing'}
   Result: {'temp': 15, 'condition': 'Sunny', 'humidity': 45, 'units': 'celsius', 'city': 'Beijing'}

💬 Assistant: The weather in Beijing is currently sunny with a temperature of 15°C and humidity at 45%. It's a pleasant day!

============================================================

🔧 Tool Call: get_weather
   Arguments: {'city': 'Tokyo'}
   Result: {'temp': 18, 'condition': 'Clear', 'humidity': 55, 'units': 'celsius', 'city': 'Tokyo'}

🔧 Tool Call: get_weather
   Arguments: {'city': 'London'}
   Result: {'temp': 12, 'condition': 'Rainy', 'humidity': 80, 'units': 'celsius', 'city': 'London'}

💬 Assistant: Here's a comparison:
- Tokyo: Clear skies, 18°C, 55% humidity
- London: Rainy conditions, 12°C, 80% humidity
Tokyo is warmer and has better weather conditions today!
```

---

### Example 2: Database Query Tool

**Scenario**: Create an AI assistant that can query a database using natural language.

```python
import sqlite3
import json
from openai import OpenAI
from typing import List, Dict, Any

# Initialize database
def init_database():
    """Create and populate a sample database."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            salary INTEGER NOT NULL,
            hire_date TEXT NOT NULL
        )
    ''')
    
    # Insert sample data
    employees = [
        (1, 'Alice Johnson', 'Engineering', 95000, '2020-01-15'),
        (2, 'Bob Smith', 'Marketing', 75000, '2019-03-20'),
        (3, 'Charlie Brown', 'Engineering', 105000, '2018-07-10'),
        (4, 'Diana Prince', 'Sales', 85000, '2021-02-28'),
        (5, 'Eve Davis', 'Engineering', 92000, '2020-09-05')
    ]
    
    cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?)', employees)
    conn.commit()
    
    return conn

# Database query tool
def query_database(query: str, conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Execute a SQL query and return results.
    
    Args:
        query: SQL query to execute
        conn: Database connection
        
    Returns:
        Dictionary with query results or error message
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Fetch results
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        results = [dict(zip(columns, row)) for row in rows]
        
        return {
            "success": True,
            "data": results,
            "row_count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Tool schema
db_tools = [{
    "type": "function",
    "function": {
        "name": "query_database",
        "description": "Execute a SQL query on the employee database. Use SELECT statements to retrieve data. Available table: employees (columns: id, name, department, salary, hire_date)",
        "parameters": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL SELECT query to execute"
                }
            }
        }
    }
}]

def database_assistant(user_question: str, conn: sqlite3.Connection):
    """AI assistant that can query the database."""
    client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
    
    messages = [
        {"role": "system", "content": "You are a database assistant. When users ask questions about employees, use the query_database tool to get the information. Always write proper SQL queries."},
        {"role": "user", "content": user_question}
    ]
    
    tool_map = {
        "query_database": lambda query: query_database(query, conn)
    }
    
    finish_reason = None
    
    while finish_reason is None or finish_reason == "tool_calls":
        response = client.chat.completions.create(
            model="kimi-k3",
            messages=messages,
            temperature=0.3,
            tools=db_tools,
            tool_choice="auto"
        )
        
        choice = response.choices[0]
        finish_reason = choice.finish_reason
        
        if finish_reason == "tool_calls":
            messages.append(choice.message)
            
            for tool_call in choice.message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"\n📊 Executing: {function_args['query']}")
                
                function_result = tool_map[function_name](**function_args)
                print(f"   Found {function_result.get('row_count', 0)} results")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
    
    print(f"\n💬 {choice.message.content}")
    return choice.message.content

# Example usage
if __name__ == "__main__":
    conn = init_database()
    
    print("=" * 60)
    print("Database Assistant Demo")
    print("=" * 60)
    
    # Example queries
    questions = [
        "How many engineers do we have?",
        "What's the average salary in the Engineering department?",
        "Who are the top 3 highest paid employees?"
    ]
    
    for question in questions:
        print(f"\n❓ Question: {question}")
        database_assistant(question, conn)
        print()
    
    conn.close()
```

---

## Advanced Agentic Workflows

### Example: Multi-Step Problem Solving

**Scenario**: Build a code analyzer that can review code, identify issues, and suggest improvements.

```python
from typing import List, Dict, Any
import json

class CodeReviewAgent:
    """An agentic code reviewer that performs multi-step analysis."""
    
    def __init__(self, client):
        self.client = client
        self.model = "kimi-k3"
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Perform comprehensive code analysis."""
        
        # Step 1: Initial assessment
        print("🔍 Step 1: Analyzing code structure...")
        structure_analysis = self._analyze_structure(code, language)
        
        # Step 2: Security review
        print("🔒 Step 2: Checking for security issues...")
        security_review = self._check_security(code, language)
        
        # Step 3: Performance analysis
        print("⚡ Step 3: Analyzing performance...")
        performance_analysis = self._analyze_performance(code, language)
        
        # Step 4: Generate recommendations
        print("💡 Step 4: Generating recommendations...")
        recommendations = self._generate_recommendations(
            structure_analysis,
            security_review,
            performance_analysis
        )
        
        return {
            "structure": structure_analysis,
            "security": security_review,
            "performance": performance_analysis,
            "recommendations": recommendations
        }
    
    def _analyze_structure(self, code: str, language: str) -> str:
        """Analyze code structure and organization."""
        prompt = f"""Analyze the structure of this {language} code:

{code}

Focus on:
- Code organization
- Function/method design
- Variable naming
- Code readability

Provide a brief assessment."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _check_security(self, code: str, language: str) -> str:
        """Check for security vulnerabilities."""
        prompt = f"""Review this {language} code for security issues:

{code}

Look for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure data handling
- Input validation issues
- Authentication/authorization problems

List any concerns found."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _analyze_performance(self, code: str, language: str) -> str:
        """Analyze code performance."""
        prompt = f"""Analyze the performance characteristics of this {language} code:

{code}

Consider:
- Time complexity
- Space complexity
- Potential bottlenecks
- Optimization opportunities

Provide analysis."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _generate_recommendations(self, structure: str, security: str, performance: str) -> str:
        """Generate final recommendations based on all analyses."""
        prompt = f"""Based on the following code analysis, provide specific, actionable recommendations:

Structure Analysis:
{structure}

Security Review:
{security}

Performance Analysis:
{performance}

Provide:
1. Top 3 priority improvements
2. Specific code changes to make
3. Best practices to follow"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800
        )
        
        return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    from openai import OpenAI
    
    client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
    agent = CodeReviewAgent(client)
    
    # Sample code to review
    sample_code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    result = db.execute(query)
    return result
'''
    
    print("=" * 60)
    print("Code Review Agent - Multi-Step Analysis")
    print("=" * 60)
    print(f"\nCode to review:\n{sample_code}\n")
    
    results = agent.analyze_code(sample_code, "Python")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    print("\n📋 STRUCTURE ANALYSIS:")
    print(results["structure"])
    
    print("\n🔒 SECURITY REVIEW:")
    print(results["security"])
    
    print("\n⚡ PERFORMANCE ANALYSIS:")
    print(results["performance"])
    
    print("\n💡 RECOMMENDATIONS:")
    print(results["recommendations"])
```

---

## Summary

This guide demonstrates Kimi K3's capabilities through:

1. **Before & After Examples**: Shows how Kimi K3 improves code quality, fixes bugs, and optimizes performance
2. **Real Coding Examples**: Practical implementations of REST APIs, async pipelines, and TDD
3. **Tool Use**: Integration with external tools and APIs for enhanced functionality
4. **Agentic Workflows**: Multi-step problem solving with autonomous decision-making

### Key Takeaways

- ✅ Kimi K3 excels at understanding context and making intelligent decisions
- ✅ Tool integration enables powerful agentic workflows
- ✅ Multi-step reasoning allows complex problem solving
- ✅ Code quality improvements are automatic and intelligent
- ✅ Real-world applications benefit from Kimi K3's capabilities

### Next Steps

1. Deploy Kimi K3 following the [Deployment Guide](./deploy_guidance.md)
2. Implement tool calling using the [Tool Calling Guide](./tool_call_guidance.md)
3. Experiment with your own use cases
4. Build agentic applications leveraging Kimi K3's capabilities

---

For more information, visit:
- [README](../README.md)
- [Deployment Guide](./deploy_guidance.md)
- [Tool Calling Guide](./tool_call_guidance.md)

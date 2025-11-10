"""Test suite for ToolManager."""

import pytest
from kimi_k2.tools import ToolManager


class TestToolManager:
    """Test cases for ToolManager."""

    def test_initialization(self):
        """Test tool manager initialization."""
        tm = ToolManager()
        assert len(tm.tools) == 0
        assert len(tm.tool_schemas) == 0

    def test_register_function(self):
        """Test registering a function."""
        tm = ToolManager()

        @tm.register(description="Test function")
        def test_func(arg1: str, arg2: int) -> str:
            return f"{arg1}-{arg2}"

        assert "test_func" in tm.tools
        assert len(tm.tool_schemas) == 1

        # Test function still works
        result = test_func("hello", 42)
        assert result == "hello-42"

    def test_register_with_custom_name(self):
        """Test registering with custom name."""
        tm = ToolManager()

        @tm.register(name="custom_name", description="Custom")
        def original_name():
            return "test"

        assert "custom_name" in tm.tools
        assert "original_name" not in tm.tools

    def test_get_tool_schemas(self):
        """Test getting tool schemas."""
        tm = ToolManager()

        @tm.register(description="Get weather")
        def get_weather(city: str) -> dict:
            return {"city": city, "weather": "Sunny"}

        schemas = tm.get_tool_schemas()
        assert len(schemas) == 1
        assert schemas[0]["type"] == "function"
        assert schemas[0]["function"]["name"] == "get_weather"
        assert schemas[0]["function"]["description"] == "Get weather"
        assert "parameters" in schemas[0]["function"]

    def test_get_tool_map(self):
        """Test getting tool map."""
        tm = ToolManager()

        @tm.register()
        def func1():
            return "one"

        @tm.register()
        def func2():
            return "two"

        tool_map = tm.get_tool_map()
        assert len(tool_map) == 2
        assert "func1" in tool_map
        assert "func2" in tool_map
        assert tool_map["func1"]() == "one"
        assert tool_map["func2"]() == "two"

    def test_call_tool(self):
        """Test calling a tool."""
        tm = ToolManager()

        @tm.register()
        def add(a: int, b: int) -> int:
            return a + b

        result = tm.call_tool("add", a=5, b=3)
        assert result == 8

    def test_call_tool_not_found(self):
        """Test calling non-existent tool raises error."""
        tm = ToolManager()

        with pytest.raises(KeyError):
            tm.call_tool("nonexistent")

    def test_schema_generation_with_required_params(self):
        """Test schema generation with required parameters."""
        tm = ToolManager()

        @tm.register(description="Search")
        def search(query: str, limit: int = 10) -> list:
            return []

        schema = tm.tool_schemas[0]
        params = schema["function"]["parameters"]

        assert "query" in params["required"]
        assert "limit" not in params["required"]
        assert "query" in params["properties"]
        assert "limit" in params["properties"]

    def test_schema_generation_type_mapping(self):
        """Test Python type to JSON type mapping."""
        tm = ToolManager()

        @tm.register()
        def test_types(s: str, i: int, f: float, b: bool, lst: list, d: dict):
            pass

        schema = tm.tool_schemas[0]
        props = schema["function"]["parameters"]["properties"]

        assert props["s"]["type"] == "string"
        assert props["i"]["type"] == "integer"
        assert props["f"]["type"] == "number"
        assert props["b"]["type"] == "boolean"
        assert props["lst"]["type"] == "array"
        assert props["d"]["type"] == "object"

    def test_multiple_registrations(self):
        """Test multiple function registrations."""
        tm = ToolManager()

        @tm.register(description="First")
        def func1():
            return 1

        @tm.register(description="Second")
        def func2():
            return 2

        @tm.register(description="Third")
        def func3():
            return 3

        assert len(tm.tools) == 3
        assert len(tm.tool_schemas) == 3

        schemas = tm.get_tool_schemas()
        names = [s["function"]["name"] for s in schemas]
        assert "func1" in names
        assert "func2" in names
        assert "func3" in names

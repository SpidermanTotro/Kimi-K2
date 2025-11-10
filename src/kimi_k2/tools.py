"""Tool management utilities for Kimi-K2."""

import json
import inspect
from typing import Any, Callable, Dict, List, Optional, get_type_hints
from pydantic import BaseModel, create_model


class ToolManager:
    """Manage tools for Kimi-K2 function calling."""

    def __init__(self):
        """Initialize the tool manager."""
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Decorator to register a function as a tool.

        Args:
            name: Optional custom name for the tool
            description: Optional description

        Example:
            @tool_manager.register(description="Get weather information")
            def get_weather(city: str) -> dict:
                return {"weather": "Sunny", "city": city}
        """

        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            tool_description = description or func.__doc__ or f"Tool: {tool_name}"

            # Register the function
            self.tools[tool_name] = func

            # Generate schema from function signature
            schema = self._generate_schema(func, tool_name, tool_description)
            self.tool_schemas.append(schema)

            return func

        return decorator

    def _generate_schema(
        self, func: Callable, name: str, description: str
    ) -> Dict[str, Any]:
        """Generate OpenAI function schema from a Python function.

        Args:
            func: Function to generate schema for
            name: Tool name
            description: Tool description

        Returns:
            OpenAI function schema
        """
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name, str)

            # Convert Python types to JSON schema types
            json_type = self._python_type_to_json_type(param_type)

            properties[param_name] = {
                "type": json_type,
                "description": f"Parameter: {param_name}",
            }

            # Check if parameter is required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def _python_type_to_json_type(self, python_type: type) -> str:
        """Convert Python type to JSON schema type.

        Args:
            python_type: Python type

        Returns:
            JSON schema type string
        """
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        # Handle Optional types
        origin = getattr(python_type, "__origin__", None)
        if origin is not None:
            args = getattr(python_type, "__args__", ())
            if origin is list:
                return "array"
            elif origin is dict:
                return "object"

        return type_mapping.get(python_type, "string")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get all registered tool schemas.

        Returns:
            List of tool schemas in OpenAI format
        """
        return self.tool_schemas

    def get_tool_map(self) -> Dict[str, Callable]:
        """Get mapping of tool names to functions.

        Returns:
            Dictionary of tool names to callable functions
        """
        return self.tools

    def call_tool(self, name: str, **kwargs) -> Any:
        """Call a registered tool by name.

        Args:
            name: Tool name
            **kwargs: Arguments to pass to the tool

        Returns:
            Tool result

        Raises:
            KeyError: If tool not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not found")

        return self.tools[name](**kwargs)


# Global tool manager instance
default_tool_manager = ToolManager()

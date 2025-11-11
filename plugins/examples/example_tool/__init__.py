"""
Example Tool Plugin for Kimi K2

This is an example plugin demonstrating how to create tool plugins
for the Kimi K2 system.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.loader import Plugin


class ExampleToolPlugin(Plugin):
    """Example tool plugin that demonstrates plugin capabilities."""
    
    def __init__(self, name: str, config: dict = None):
        """Initialize the example tool plugin.
        
        Args:
            name: Plugin name
            config: Plugin configuration
        """
        super().__init__(name, config)
        self.tool_name = "example_tool"
        self.description = "An example tool that processes text"
        
    def initialize(self) -> bool:
        """Initialize the plugin.
        
        Returns:
            True if initialization successful
        """
        print(f"Initializing {self.name} plugin...")
        # Add any initialization logic here
        return True
    
    def execute(self, text: str) -> dict:
        """Execute the tool's main functionality.
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary with processing results
        """
        # Example processing: count words and characters
        words = text.split()
        
        result = {
            "input": text,
            "word_count": len(words),
            "char_count": len(text),
            "char_count_no_spaces": len(text.replace(" ", "")),
            "tool": self.tool_name
        }
        
        return result
    
    def cleanup(self):
        """Cleanup plugin resources."""
        print(f"Cleaning up {self.name} plugin...")

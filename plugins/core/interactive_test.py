#!/usr/bin/env python3
"""
Interactive Testing Framework for Kimi K2 Plugins

This module provides interactive testing capabilities for plugins,
allowing developers to test plugin functionality in real-time.
"""

import argparse
import json
import logging
import sys
from typing import Any, Dict

from loader import PluginLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractiveTester:
    """Interactive testing framework for plugins."""
    
    def __init__(self, plugin_name: str):
        """Initialize the interactive tester.
        
        Args:
            plugin_name: Name of the plugin to test
        """
        self.plugin_name = plugin_name
        self.loader = PluginLoader()
        self.plugin = None
        
    def load_plugin(self) -> bool:
        """Load the plugin for testing.
        
        Returns:
            True if successful, False otherwise
        """
        self.plugin = self.loader.load_plugin(self.plugin_name)
        if self.plugin:
            logger.info(f"Successfully loaded plugin: {self.plugin_name}")
            return True
        else:
            logger.error(f"Failed to load plugin: {self.plugin_name}")
            return False
    
    def run_test(self, test_input: Any) -> Any:
        """Run a test with the given input.
        
        Args:
            test_input: Input data for the test
            
        Returns:
            Test result
        """
        if not self.plugin:
            logger.error("Plugin not loaded")
            return None
        
        try:
            result = self.plugin.execute(test_input)
            logger.info(f"Test completed successfully")
            return result
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            return None
    
    def interactive_session(self):
        """Start an interactive testing session."""
        if not self.load_plugin():
            return
        
        print(f"\n{'='*60}")
        print(f"Interactive Testing Session for: {self.plugin_name}")
        print(f"{'='*60}\n")
        print("Commands:")
        print("  test <input>  - Run a test with the given input")
        print("  info          - Show plugin information")
        print("  quit          - Exit interactive session")
        print(f"{'='*60}\n")
        
        while True:
            try:
                command = input("> ").strip()
                
                if command == "quit":
                    break
                elif command == "info":
                    info = self.plugin.get_info()
                    print(json.dumps(info, indent=2))
                elif command.startswith("test "):
                    test_input = command[5:]
                    result = self.run_test(test_input)
                    print(f"Result: {result}")
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        if self.plugin:
            self.plugin.cleanup()
            logger.info("Plugin cleanup completed")


def main():
    """Main entry point for interactive tester."""
    parser = argparse.ArgumentParser(
        description="Interactive testing for Kimi K2 plugins"
    )
    parser.add_argument(
        "--plugin",
        type=str,
        required=True,
        help="Name of the plugin to test"
    )
    
    args = parser.parse_args()
    
    tester = InteractiveTester(args.plugin)
    tester.interactive_session()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Data Formatter for Instruction Tuning
THE FORGE AI - Phase 3: Training Data Enhancement

Formats raw data into instruction tuning format for Kimi K2.
"""

import json
import argparse
from typing import Dict, List, Any
from pathlib import Path


class InstructionFormatter:
    """Format data for instruction tuning."""
    
    def __init__(self):
        self.formatted_count = 0
        
    def format(self, raw_data: List[Dict]) -> List[Dict]:
        """Format raw data into instruction tuning format."""
        formatted = []
        
        for item in raw_data:
            formatted_item = self._format_item(item)
            if formatted_item:
                formatted.append(formatted_item)
                self.formatted_count += 1
        
        return formatted
    
    def _format_item(self, item: Dict) -> Dict:
        """Format a single data item."""
        # Standard instruction tuning format
        return {
            "messages": [
                {
                    "role": "system",
                    "content": item.get("system_prompt", "You are Kimi, an AI assistant created by Moonshot AI.")
                },
                {
                    "role": "user",
                    "content": item.get("input", item.get("instruction", ""))
                },
                {
                    "role": "assistant",
                    "content": item.get("output", item.get("response", ""))
                }
            ],
            "metadata": {
                "source": item.get("source", "unknown"),
                "difficulty": item.get("difficulty", "medium"),
                "category": item.get("category", "general")
            }
        }


class CodeFormatter:
    """Format code data for training."""
    
    def format(self, code_data: List[Dict]) -> List[Dict]:
        """Format code data."""
        formatted = []
        
        for item in code_data:
            formatted_item = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert programmer."
                    },
                    {
                        "role": "user",
                        "content": self._create_code_prompt(item)
                    },
                    {
                        "role": "assistant",
                        "content": item.get("solution", "")
                    }
                ],
                "metadata": {
                    "language": item.get("language", "python"),
                    "task_type": item.get("task_type", "implementation")
                }
            }
            formatted.append(formatted_item)
        
        return formatted
    
    def _create_code_prompt(self, item: Dict) -> str:
        """Create code generation prompt."""
        prompt = f"""
{item.get('description', '')}

{item.get('requirements', '')}

Please implement the solution.
"""
        return prompt.strip()


def main():
    """Main entry point for data formatting."""
    parser = argparse.ArgumentParser(description='Format data for instruction tuning')
    parser.add_argument('--input', required=True, help='Input data file')
    parser.add_argument('--output', required=True, help='Output file')
    parser.add_argument('--format', choices=['instruction', 'code'], default='instruction')
    
    args = parser.parse_args()
    
    # Load raw data
    print(f"Loading data from {args.input}...")
    with open(args.input, 'r') as f:
        raw_data = [json.loads(line) for line in f]
    
    print(f"Loaded {len(raw_data)} items")
    
    # Format data
    if args.format == 'instruction':
        formatter = InstructionFormatter()
    else:
        formatter = CodeFormatter()
    
    formatted_data = formatter.format(raw_data)
    
    # Save formatted data
    print(f"Saving {len(formatted_data)} formatted items to {args.output}...")
    with open(args.output, 'w') as f:
        for item in formatted_data:
            f.write(json.dumps(item) + '\n')
    
    print("Formatting complete!")


if __name__ == '__main__':
    main()

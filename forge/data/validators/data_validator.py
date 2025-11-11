#!/usr/bin/env python3
"""
Data Validator
THE FORGE AI - Phase 3: Training Data Enhancement

Validates formatted training data for quality and completeness.
"""

import json
import argparse
from typing import Dict, List, Set
from collections import Counter


class DataValidator:
    """Validate training data quality."""
    
    def __init__(self):
        self.issues = []
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'warnings': 0
        }
        
    def validate(self, data: List[Dict]) -> tuple:
        """Validate a dataset."""
        self.stats['total'] = len(data)
        valid_items = []
        
        for i, item in enumerate(data):
            is_valid, issues = self._validate_item(item, i)
            
            if is_valid:
                self.stats['valid'] += 1
                valid_items.append(item)
            else:
                self.stats['invalid'] += 1
                self.issues.extend(issues)
        
        return valid_items, self.issues
    
    def _validate_item(self, item: Dict, index: int) -> tuple:
        """Validate a single item."""
        issues = []
        
        # Check required fields
        if 'messages' not in item:
            issues.append(f"Item {index}: Missing 'messages' field")
            return False, issues
        
        messages = item['messages']
        
        # Check message structure
        if not isinstance(messages, list) or len(messages) == 0:
            issues.append(f"Item {index}: 'messages' must be a non-empty list")
            return False, issues
        
        # Validate each message
        for j, msg in enumerate(messages):
            if 'role' not in msg:
                issues.append(f"Item {index}, Message {j}: Missing 'role'")
                return False, issues
            
            if 'content' not in msg:
                issues.append(f"Item {index}, Message {j}: Missing 'content'")
                return False, issues
            
            if msg['role'] not in ['system', 'user', 'assistant', 'tool']:
                issues.append(f"Item {index}, Message {j}: Invalid role '{msg['role']}'")
                return False, issues
            
            # Check content length
            content_len = len(msg['content'])
            if content_len == 0:
                issues.append(f"Item {index}, Message {j}: Empty content")
                self.stats['warnings'] += 1
            elif content_len > 100000:
                issues.append(f"Item {index}, Message {j}: Content too long ({content_len} chars)")
                self.stats['warnings'] += 1
        
        return True, issues
    
    def print_stats(self):
        """Print validation statistics."""
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        print(f"Total items:    {self.stats['total']}")
        print(f"Valid items:    {self.stats['valid']} ({self.stats['valid']/max(self.stats['total'],1)*100:.1f}%)")
        print(f"Invalid items:  {self.stats['invalid']}")
        print(f"Warnings:       {self.stats['warnings']}")
        print("="*60 + "\n")


def main():
    """Main entry point for data validation."""
    parser = argparse.ArgumentParser(description='Validate training data')
    parser.add_argument('--input', required=True, help='Input data file')
    parser.add_argument('--output', help='Output file for valid data')
    parser.add_argument('--report', help='Output file for validation report')
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading data from {args.input}...")
    with open(args.input, 'r') as f:
        data = [json.loads(line) for line in f]
    
    print(f"Loaded {len(data)} items")
    
    # Validate
    validator = DataValidator()
    valid_data, issues = validator.validate(data)
    
    validator.print_stats()
    
    # Save valid data
    if args.output:
        print(f"Saving {len(valid_data)} valid items to {args.output}...")
        with open(args.output, 'w') as f:
            for item in valid_data:
                f.write(json.dumps(item) + '\n')
    
    # Save report
    if args.report:
        print(f"Saving validation report to {args.report}...")
        report = {
            'stats': validator.stats,
            'issues': issues
        }
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
    
    # Print issues
    if issues:
        print(f"\nFound {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues)-10} more")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
THE FORGE AI - Data Analyzer
Analyze CSV, JSON, and other data formats
"""

import json
import csv
from pathlib import Path
from collections import Counter

class DataAnalyzer:
    """Analyze data files"""
    
    def analyze_csv(self, file_path: str):
        """Analyze CSV file"""
        print(f"📊 Analyzing CSV: {file_path}")
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"   Rows: {len(rows)}")
        print(f"   Columns: {len(rows[0].keys()) if rows else 0}")
        
        if rows:
            print(f"   Column names: {', '.join(rows[0].keys())}")
        
        print("   ✓ CSV analysis complete")
        return rows
    
    def analyze_json(self, file_path: str):
        """Analyze JSON file"""
        print(f"📊 Analyzing JSON: {file_path}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"   Type: {type(data).__name__}")
        
        if isinstance(data, list):
            print(f"   Items: {len(data)}")
        elif isinstance(data, dict):
            print(f"   Keys: {len(data.keys())}")
            print(f"   Top-level keys: {', '.join(list(data.keys())[:5])}")
        
        print("   ✓ JSON analysis complete")
        return data
    
    def generate_stats(self, data):
        """Generate statistics"""
        print("\n📈 Statistics:")
        
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                for key in data[0].keys():
                    values = [row.get(key) for row in data if row.get(key)]
                    print(f"   {key}: {len(values)} values")
        
        print("   ✓ Statistics generated")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='THE FORGE AI - Data Analyzer')
    parser.add_argument('file', help='Data file to analyze')
    parser.add_argument('--stats', action='store_true', help='Generate statistics')
    
    args = parser.parse_args()
    
    analyzer = DataAnalyzer()
    
    file_path = Path(args.file)
    
    if file_path.suffix == '.csv':
        data = analyzer.analyze_csv(args.file)
    elif file_path.suffix == '.json':
        data = analyzer.analyze_json(args.file)
    else:
        print(f"✗ Unsupported format: {file_path.suffix}")
        return
    
    if args.stats:
        analyzer.generate_stats(data)

if __name__ == '__main__':
    main()

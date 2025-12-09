#!/usr/bin/env python3
"""
Example: Using the AI Code Clinging Tool

This example demonstrates how to use the Code Clinging Tool
to analyze code, find vulnerabilities, and break down large files.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_clinging_tool import CodeClingingTool


def example_basic_analysis():
    """Basic file analysis example"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic File Analysis")
    print("=" * 80)
    
    tool = CodeClingingTool(verbose=False)
    
    # Analyze a single file
    result = tool.cling_to_file("build_system.py")
    
    print(f"\nAnalysis Results:")
    print(f"  • Total Lines: {result.total_lines}")
    print(f"  • Code Lines: {result.code_lines}")
    print(f"  • Quality Score: {result.quality_score}/100")
    print(f"  • Complexity: {result.complexity_score}")
    print(f"  • Vulnerabilities: {len(result.vulnerabilities)}")
    print(f"  • Functions: {len(result.functions)}")
    print(f"  • Classes: {len(result.classes)}")


def example_find_weak_spots():
    """Find all weak spots in a directory"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Find Weak Spots")
    print("=" * 80)
    
    tool = CodeClingingTool(verbose=False)
    
    # Find weak spots in current directory
    weak_spots = tool.find_weak_spots(".")
    
    print(f"\nFound {len(weak_spots)} weak spots")
    print("\nTop 5 Critical Issues:")
    
    critical = [w for w in weak_spots if w['severity'] == 'critical'][:5]
    for i, spot in enumerate(critical, 1):
        print(f"\n{i}. [{spot['severity'].upper()}] {spot['type']}")
        print(f"   File: {spot['file']}")
        if 'location' in spot:
            print(f"   Location: {spot['location']}")
        print(f"   💡 {spot['recommendation']}")


def example_break_down_file():
    """Break down a large file"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Break Down Large File")
    print("=" * 80)
    
    tool = CodeClingingTool(verbose=False)
    
    # Create a test file
    import tempfile
    
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            # Write a large file with multiple functions
            f.write("# Large file example\n\n")
            for i in range(20):
                f.write(f"def function_{i}():\n")
                f.write(f"    '''Function {i}'''\n")
                f.write(f"    result = {i} * 2\n")
                f.write(f"    return result\n\n")
            temp_file = f.name
        
        # Break it down
        segments = tool.break_down_large_file(temp_file, "/tmp/example_segments")
        
        print(f"\nBroke down file into {len(segments)} segments")
        print("Segments saved to: /tmp/example_segments/")
    finally:
        # Clean up
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)


def example_comprehensive_scan():
    """Comprehensive directory scan"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Comprehensive Directory Scan")
    print("=" * 80)
    
    tool = CodeClingingTool(verbose=False)
    
    # Scan a directory (use a small subset to keep it fast)
    os.makedirs("/tmp/scan_example", exist_ok=True)
    
    # Create some test files
    with open("/tmp/scan_example/good_code.py", "w") as f:
        f.write("""
# Well-written code
def add(a, b):
    '''Add two numbers'''
    return a + b

class Calculator:
    '''Simple calculator'''
    def multiply(self, a, b):
        '''Multiply two numbers'''
        return a * b
""")
    
    with open("/tmp/scan_example/bad_code.py", "w") as f:
        f.write("""
# Code with issues
import os
password = "admin123"
def unsafe(cmd):
    os.system(cmd)
    return eval("1+1")
""")
    
    # Scan
    report = tool.cling_to_directory("/tmp/scan_example", recursive=False)
    
    print(f"\nScan Results:")
    print(f"  • Files Analyzed: {report.total_files}")
    print(f"  • Total Lines: {report.total_lines}")
    print(f"  • Vulnerabilities: {report.total_vulnerabilities}")
    print(f"  • Critical: {report.critical_vulnerabilities}")
    print(f"  • Average Quality: {report.average_quality_score:.1f}/100")
    
    if report.recommendations:
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(report.recommendations[:3], 1):
            print(f"  {i}. {rec}")


def main():
    """Run all examples"""
    print("\n🔍 CODE CLINGING TOOL - EXAMPLES")
    print("Demonstrating the capabilities of the AI Code Analysis Tool")
    
    try:
        example_basic_analysis()
        example_find_weak_spots()
        example_break_down_file()
        example_comprehensive_scan()
        
        print("\n" + "=" * 80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nFor more information, see: docs/CODE_CLINGING_TOOL.md")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
AI Ripper CLI - Command Line Interface
======================================
Command-line interface for AI model extraction
"""

import argparse
import sys
from ai_ripper_core import AIRipper, EndpointConfig, request_ethical_consent
import json


def print_banner():
    """Print ASCII art banner"""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║                    AI RIPPER v1.0                          ║
    ║          Model Extraction & Analysis Tool                  ║
    ║                                                            ║
    ║  Extract, Analyze, and Export AI Models from Endpoints     ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def rip_command(args):
    """Handle rip command"""
    print(f"\n🔍 Ripping endpoint: {args.url}")
    
    # Request consent if required
    if not args.no_consent:
        if not request_ethical_consent():
            print("\n❌ Consent required to proceed")
            return 1
    
    # Create ripper
    ripper = AIRipper()
    
    # Configure endpoint
    config = EndpointConfig(
        url=args.url,
        api_key=args.api_key,
        timeout=args.timeout,
        max_retries=args.retries,
        scan_depth=args.depth
    )
    
    ripper.add_endpoint("target", config)
    
    # Progress callback
    def progress_callback(progress):
        print(f"  [{progress.progress_percentage:5.1f}%] {progress.current_task}")
        
        for error in progress.errors:
            print(f"  ❌ ERROR: {error}")
        progress.errors.clear()
        
        for warning in progress.warnings:
            print(f"  ⚠️  WARNING: {warning}")
        progress.warnings.clear()
    
    ripper.set_progress_callback(progress_callback)
    
    # Rip the endpoint
    print("\n📡 Connecting to endpoint...")
    success = ripper.rip_endpoint("target", args.depth)
    
    if not success:
        print("\n❌ Failed to rip endpoint")
        return 1
    
    print("\n✅ Successfully extracted model information")
    
    # Display metadata
    metadata = ripper.extracted_models["target"]
    print("\n📊 Model Metadata:")
    print(f"  Name: {metadata.name}")
    print(f"  Type: {metadata.model_type}")
    print(f"  Endpoint: {metadata.endpoint_url}")
    print(f"  Capabilities: {', '.join(metadata.capabilities) if metadata.capabilities else 'None detected'}")
    
    # Export if requested
    if args.output:
        print(f"\n💾 Exporting to {args.output}...")
        
        export_func = {
            'json': ripper.export_to_json,
            'python': ripper.export_to_python,
            'gguf': ripper.export_to_gguf,
            'onnx': ripper.export_to_onnx
        }.get(args.format)
        
        if export_func and export_func("target", args.output):
            print(f"✅ Exported successfully")
        else:
            print(f"❌ Export failed")
            return 1
    
    return 0


def compare_command(args):
    """Handle compare command"""
    print(f"\n🔍 Comparing {len(args.urls)} endpoints...")
    
    # Request consent if required
    if not args.no_consent:
        if not request_ethical_consent():
            print("\n❌ Consent required to proceed")
            return 1
    
    # Create ripper
    ripper = AIRipper()
    
    # Add all endpoints
    for i, url in enumerate(args.urls):
        name = f"endpoint_{i+1}"
        config = EndpointConfig(
            url=url,
            timeout=args.timeout,
            max_retries=args.retries,
            scan_depth=args.depth
        )
        ripper.add_endpoint(name, config)
    
    # Progress callback
    def progress_callback(progress):
        print(f"  [{progress.progress_percentage:5.1f}%] {progress.current_task}")
    
    ripper.set_progress_callback(progress_callback)
    
    # Rip all endpoints
    print("\n📡 Extracting from all endpoints...")
    endpoint_names = [f"endpoint_{i+1}" for i in range(len(args.urls))]
    results = ripper.rip_multiple_endpoints(endpoint_names, args.depth)
    
    # Display results
    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    
    successful = sum(1 for success in results.values() if success)
    print(f"\nSuccessful: {successful}/{len(args.urls)}")
    
    # Compare
    comparison = ripper.compare_endpoints([name for name, success in results.items() if success])
    
    print("\n📊 Endpoint Details:")
    for endpoint_data in comparison['endpoints']:
        print(f"\n  {endpoint_data['name']}:")
        print(f"    Model: {endpoint_data['model_name']}")
        print(f"    URL: {endpoint_data['url']}")
        print(f"    Capabilities: {', '.join(endpoint_data['capabilities']) if endpoint_data['capabilities'] else 'None'}")
    
    print("\n📈 Metrics:")
    print(f"  Average Response Times:")
    for name, time in comparison['metrics']['avg_response_time'].items():
        print(f"    {name}: {time:.3f}s")
    
    # Export comparison if requested
    if args.output:
        print(f"\n💾 Exporting comparison to {args.output}...")
        try:
            with open(args.output, 'w') as f:
                json.dump(comparison, f, indent=2)
            print("✅ Exported successfully")
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
            return 1
    
    return 0


def list_formats_command(args):
    """Handle list-formats command"""
    print("\n📦 Available Export Formats:\n")
    
    formats = [
        ("JSON", "JavaScript Object Notation - Standard metadata format"),
        ("Python", "Python configuration file - Easy to import in Python projects"),
        ("GGUF", "GGUF model format - Compatible with llama.cpp"),
        ("ONNX", "Open Neural Network Exchange - Cross-platform model format")
    ]
    
    for fmt, description in formats:
        print(f"  {fmt:10} - {description}")
    
    print()
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Ripper - Extract and analyze AI models from endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rip a single endpoint
  %(prog)s rip http://localhost:8000 -o model.json
  
  # Rip with custom settings
  %(prog)s rip http://api.example.com --api-key YOUR_KEY --depth 5 -o model.py -f python
  
  # Compare multiple endpoints
  %(prog)s compare http://endpoint1.com http://endpoint2.com -o comparison.json
  
  # List available export formats
  %(prog)s list-formats
        """
    )
    
    # Add version
    parser.add_argument('--version', action='version', version='AI Ripper 1.0')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Rip command
    rip_parser = subparsers.add_parser('rip', help='Rip a single endpoint')
    rip_parser.add_argument('url', help='Endpoint URL')
    rip_parser.add_argument('-k', '--api-key', help='API key for authentication')
    rip_parser.add_argument('-o', '--output', help='Output file path')
    rip_parser.add_argument('-f', '--format', choices=['json', 'python', 'gguf', 'onnx'], 
                           default='json', help='Export format (default: json)')
    rip_parser.add_argument('-t', '--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')
    rip_parser.add_argument('-r', '--retries', type=int, default=3, help='Max retries (default: 3)')
    rip_parser.add_argument('-d', '--depth', type=int, default=3, help='Scan depth (default: 3)')
    rip_parser.add_argument('--no-consent', action='store_true', help='Skip consent prompt')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple endpoints')
    compare_parser.add_argument('urls', nargs='+', help='Endpoint URLs to compare')
    compare_parser.add_argument('-o', '--output', help='Output file path for comparison results')
    compare_parser.add_argument('-t', '--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')
    compare_parser.add_argument('-r', '--retries', type=int, default=3, help='Max retries (default: 3)')
    compare_parser.add_argument('-d', '--depth', type=int, default=3, help='Scan depth (default: 3)')
    compare_parser.add_argument('--no-consent', action='store_true', help='Skip consent prompt')
    
    # List formats command
    list_formats_parser = subparsers.add_parser('list-formats', help='List available export formats')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Execute command
    if args.command == 'rip':
        return rip_command(args)
    elif args.command == 'compare':
        return compare_command(args)
    elif args.command == 'list-formats':
        return list_formats_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())

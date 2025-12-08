#!/usr/bin/env python3
"""
BASE 44 Launcher - Easy Start Script
====================================

Quick launcher for BASE 44 with multiple modes:
- Interactive CLI
- REST API Server
- Batch Processing
- Demo Mode
"""

import sys
import argparse
from pathlib import Path

# Ensure base_44_core is importable
sys.path.insert(0, str(Path(__file__).parent))

from base_44_core import Base44Core, Base44Config


def run_interactive_mode(base44: Base44Core):
    """Run BASE 44 in interactive CLI mode"""
    print("\n" + "="*70)
    print("BASE 44 - Interactive Mode")
    print("="*70)
    print("\nType your requests, or 'help' for commands, 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("BASE44> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! BASE 44 remains free forever. 🚀\n")
                break
            
            if user_input.lower() == 'help':
                print_help()
                continue
            
            if user_input.lower() == 'stats':
                stats = base44.get_stats()
                print("\n📊 System Statistics:")
                for key, value in stats.items():
                    if key != "uptime_start":
                        print(f"  {key}: {value}")
                print()
                continue
            
            if user_input.lower() == 'capabilities':
                caps = base44.list_capabilities()
                print(f"\n📋 All Capabilities ({len(caps)} total, ALL FREE):\n")
                
                categories = {}
                for cap in caps:
                    cat = cap["category"]
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(cap)
                
                for category, cat_caps in sorted(categories.items()):
                    print(f"{category.upper()} ({len(cat_caps)}):")
                    for cap in cat_caps:
                        print(f"  ✅ {cap['name']}")
                print()
                continue
            
            # Process the request
            response = base44.process(user_input)
            
            print("\n" + "-"*70)
            print(response["response"])
            print("-"*70)
            print(f"Quality: {response['quality_tier']} | Free: {response['metadata']['free']}")
            if response['capabilities_used']:
                print(f"Capabilities: {', '.join(response['capabilities_used'])}")
            print()
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit properly.\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def print_help():
    """Print help information"""
    print("""
Available Commands:
  help          - Show this help message
  stats         - Show system statistics
  capabilities  - List all available capabilities
  quit          - Exit BASE 44
  
  Or just type any request to process it!
  
Examples:
  > Help me write Python code for data analysis
  > Create a video editing workflow
  > Write a book outline for a sci-fi novel
  > Design a REST API
    """)


def run_api_mode(base44: Base44Core, host: str = '0.0.0.0', port: int = 5044):
    """Run BASE 44 as REST API server"""
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
    except ImportError:
        print("\n❌ Flask and Flask-CORS required for API mode")
        print("Install with: pip install Flask Flask-CORS")
        sys.exit(1)
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    @app.route('/')
    def index():
        return jsonify({
            "name": "BASE 44 API",
            "version": base44.config.version,
            "edition": base44.config.edition,
            "status": "running",
            "free": True,
            "paid_restrictions": False,
            "endpoints": {
                "POST /api/process": "Process a request",
                "GET /api/capabilities": "List all capabilities",
                "GET /api/stats": "Get system statistics",
                "GET /api/config": "Get configuration"
            }
        })
    
    @app.route('/api/process', methods=['POST'])
    def process():
        data = request.json
        if not data or 'request' not in data:
            return jsonify({"error": "Missing 'request' field"}), 400
        
        response = base44.process(data['request'])
        return jsonify(response)
    
    @app.route('/api/capabilities', methods=['GET'])
    def capabilities():
        category = request.args.get('category')
        caps = base44.list_capabilities(category=category)
        return jsonify({
            "total": len(caps),
            "capabilities": caps,
            "all_free": True
        })
    
    @app.route('/api/stats', methods=['GET'])
    def stats():
        return jsonify(base44.get_stats())
    
    @app.route('/api/config', methods=['GET'])
    def config():
        return jsonify({
            "version": base44.config.version,
            "edition": base44.config.edition,
            "paid_restrictions": base44.config.paid_restrictions,
            "enable_all_features": base44.config.enable_all_features,
            "quality_tier": base44.config.quality_tier
        })
    
    print("\n" + "="*70)
    print("BASE 44 - API Server Mode")
    print("="*70)
    print(f"\n🚀 Server running at: http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/")
    print("\nEndpoints:")
    print(f"  POST http://{host}:{port}/api/process")
    print(f"  GET  http://{host}:{port}/api/capabilities")
    print(f"  GET  http://{host}:{port}/api/stats")
    print(f"  GET  http://{host}:{port}/api/config")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host=host, port=port, debug=False)


def run_demo_mode(base44: Base44Core):
    """Run BASE 44 in demo mode with example requests"""
    print("\n" + "="*70)
    print("BASE 44 - Demo Mode")
    print("="*70)
    print("\nProcessing example requests to showcase capabilities...\n")
    
    demos = [
        {
            "title": "Python Development",
            "request": "Create a Python function for data analysis with pandas"
        },
        {
            "title": "Video Editing",
            "request": "Edit a video with professional color grading and transitions"
        },
        {
            "title": "Book Writing",
            "request": "Help me write a science fiction novel outline"
        },
        {
            "title": "Image Processing",
            "request": "Upscale an image to 8K with AI enhancement"
        },
        {
            "title": "REST API Design",
            "request": "Design a RESTful API for an e-commerce platform"
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n{'='*70}")
        print(f"Demo {i}/{len(demos)}: {demo['title']}")
        print(f"{'='*70}")
        print(f"\nRequest: {demo['request']}\n")
        
        response = base44.process(demo['request'])
        
        print("Response:")
        print("-" * 70)
        print(response['response'])
        print("-" * 70)
        print(f"Quality: {response['quality_tier']} | Free: {response['metadata']['free']}")
        print(f"Capabilities: {', '.join(response['capabilities_used']) if response['capabilities_used'] else 'general'}")
        
        if i < len(demos):
            input("\nPress Enter for next demo...")
    
    print("\n" + "="*70)
    print("Demo completed! All features are FREE and available.")
    print("="*70)
    print()


def run_batch_mode(base44: Base44Core, input_file: str):
    """Run BASE 44 in batch mode processing requests from file"""
    print("\n" + "="*70)
    print("BASE 44 - Batch Processing Mode")
    print("="*70)
    
    try:
        with open(input_file, 'r') as f:
            requests = [line.strip() for line in f if line.strip()]
        
        print(f"\nProcessing {len(requests)} requests from {input_file}...\n")
        
        results = []
        for i, req in enumerate(requests, 1):
            print(f"\n[{i}/{len(requests)}] Processing: {req[:60]}...")
            response = base44.process(req)
            results.append({
                "request": req,
                "response": response
            })
            print(f"  ✅ Done (Quality: {response['quality_tier']}, Free: {response['metadata']['free']})")
        
        # Export results
        output_file = input_file.replace('.txt', '_results.json')
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Batch processing complete!")
        print(f"📄 Results saved to: {output_file}")
        print()
        
    except FileNotFoundError:
        print(f"\n❌ Error: File '{input_file}' not found\n")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='BASE 44 Launcher - The Free, Unrestricted AI Foundation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive mode (default)
  %(prog)s --mode interactive       # Interactive CLI
  %(prog)s --mode api               # Start REST API server
  %(prog)s --mode demo              # Run demonstration
  %(prog)s --mode batch -i file.txt # Batch process requests
  %(prog)s --api-host 0.0.0.0 --api-port 8080  # Custom API settings
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['interactive', 'api', 'demo', 'batch'],
        default='interactive',
        help='Launch mode (default: interactive)'
    )
    
    parser.add_argument(
        '--api-host',
        default='0.0.0.0',
        help='API server host (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--api-port',
        type=int,
        default=5044,
        help='API server port (default: 5044)'
    )
    
    parser.add_argument(
        '-i', '--input',
        help='Input file for batch mode'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='BASE 44 v44.0.0 - Free Forever Edition'
    )
    
    args = parser.parse_args()
    
    # Initialize BASE 44
    base44 = Base44Core()
    
    # Route to appropriate mode
    if args.mode == 'interactive':
        run_interactive_mode(base44)
    elif args.mode == 'api':
        run_api_mode(base44, host=args.api_host, port=args.api_port)
    elif args.mode == 'demo':
        run_demo_mode(base44)
    elif args.mode == 'batch':
        if not args.input:
            print("\n❌ Error: Batch mode requires --input file\n")
            parser.print_help()
            sys.exit(1)
        run_batch_mode(base44, args.input)


if __name__ == "__main__":
    main()

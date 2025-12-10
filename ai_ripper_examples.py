#!/usr/bin/env python3
"""
AI Ripper Integration Example
=============================
Example showing how to use AI Ripper with Kimi K2 and FORGE tools
"""

from ai_ripper_core import AIRipper, EndpointConfig
import json


def example_basic_ripping():
    """Basic example: Rip a single endpoint"""
    print("=" * 80)
    print("Example 1: Basic Endpoint Ripping")
    print("=" * 80)
    
    # Create ripper
    ripper = AIRipper()
    
    # Configure endpoint
    config = EndpointConfig(
        url="http://localhost:8000",
        timeout=30,
        scan_depth=3
    )
    
    # Add endpoint
    ripper.add_endpoint("my_model", config)
    
    print("\n✅ Endpoint configured")
    print(f"   URL: {config.url}")
    print(f"   Timeout: {config.timeout}s")
    print(f"   Scan Depth: {config.scan_depth}")
    
    # Note: Actual ripping would require a running endpoint
    print("\n⚠️  To run this example, start a model server at http://localhost:8000")
    print("   Example: python -m vllm.entrypoints.api_server --model gpt2")


def example_multi_endpoint_comparison():
    """Example: Compare multiple endpoints"""
    print("\n" + "=" * 80)
    print("Example 2: Multi-Endpoint Comparison")
    print("=" * 80)
    
    # Create ripper
    ripper = AIRipper()
    
    # Add multiple endpoints
    endpoints = {
        "local_gpt2": "http://localhost:8000",
        "local_llama": "http://localhost:8001",
        "cloud_api": "https://api.example.com/v1"
    }
    
    for name, url in endpoints.items():
        config = EndpointConfig(url=url, timeout=30)
        ripper.add_endpoint(name, config)
        print(f"✅ Added endpoint: {name} ({url})")
    
    print("\n📊 Ready to compare endpoints")
    print("   Use ripper.rip_multiple_endpoints() to extract and compare")


def example_export_formats():
    """Example: Export to different formats"""
    print("\n" + "=" * 80)
    print("Example 3: Export Formats")
    print("=" * 80)
    
    from ai_ripper_core import ModelMetadata
    
    # Create sample metadata
    metadata = ModelMetadata(
        name="example-model",
        endpoint_url="http://localhost:8000",
        model_type="llm",
        parameters={
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        },
        architecture="transformer",
        vocabulary_size=50257,
        context_length=2048,
        capabilities=["chat_completion", "text_generation", "embeddings"]
    )
    
    # Create ripper and add metadata
    ripper = AIRipper()
    ripper.extracted_models["example"] = metadata
    
    print("\n📦 Available export formats:")
    
    # Export to JSON
    print("\n1. JSON Export:")
    ripper.export_to_json("example", "example_model.json")
    print("   ✅ Exported to example_model.json")
    
    # Export to Python
    print("\n2. Python Export:")
    ripper.export_to_python("example", "example_model_config.py")
    print("   ✅ Exported to example_model_config.py")
    
    # Export to GGUF
    print("\n3. GGUF Export:")
    ripper.export_to_gguf("example", "example_model.gguf")
    print("   ✅ Exported to example_model.gguf")
    
    # Show JSON content
    print("\n📄 JSON Export Preview:")
    with open("example_model.json", "r") as f:
        data = json.load(f)
        print(json.dumps(data, indent=2)[:500] + "...")


def example_progress_tracking():
    """Example: Track ripping progress"""
    print("\n" + "=" * 80)
    print("Example 4: Progress Tracking")
    print("=" * 80)
    
    # Create ripper
    ripper = AIRipper()
    
    # Define progress callback
    def on_progress(progress):
        print(f"\r[{progress.progress_percentage:5.1f}%] {progress.current_task}", end="", flush=True)
        
        # Display errors and warnings
        if progress.errors:
            print(f"\n❌ Errors: {', '.join(progress.errors)}")
        if progress.warnings:
            print(f"\n⚠️  Warnings: {', '.join(progress.warnings)}")
    
    # Set callback
    ripper.set_progress_callback(on_progress)
    
    print("\n✅ Progress callback configured")
    print("   Will display real-time progress during ripping operations")


def example_kimi_integration():
    """Example: Integration with Kimi K2"""
    print("\n" + "=" * 80)
    print("Example 5: AI Ripper + Kimi K2 Integration")
    print("=" * 80)
    
    print("""
AI Ripper can be integrated with Kimi K2 for enhanced workflows:

1. Model Discovery:
   - Use AI Ripper to discover and analyze available models
   - Extract capabilities and metadata
   - Compare performance characteristics

2. Intelligent Selection:
   - Kimi K2 can use AI Ripper data to select optimal models
   - Match model capabilities to task requirements
   - Optimize for performance and cost

3. Automated Workflows:
   - Rip multiple endpoints automatically
   - Update model registry with latest metadata
   - Trigger alerts on capability changes

Example usage:
    from ai_ripper_core import AIRipper
    from kimi_forge_unified import KimiForgeUnified
    
    # Discover available models
    ripper = AIRipper()
    ripper.add_endpoint("endpoint1", config)
    ripper.rip_endpoint("endpoint1")
    
    # Use metadata with Kimi K2
    metadata = ripper.extracted_models["endpoint1"]
    
    # Kimi K2 intelligently selects based on capabilities
    system = KimiForgeUnified()
    if "chat_completion" in metadata.capabilities:
        system.use_model(metadata.name, metadata.endpoint_url)
    """)


def example_advanced_features():
    """Example: Advanced features"""
    print("\n" + "=" * 80)
    print("Example 6: Advanced Features")
    print("=" * 80)
    
    print("""
Advanced AI Ripper features:

1. Adaptive Memory Management:
   - Automatically adjusts memory usage for large models
   - Handles low-resource systems gracefully
   - Configurable memory limits

2. Security Features:
   - Ethical consent prompts
   - SSL certificate verification
   - API key encryption in memory
   - No storage of sensitive credentials

3. Performance Optimization:
   - Parallel endpoint scanning
   - Efficient metadata extraction
   - Optimized for large-scale deployments

4. Visualization:
   - Response time graphs
   - Capability comparison charts
   - Token attention heatmaps
   - Behavior classification metrics

5. Extensibility:
   - Custom export formats
   - Plugin architecture ready
   - Modular design for easy extension
    """)


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("AI RIPPER - INTEGRATION EXAMPLES")
    print("=" * 80)
    
    # Run examples
    example_basic_ripping()
    example_multi_endpoint_comparison()
    example_export_formats()
    example_progress_tracking()
    example_kimi_integration()
    example_advanced_features()
    
    print("\n" + "=" * 80)
    print("Examples Complete!")
    print("=" * 80)
    print("\nFor more information:")
    print("  - Read AI_RIPPER_README.md")
    print("  - Run 'python ai_ripper_cli.py --help'")
    print("  - Run 'python ai_ripper_gui.py' for the GUI")
    print("  - Check test_ai_ripper.py for code examples")
    print()


if __name__ == "__main__":
    main()

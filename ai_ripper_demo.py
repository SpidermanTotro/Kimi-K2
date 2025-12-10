#!/usr/bin/env python3
"""
AI Ripper - Comprehensive Demo
===============================

This script demonstrates all capabilities of the AI Ripper:
- Scanning multiple AI models
- Extracting features and patterns
- Exporting to all formats
- Generating size variants
- System optimization

Run this to see the AI Ripper in action!
"""

import os
import sys
from ai_ripper import AIRipper


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def demo_scan_multiple_ais():
    """Demo: Scan multiple AI models"""
    print_header("DEMO 1: Scanning Multiple AI Models")
    
    ripper = AIRipper()
    
    # AI models to scan
    ai_models = [
        "https://chatgpt.com",
        "https://claude.ai",
        "https://gemini.google.com"
    ]
    
    for url in ai_models:
        print(f"📡 Scanning: {url}")
        model_info = ripper.scan_ai(url)
        print(f"   ✅ Detected: {model_info.model_type}")
        print(f"   📝 Name: {model_info.name}")
        print()


def demo_full_analysis():
    """Demo: Full analysis pipeline"""
    print_header("DEMO 2: Full Analysis Pipeline")
    
    ripper = AIRipper()
    
    # Scan
    print("Step 1: Scanning...")
    model_info = ripper.scan_ai("https://chatgpt.com")
    print(f"✅ Scanned: {model_info.name}\n")
    
    # Analyze
    print("Step 2: Analyzing behaviors and extracting features...")
    patterns, features = ripper.analyze_and_extract()
    print(f"✅ Found {len(patterns)} behavior patterns")
    print(f"✅ Extracted {len(features)} features\n")
    
    # Show some patterns
    print("Sample Behavior Patterns:")
    for pattern in patterns[:2]:
        print(f"  - {pattern.pattern_type}")
        print(f"    Description: {pattern.description}")
        print(f"    Confidence: {pattern.confidence * 100}%")
        print()
    
    # Show some features
    print("Sample Features:")
    for feature in features[:3]:
        print(f"  - {feature.feature_name} ({feature.feature_type})")
        print(f"    Importance: {feature.importance * 100}%")
        print()


def demo_all_exports():
    """Demo: Export to all formats"""
    print_header("DEMO 3: Export to All Formats")
    
    ripper = AIRipper()
    
    # Full rip with all formats
    print("Executing full rip with all export formats...")
    results = ripper.full_rip(
        url="https://claude.ai",
        export_formats=["gguf", "python", "variants"]
    )
    
    print("\n✅ Full rip complete!\n")
    
    # Show exports
    print("📦 Generated Exports:")
    print(f"\n1. GGUF Format:")
    print(f"   {results['exports']['gguf']}")
    
    print(f"\n2. Python Package:")
    print(f"   {results['exports']['python']}")
    python_files = os.listdir(results['exports']['python'])
    for file in python_files:
        print(f"     - {file}")
    
    print(f"\n3. Size Variants ({len(results['exports']['variants'])} variants):")
    for variant_name, variant_path in results['exports']['variants'].items():
        size_kb = os.path.getsize(variant_path) / 1024
        print(f"   {variant_name:8s}: {size_kb:6.1f} KB")
    print()


def demo_system_optimization():
    """Demo: System resource optimization"""
    print_header("DEMO 4: System Resource Optimization")
    
    ripper = AIRipper()
    
    print("💻 Your System Resources:")
    print(f"   Total RAM:      {ripper.resources.total_ram_gb:.1f} GB")
    print(f"   Available RAM:  {ripper.resources.available_ram_gb:.1f} GB")
    print(f"   CPU Cores:      {ripper.resources.cpu_cores}")
    print(f"   GPU Available:  {'Yes ✅' if ripper.resources.gpu_available else 'No ❌'}")
    if ripper.resources.gpu_available:
        print(f"   GPU Memory:     {ripper.resources.gpu_memory_gb:.1f} GB")
    print(f"   Free Disk:      {ripper.resources.disk_space_gb:.1f} GB")
    
    print(f"\n🎯 Recommended Model Size: {ripper.optimizer.recommend_size().upper()}")
    
    print("\n📊 Size Variant Guide:")
    print("   TINY    : < 4GB RAM  (25% scale)")
    print("   SMALL   : 4-8GB RAM  (50% scale)")
    print("   MEDIUM  : 8-16GB RAM (100% scale)")
    print("   LARGE   : 16-32GB RAM (150% scale)")
    print("   XLARGE  : 32-64GB RAM (200% scale)")
    print("   HUGE    : 64GB+ RAM  (400% scale)")
    print()


def demo_custom_workflow():
    """Demo: Custom workflow"""
    print_header("DEMO 5: Custom Workflow")
    
    from ai_ripper import AIScanner, GGUFConverter, ModelSizeOptimizer, SystemResources
    
    print("Building custom workflow with individual components...\n")
    
    # Step 1: Custom scanning
    print("1. Custom Scanning:")
    scanner = AIScanner()
    model_info = scanner.scan_url("https://gemini.google.com")
    print(f"   Scanned: {model_info.name}")
    
    # Step 2: Custom analysis
    print("\n2. Custom Analysis:")
    patterns = scanner.analyze_behavior(model_info)
    features = scanner.extract_features(model_info)
    print(f"   Patterns: {len(patterns)}")
    print(f"   Features: {len(features)}")
    
    # Step 3: Custom optimization
    print("\n3. Custom Optimization:")
    resources = SystemResources.scan_system()
    optimizer = ModelSizeOptimizer(resources)
    recommended = optimizer.recommend_size()
    print(f"   Recommended: {recommended}")
    
    # Step 4: Custom export
    print("\n4. Custom GGUF Export:")
    converter = GGUFConverter()
    output_path = converter.convert_to_gguf(
        model_info,
        features,
        f"output/custom_{model_info.name}.gguf"
    )
    print(f"   Exported: {output_path}")
    print()


def demo_comparison():
    """Demo: Compare different AI models"""
    print_header("DEMO 6: AI Model Comparison")
    
    ripper = AIRipper()
    
    models = [
        ("ChatGPT", "https://chatgpt.com"),
        ("Claude", "https://claude.ai"),
        ("Gemini", "https://gemini.google.com")
    ]
    
    print("Scanning and comparing AI models...\n")
    print(f"{'Model':<15} {'Type':<15} {'Features':<10} {'Patterns':<10}")
    print("-" * 50)
    
    for name, url in models:
        ripper.scan_ai(url)
        patterns, features = ripper.analyze_and_extract()
        print(f"{name:<15} {ripper.model_info.model_type:<15} {len(features):<10} {len(patterns):<10}")
    
    print()


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("  🚀 AI RIPPER - COMPREHENSIVE DEMONSTRATION 🚀")
    print("="*70)
    print("\nThis demo will showcase all AI Ripper capabilities.")
    print("It will scan AI models, extract features, and create exports.\n")
    
    # Ask user which demos to run
    print("Available demos:")
    print("  1. Scan Multiple AI Models")
    print("  2. Full Analysis Pipeline")
    print("  3. Export to All Formats")
    print("  4. System Resource Optimization")
    print("  5. Custom Workflow")
    print("  6. AI Model Comparison")
    print("  0. Run ALL demos")
    
    try:
        choice = input("\nSelect demo (0-6): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nRunning all demos by default...\n")
        choice = "0"
    
    demos = {
        "1": ("Scan Multiple AI Models", demo_scan_multiple_ais),
        "2": ("Full Analysis Pipeline", demo_full_analysis),
        "3": ("Export to All Formats", demo_all_exports),
        "4": ("System Resource Optimization", demo_system_optimization),
        "5": ("Custom Workflow", demo_custom_workflow),
        "6": ("AI Model Comparison", demo_comparison),
    }
    
    try:
        if choice == "0":
            # Run all demos
            for name, func in demos.values():
                try:
                    func()
                except Exception as e:
                    print(f"⚠️  Demo '{name}' encountered an error: {e}")
                    import traceback
                    traceback.print_exc()
        elif choice in demos:
            name, func = demos[choice]
            func()
        else:
            print("Invalid choice. Running all demos...")
            for name, func in demos.values():
                try:
                    func()
                except Exception as e:
                    print(f"⚠️  Demo '{name}' encountered an error: {e}")
    
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        import traceback
        traceback.print_exc()
    
    print_header("🎉 DEMONSTRATION COMPLETE!")
    print("The AI Ripper is ready to use!")
    print("\nTo use the AI Ripper:")
    print("  - Interactive: python ai_ripper_cli.py")
    print("  - Quick mode:  python ai_ripper.py <url>")
    print("  - Examples:    python ai_ripper_examples.py")
    print("\nSee AI_RIPPER_README.md for complete documentation.\n")


if __name__ == "__main__":
    main()

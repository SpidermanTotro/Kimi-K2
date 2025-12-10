#!/usr/bin/env python3
"""
AI Ripper Examples
==================

Example scripts demonstrating various AI Ripper capabilities.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_ripper import AIRipper


def example_1_basic_scan():
    """Example 1: Basic AI scanning"""
    print("\n" + "="*60)
    print("Example 1: Basic AI Scanning")
    print("="*60 + "\n")
    
    ripper = AIRipper()
    
    # Scan ChatGPT
    model_info = ripper.scan_ai("https://chatgpt.com")
    
    print(f"Model Name: {model_info.name}")
    print(f"Model Type: {model_info.model_type}")
    print(f"URL: {model_info.url}")
    print(f"Architecture: {model_info.architecture}")


def example_2_feature_extraction():
    """Example 2: Feature extraction"""
    print("\n" + "="*60)
    print("Example 2: Feature Extraction")
    print("="*60 + "\n")
    
    ripper = AIRipper()
    ripper.scan_ai("https://claude.ai")
    
    patterns, features = ripper.analyze_and_extract()
    
    print(f"Behavior Patterns Found: {len(patterns)}")
    for pattern in patterns[:3]:
        print(f"  - {pattern.pattern_type}: {pattern.description}")
    
    print(f"\nFeatures Extracted: {len(features)}")
    for feature in features[:3]:
        print(f"  - {feature.feature_name} ({feature.feature_type})")


def example_3_gguf_export():
    """Example 3: Export to GGUF format"""
    print("\n" + "="*60)
    print("Example 3: GGUF Export")
    print("="*60 + "\n")
    
    ripper = AIRipper()
    ripper.scan_ai("https://gemini.google.com")
    ripper.analyze_and_extract()
    
    gguf_path = ripper.export_to_gguf()
    
    print(f"GGUF file created: {gguf_path}")
    print(f"File size: {os.path.getsize(gguf_path) / 1024:.2f} KB")


def example_4_python_export():
    """Example 4: Export to Python package"""
    print("\n" + "="*60)
    print("Example 4: Python Package Export")
    print("="*60 + "\n")
    
    ripper = AIRipper()
    ripper.scan_ai("https://chatgpt.com")
    ripper.analyze_and_extract()
    
    python_dir = ripper.export_to_python()
    
    print(f"Python package created: {python_dir}")
    
    # List files
    for file in os.listdir(python_dir):
        file_path = os.path.join(python_dir, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size} bytes)")


def example_5_size_variants():
    """Example 5: Generate size variants"""
    print("\n" + "="*60)
    print("Example 5: Size Variants Generation")
    print("="*60 + "\n")
    
    ripper = AIRipper()
    ripper.scan_ai("https://claude.ai")
    ripper.analyze_and_extract()
    
    variants = ripper.generate_size_variants()
    
    print(f"System Recommendation: {ripper.optimizer.recommend_size()}")
    print(f"\nGenerated {len(variants)} variants:")
    
    for variant_name, variant_path in variants.items():
        size_mb = os.path.getsize(variant_path) / (1024 * 1024)
        print(f"  - {variant_name}: {size_mb:.2f} MB")


def example_6_full_rip():
    """Example 6: Full ripping pipeline"""
    print("\n" + "="*60)
    print("Example 6: Full Rip Pipeline")
    print("="*60 + "\n")
    
    ripper = AIRipper()
    
    results = ripper.full_rip(
        url="https://chatgpt.com",
        export_formats=["gguf", "python", "variants"]
    )
    
    print("Full rip complete!")
    print(f"\nModel: {results['model_info']['name']}")
    print(f"Features: {len(results['features'])}")
    print(f"Patterns: {len(results['behavior_patterns'])}")
    
    print("\nExported files:")
    for format_name, path in results['exports'].items():
        if isinstance(path, dict):
            print(f"  {format_name}:")
            for variant, variant_path in path.items():
                print(f"    - {variant}: {variant_path}")
        else:
            print(f"  {format_name}: {path}")


def example_7_system_optimization():
    """Example 7: System resource optimization"""
    print("\n" + "="*60)
    print("Example 7: System Resource Optimization")
    print("="*60 + "\n")
    
    ripper = AIRipper()
    
    print("System Resources:")
    print(f"  RAM: {ripper.resources.total_ram_gb:.1f} GB total, "
          f"{ripper.resources.available_ram_gb:.1f} GB available")
    print(f"  CPU: {ripper.resources.cpu_cores} cores")
    print(f"  GPU: {'Yes' if ripper.resources.gpu_available else 'No'}")
    if ripper.resources.gpu_available:
        print(f"  GPU Memory: {ripper.resources.gpu_memory_gb:.1f} GB")
    print(f"  Disk Space: {ripper.resources.disk_space_gb:.1f} GB free")
    
    print(f"\nRecommended model size: {ripper.optimizer.recommend_size()}")


def example_8_custom_workflow():
    """Example 8: Custom workflow with manual steps"""
    print("\n" + "="*60)
    print("Example 8: Custom Workflow")
    print("="*60 + "\n")
    
    from ai_ripper import AIScanner, GGUFConverter
    
    # Manual scanning
    scanner = AIScanner()
    model_info = scanner.scan_url("https://claude.ai")
    
    # Manual analysis
    patterns = scanner.analyze_behavior(model_info)
    features = scanner.extract_features(model_info)
    
    print(f"Scanned: {model_info.name}")
    print(f"Patterns: {len(patterns)}")
    print(f"Features: {len(features)}")
    
    # Manual GGUF conversion
    converter = GGUFConverter()
    gguf_path = converter.convert_to_gguf(
        model_info,
        features,
        "output/custom_model.gguf"
    )
    
    print(f"\nCustom export: {gguf_path}")


def main():
    """Run all examples"""
    examples = [
        ("Basic Scan", example_1_basic_scan),
        ("Feature Extraction", example_2_feature_extraction),
        ("GGUF Export", example_3_gguf_export),
        ("Python Export", example_4_python_export),
        ("Size Variants", example_5_size_variants),
        ("Full Rip", example_6_full_rip),
        ("System Optimization", example_7_system_optimization),
        ("Custom Workflow", example_8_custom_workflow),
    ]
    
    print("\n" + "="*60)
    print("AI RIPPER EXAMPLES")
    print("="*60)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print("  0. Run all examples")
    
    choice = input("\nSelect example (0-8): ").strip()
    
    if choice == "0":
        # Run all examples
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\nError in {name}: {e}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        # Run selected example
        name, func = examples[int(choice) - 1]
        try:
            func()
        except Exception as e:
            print(f"\nError in {name}: {e}")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()

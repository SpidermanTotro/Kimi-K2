#!/usr/bin/env python3
"""
AI Model Explorer CLI - Command Line Interface
===============================================

Command-line interface for the AI Model Exploration system.

Usage:
    python ai_model_explorer_cli.py analyze <model_name>
    python ai_model_explorer_cli.py create-copy <model_name>
    python ai_model_explorer_cli.py compare <model1> <model2> [model3...]
    python ai_model_explorer_cli.py generate-images --count 100
    python ai_model_explorer_cli.py train-model --epochs 50
    python ai_model_explorer_cli.py full-pipeline <model_name>
"""

import argparse
import sys
import json
from pathlib import Path

from ai_model_explorer import AIModelExplorer, ModelType
from image_generation_module import ImageGenerator, OfflineModelTrainer


def analyze_command(args):
    """Analyze a model and display results"""
    print(f"\n{'='*80}")
    print(f"Analyzing Model: {args.model_name}")
    print(f"{'='*80}\n")
    
    explorer = AIModelExplorer()
    
    # Determine model type
    model_type = None
    if args.type:
        model_type = ModelType[args.type.upper().replace('-', '_')]
    
    profile = explorer.analyze_model(args.model_name, model_type)
    
    # Display results
    print(f"📊 Analysis Results for {profile.model_name}")
    print(f"{'='*80}")
    print(f"Model Type: {profile.model_type.value}")
    print(f"Version: {profile.version}")
    print(f"Description: {profile.description}\n")
    
    print(f"📝 Personality Traits ({len(profile.personality_traits)}):")
    for trait in profile.personality_traits:
        print(f"  • {trait.name}: {trait.strength:.0%}")
        print(f"    {trait.description}")
    
    print(f"\n🎯 Skills ({len(profile.skills)}):")
    for skill in profile.skills:
        print(f"  • {skill.name} ({skill.category.value}): {skill.proficiency:.0%}")
        if skill.benchmarks:
            for bench, score in skill.benchmarks.items():
                print(f"    - {bench}: {score:.1%}")
    
    print(f"\n🔍 Behavior Patterns ({len(profile.behavior_patterns)}):")
    for pattern in profile.behavior_patterns:
        print(f"  • {pattern.pattern_id}: {pattern.description}")
    
    if args.save:
        output_path = args.save
        profile.to_json(output_path)
        print(f"\n✅ Profile saved to: {output_path}")
    
    print(f"\n{'='*80}")


def create_copy_command(args):
    """Create a working copy of a model"""
    print(f"\n{'='*80}")
    print(f"Creating Working Copy: {args.model_name}")
    print(f"{'='*80}\n")
    
    explorer = AIModelExplorer()
    
    # Analyze first
    model_type = None
    if args.type:
        model_type = ModelType[args.type.upper().replace('-', '_')]
    
    print("🔍 Analyzing model...")
    profile = explorer.analyze_model(args.model_name, model_type)
    
    print(f"✅ Analysis complete")
    print(f"   Personality Traits: {len(profile.personality_traits)}")
    print(f"   Skills: {len(profile.skills)}")
    print(f"   Behavior Patterns: {len(profile.behavior_patterns)}\n")
    
    # Create working copy
    print("🔨 Creating working copy...")
    output_dir = args.output or "./working_models"
    working_dir = explorer.create_working_copy(profile, output_dir)
    
    print(f"\n✅ Working copy created successfully!")
    print(f"📁 Location: {working_dir}")
    print(f"\nGenerated files:")
    for filepath in Path(working_dir).iterdir():
        print(f"  • {filepath.name}")
    
    print(f"\n{'='*80}")


def compare_command(args):
    """Compare multiple models"""
    print(f"\n{'='*80}")
    print(f"Comparing Models: {', '.join(args.models)}")
    print(f"{'='*80}\n")
    
    explorer = AIModelExplorer()
    
    # Analyze all models
    print("🔍 Analyzing models...")
    for model_name in args.models:
        print(f"  Analyzing: {model_name}")
        explorer.analyze_model(model_name)
    
    # Compare
    print("\n📊 Comparing models...")
    comparison = explorer.compare_models(args.models)
    
    # Display comparison
    print(f"\n{'='*80}")
    print("Personality Trait Comparison")
    print(f"{'='*80}")
    for trait, scores in comparison["personality_comparison"].items():
        print(f"\n{trait}:")
        for model, score in scores.items():
            bar = "█" * int(score * 20)
            print(f"  {model:20s} [{score:5.1%}] {bar}")
    
    print(f"\n{'='*80}")
    print("Skill Comparison")
    print(f"{'='*80}")
    for skill, scores in comparison["skill_comparison"].items():
        print(f"\n{skill}:")
        for model, score in scores.items():
            bar = "█" * int(score * 20)
            print(f"  {model:20s} [{score:5.1%}] {bar}")
    
    if args.save:
        explorer.save_comparison(comparison, args.save)
        print(f"\n✅ Comparison saved to: {args.save}")
    
    print(f"\n{'='*80}")


def generate_images_command(args):
    """Generate training images"""
    print(f"\n{'='*80}")
    print(f"Generating Training Images")
    print(f"{'='*80}\n")
    
    generator = ImageGenerator(output_dir=args.output or "./generated_images")
    
    if args.dataset:
        # Create full dataset
        print(f"📊 Creating training dataset...")
        print(f"   Size: {args.count} images")
        print(f"   Categories: {len(args.categories) if args.categories else 'default'}")
        
        dataset = generator.create_training_dataset(
            size=args.count,
            categories=args.categories
        )
        
        print(f"\n✅ Dataset created!")
        print(f"   Total images: {len(dataset['images'])}")
        print(f"   Categories: {', '.join(dataset['categories'])}")
    else:
        # Generate prompts and images
        print(f"📝 Generating {args.count} training prompts...")
        prompts_text = generator.generate_training_prompts(count=args.count)
        
        print(f"✅ Generated {len(prompts_text)} prompts")
    
    # Save report
    generator.save_generation_report()
    print(f"\n📄 Generation report saved")
    
    print(f"\n{'='*80}")


def train_model_command(args):
    """Train an offline model"""
    print(f"\n{'='*80}")
    print(f"Training Offline Model: {args.model_name}")
    print(f"{'='*80}\n")
    
    # Generate training data
    print("📊 Generating training data...")
    generator = ImageGenerator()
    
    dataset = generator.create_training_dataset(
        size=args.dataset_size,
        categories=["portraits", "landscapes", "objects", "abstract"]
    )
    
    prompts = generator.generate_training_prompts(count=args.prompt_count)
    
    print(f"✅ Training data ready")
    print(f"   Images: {len(dataset['images'])}")
    print(f"   Prompts: {len(prompts)}\n")
    
    # Initialize trainer
    print("🚀 Initializing trainer...")
    trainer = OfflineModelTrainer(args.model_name)
    
    # Prepare data
    print("📊 Preparing training data...")
    training_data = trainer.prepare_training_data(dataset, prompts)
    
    # Create config
    print("⚙️ Creating training configuration...")
    config = trainer.create_training_config()
    
    # Train
    print(f"\n🏋️ Starting training for {args.epochs} epochs...\n")
    results = trainer.simulate_training(epochs=args.epochs)
    
    # Save results
    trainer.save_training_results(results)
    
    print(f"\n✅ Training complete!")
    print(f"   Final Loss: {results['final_metrics']['final_loss']:.4f}")
    print(f"   Final Accuracy: {results['final_metrics']['final_accuracy']:.2%}")
    
    print(f"\n{'='*80}")


def full_pipeline_command(args):
    """Run the complete pipeline"""
    print(f"\n{'='*80}")
    print(f"Full AI Model Exploration Pipeline")
    print(f"{'='*80}\n")
    
    model_name = args.model_name
    
    # Step 1: Analyze model
    print(f"Step 1: Analyzing {model_name}...")
    explorer = AIModelExplorer()
    profile = explorer.analyze_model(model_name)
    print(f"✅ Analysis complete\n")
    
    # Step 2: Create working copy
    print(f"Step 2: Creating working copy...")
    working_dir = explorer.create_working_copy(profile)
    print(f"✅ Working copy created at: {working_dir}\n")
    
    # Step 3: Generate training data
    print(f"Step 3: Generating training data...")
    generator = ImageGenerator()
    dataset = generator.create_training_dataset(size=args.dataset_size)
    prompts = generator.generate_training_prompts(count=args.prompt_count)
    print(f"✅ Training data ready\n")
    
    # Step 4: Train custom model
    print(f"Step 4: Training custom model...")
    trainer = OfflineModelTrainer(f"custom_{model_name}")
    training_data = trainer.prepare_training_data(dataset, prompts)
    config = trainer.create_training_config()
    results = trainer.simulate_training(epochs=args.epochs)
    print(f"✅ Training complete\n")
    
    # Step 5: Save everything
    print(f"Step 5: Saving results...")
    profile.to_json(f"{model_name}_profile.json")
    explorer.save_comparison(
        explorer.compare_models([model_name]),
        f"{model_name}_analysis.json"
    )
    trainer.save_training_results(results, f"{model_name}_training.json")
    generator.save_generation_report(f"{model_name}_generation.json")
    
    print(f"\n{'='*80}")
    print(f"✅ Full Pipeline Complete!")
    print(f"{'='*80}")
    print(f"Model Analyzed: {model_name}")
    print(f"Working Copy: {working_dir}")
    print(f"Training Samples: {len(training_data['data'])}")
    print(f"Final Accuracy: {results['final_metrics']['final_accuracy']:.2%}")
    print(f"\nGenerated files:")
    print(f"  • {model_name}_profile.json")
    print(f"  • {model_name}_analysis.json")
    print(f"  • {model_name}_training.json")
    print(f"  • {model_name}_generation.json")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="AI Model Explorer - Analyze and replicate AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a model
  %(prog)s analyze ChatGPT-4
  
  # Create working copy
  %(prog)s create-copy "Ninja AI" --type ninja_ai
  
  # Compare models
  %(prog)s compare ChatGPT-4 "Kimi K2" "Ninja AI"
  
  # Generate training dataset
  %(prog)s generate-images --count 1000 --dataset
  
  # Train model
  %(prog)s train-model my_model --epochs 100
  
  # Run full pipeline
  %(prog)s full-pipeline ChatGPT-4 --epochs 50
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze an AI model')
    analyze_parser.add_argument('model_name', help='Name of the model to analyze')
    analyze_parser.add_argument('--type', choices=['chatgpt', 'ninja_ai', 'super_ninja_ai', 'genspark_ai', 'kimi_k2'],
                               help='Model type (auto-detected if not specified)')
    analyze_parser.add_argument('--save', help='Save profile to JSON file')
    
    # Create copy command
    copy_parser = subparsers.add_parser('create-copy', help='Create a working copy of a model')
    copy_parser.add_argument('model_name', help='Name of the model')
    copy_parser.add_argument('--type', choices=['chatgpt', 'ninja_ai', 'super_ninja_ai', 'genspark_ai', 'kimi_k2'],
                            help='Model type')
    copy_parser.add_argument('--output', help='Output directory')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple models')
    compare_parser.add_argument('models', nargs='+', help='Models to compare')
    compare_parser.add_argument('--save', help='Save comparison to JSON file')
    
    # Generate images command
    images_parser = subparsers.add_parser('generate-images', help='Generate training images')
    images_parser.add_argument('--count', type=int, default=100, help='Number of images/prompts')
    images_parser.add_argument('--dataset', action='store_true', help='Create full dataset')
    images_parser.add_argument('--categories', nargs='+', help='Image categories')
    images_parser.add_argument('--output', help='Output directory')
    
    # Train model command
    train_parser = subparsers.add_parser('train-model', help='Train an offline model')
    train_parser.add_argument('model_name', help='Name for the custom model')
    train_parser.add_argument('--epochs', type=int, default=10, help='Training epochs')
    train_parser.add_argument('--dataset-size', type=int, default=1000, help='Training dataset size')
    train_parser.add_argument('--prompt-count', type=int, default=5000, help='Number of training prompts')
    
    # Full pipeline command
    pipeline_parser = subparsers.add_parser('full-pipeline', help='Run complete pipeline')
    pipeline_parser.add_argument('model_name', help='Model to analyze and replicate')
    pipeline_parser.add_argument('--epochs', type=int, default=10, help='Training epochs')
    pipeline_parser.add_argument('--dataset-size', type=int, default=500, help='Dataset size')
    pipeline_parser.add_argument('--prompt-count', type=int, default=1000, help='Prompt count')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    commands = {
        'analyze': analyze_command,
        'create-copy': create_copy_command,
        'compare': compare_command,
        'generate-images': generate_images_command,
        'train-model': train_model_command,
        'full-pipeline': full_pipeline_command,
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

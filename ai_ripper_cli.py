#!/usr/bin/env python3
"""
AI Ripper Interactive CLI
==========================

Interactive command-line interface for the AI Ripper tool.
Provides a user-friendly experience for scanning, analyzing,
and copying AI models.
"""

import os
import sys
import json
from typing import Optional
from ai_ripper import AIRipper, SystemResources


# Constants
MB_TO_BYTES = 1024 * 1024


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_banner():
    """Print ASCII art banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     █████╗ ██╗    ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗        ║
║    ██╔══██╗██║    ██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗       ║
║    ███████║██║    ██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝       ║
║    ██╔══██║██║    ██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗       ║
║    ██║  ██║██║    ██║  ██║██║██║     ██║     ███████╗██║  ██║       ║
║    ╚═╝  ╚═╝╚═╝    ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝       ║
║                                                                       ║
║              The First-Ever AI Photocopying Tool                      ║
║                  Powered by Kimi-K2 & THE FORGE                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
{Colors.END}
    """
    print(banner)


def print_system_info(resources: SystemResources):
    """Print system information"""
    print(f"\n{Colors.BOLD}💻 System Information:{Colors.END}")
    print(f"   RAM: {resources.total_ram_gb:.1f}GB total, {resources.available_ram_gb:.1f}GB available")
    print(f"   CPU: {resources.cpu_cores} cores")
    print(f"   GPU: {'✅ Available' if resources.gpu_available else '❌ Not detected'}")
    if resources.gpu_available:
        print(f"   GPU Memory: {resources.gpu_memory_gb:.1f}GB")
    print(f"   Disk Space: {resources.disk_space_gb:.1f}GB free")
    print()


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default"""
    if default:
        full_prompt = f"{Colors.YELLOW}{prompt} [{default}]: {Colors.END}"
    else:
        full_prompt = f"{Colors.YELLOW}{prompt}: {Colors.END}"
    
    user_input = input(full_prompt).strip()
    return user_input if user_input else (default or "")


def confirm(prompt: str) -> bool:
    """Ask for yes/no confirmation"""
    response = get_user_input(f"{prompt} (y/n)", "y").lower()
    return response in ['y', 'yes']


def select_export_formats() -> list:
    """Let user select export formats"""
    print(f"\n{Colors.BOLD}📦 Select export formats:{Colors.END}")
    print("   1. GGUF format (for llama.cpp, etc.)")
    print("   2. Python package (with auto-training)")
    print("   3. Size variants (tiny to huge)")
    print("   4. All formats")
    
    choice = get_user_input("Enter choice (1-4)", "4")
    
    if choice == "1":
        return ["gguf"]
    elif choice == "2":
        return ["python"]
    elif choice == "3":
        return ["variants"]
    else:
        return ["gguf", "python", "variants"]


def interactive_mode():
    """Run interactive mode"""
    print_banner()
    
    print(f"{Colors.GREEN}Welcome to AI Ripper!{Colors.END}")
    print("This tool will scan, analyze, and 'photocopy' AI models.\n")
    
    # Initialize ripper
    ripper = AIRipper()
    print_system_info(ripper.resources)
    
    # Get AI URL
    print(f"{Colors.BOLD}🔗 Enter the AI model URL to rip:{Colors.END}")
    print("   Examples:")
    print("   - https://chatgpt.com")
    print("   - https://claude.ai")
    print("   - https://gemini.google.com")
    print("   - Any custom AI endpoint")
    print()
    
    url = get_user_input("AI URL")
    
    if not url:
        print(f"{Colors.RED}Error: URL is required{Colors.END}")
        return
    
    # Select export formats
    formats = select_export_formats()
    
    # Confirm before starting
    print(f"\n{Colors.BOLD}📋 Configuration Summary:{Colors.END}")
    print(f"   URL: {url}")
    print(f"   Export formats: {', '.join(formats)}")
    print()
    
    if not confirm("Proceed with ripping?"):
        print(f"{Colors.YELLOW}Operation cancelled.{Colors.END}")
        return
    
    print()
    
    # Execute full rip
    try:
        results = ripper.full_rip(url, formats)
        
        # Display results
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ RIP COMPLETE!{Colors.END}\n")
        print(f"{Colors.BOLD}📊 Summary:{Colors.END}")
        print(f"   Model: {results['model_info']['name']}")
        print(f"   Type: {results['model_info']['model_type']}")
        print(f"   Features extracted: {len(results['features'])}")
        print(f"   Behavior patterns: {len(results['behavior_patterns'])}")
        print()
        
        print(f"{Colors.BOLD}📁 Exported files:{Colors.END}")
        for format_name, path in results['exports'].items():
            if isinstance(path, dict):
                print(f"   {format_name}:")
                for variant_name, variant_path in path.items():
                    size_mb = os.path.getsize(variant_path) / MB_TO_BYTES
                    print(f"      {variant_name}: {variant_path} ({size_mb:.2f}MB)")
            else:
                if os.path.isfile(path):
                    size_mb = os.path.getsize(path) / MB_TO_BYTES
                    print(f"   {format_name}: {path} ({size_mb:.2f}MB)")
                else:
                    print(f"   {format_name}: {path}")
        
        print()
        print(f"{Colors.GREEN}🎉 AI successfully ripped and ready to use!{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error during ripping: {e}{Colors.END}")
        import traceback
        traceback.print_exc()


def quick_mode(url: str, formats: list = None):
    """Run quick mode with minimal prompts"""
    if formats is None:
        formats = ["gguf", "python", "variants"]
    
    print_banner()
    print(f"{Colors.BOLD}🚀 Quick Mode{Colors.END}\n")
    
    ripper = AIRipper()
    
    print(f"Target: {url}")
    print(f"Formats: {', '.join(formats)}\n")
    
    try:
        results = ripper.full_rip(url, formats)
        
        print(f"\n{Colors.GREEN}✅ Success!{Colors.END}")
        print(f"Results saved to: output/{results['model_info']['name']}_rip_results.json")
        
        return results
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        return None


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Ripper CLI - Interactive interface for AI model copying",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python ai_ripper_cli.py
  
  # Quick mode
  python ai_ripper_cli.py --url https://chatgpt.com
  
  # Specific formats
  python ai_ripper_cli.py --url https://claude.ai --formats gguf python
        """
    )
    
    parser.add_argument(
        "--url",
        help="AI model URL (skips interactive mode)"
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        choices=["gguf", "python", "variants"],
        help="Export formats"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Force interactive mode"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.url and not args.interactive:
        # Quick mode
        quick_mode(args.url, args.formats)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()

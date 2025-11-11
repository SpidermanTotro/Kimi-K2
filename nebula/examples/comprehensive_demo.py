#!/usr/bin/env python3
"""
Comprehensive Demonstration of Project Nebula

This script demonstrates all components of the Nebula OS system.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nebula.kernel.kernel_module import NebulaKernel
from nebula.package_manager.npm import PackageManager


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_kernel():
    """Demonstrate kernel functionality"""
    print_header("KERNEL DEMONSTRATION")
    
    # Create and boot kernel
    kernel = NebulaKernel(total_memory=256 * 1024 * 1024)  # 256MB
    kernel.boot()
    
    # Show system info
    print("\n📊 System Information:")
    info = kernel.get_system_info()
    print(f"   Kernel Version: {info['kernel_version']}")
    print(f"   Total Memory: {info['memory']['total'] // (1024*1024)} MB")
    print(f"   Free Memory: {info['memory']['free'] // (1024*1024)} MB")
    
    # Create processes
    print("\n🚀 Creating processes...")
    for i in range(3):
        pid = kernel.create_process(f"demo_process_{i+1}", 5 * 1024 * 1024)
        print(f"   ✓ Created process {i+1} with PID {pid}")
    
    # Show memory usage
    info = kernel.get_system_info()
    print(f"\n💾 Memory Usage: {info['memory']['allocated'] // (1024*1024)} MB / {info['memory']['total'] // (1024*1024)} MB")
    
    # Schedule processes
    print("\n⚙️  Scheduling processes...")
    for i in range(3):
        proc = kernel.scheduler.schedule_next()
        if proc:
            print(f"   → Running: {proc.name}")
    
    # Shutdown
    kernel.shutdown()
    return True


def demo_package_manager():
    """Demonstrate package manager functionality"""
    print_header("PACKAGE MANAGER DEMONSTRATION")
    
    # Create package manager
    pm = PackageManager(install_dir="/tmp/nebula_demo")
    
    print("\n📦 Available packages:")
    for name, pkg in sorted(pm.repository.items()):
        print(f"   • {pkg.name} v{pkg.version} - {pkg.description}")
    
    # Install a package
    print("\n📥 Installing nebula-web (with dependencies)...")
    pm.install("nebula-web")
    
    # Show installed packages
    print("\n✅ Installed packages:")
    for pkg in pm.database.list_packages():
        print(f"   • {pkg.name} v{pkg.version} ({pkg.size // 1024} KB)")
    
    # Search for packages
    print("\n🔍 Searching for 'network'...")
    results = []
    for name, pkg in pm.repository.items():
        if 'network' in pkg.description.lower():
            results.append(pkg)
    
    for pkg in results:
        print(f"   • {pkg.name} - {pkg.description}")
    
    return True


def demo_cli_commands():
    """Demonstrate CLI commands"""
    print_header("CLI COMMANDS DEMONSTRATION")
    
    print("\n🖥️  Available built-in commands:")
    commands = [
        "help", "exit", "cd", "pwd", "ls", "cat", "mkdir", "rm", "touch",
        "echo", "env", "export", "history", "clear", "version"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"   {i:2d}. {cmd}")
    
    print("\n💡 Example usage:")
    print("   nebula> pwd           # Print working directory")
    print("   nebula> ls            # List files")
    print("   nebula> mkdir test    # Create directory")
    print("   nebula> cd test       # Change directory")
    print("   nebula> echo Hello!   # Echo text")
    print("   nebula> env           # Show environment variables")
    
    return True


def main():
    """Main demonstration"""
    print("\n" + "=" * 70)
    print("  PROJECT NEBULA - Comprehensive Demonstration")
    print("  Linux-like System for Kimi-K2")
    print("=" * 70)
    
    try:
        # Kernel demo
        print("\n[1/3] Kernel Component")
        if demo_kernel():
            print("   ✓ Kernel demonstration completed")
        
        # Package manager demo
        print("\n[2/3] Package Manager Component")
        if demo_package_manager():
            print("   ✓ Package manager demonstration completed")
        
        # CLI demo
        print("\n[3/3] CLI Component")
        if demo_cli_commands():
            print("   ✓ CLI demonstration completed")
        
        # Final summary
        print_header("SUMMARY")
        print("\n✨ Project Nebula Components:")
        print("   ✓ Kernel - Process & memory management")
        print("   ✓ Package Manager - Software installation & dependencies")
        print("   ✓ CLI Shell - Interactive command-line interface")
        
        print("\n🚀 Quick Start:")
        print("   make build          # Build all components")
        print("   make test           # Run tests")
        print("   make run-shell      # Launch the shell")
        print("   make run-kernel     # Launch the kernel")
        
        print("\n📚 Documentation:")
        print("   nebula/README.md         # Quick start guide")
        print("   nebula/docs/README.md    # Complete documentation")
        
        print("\n" + "=" * 70)
        print("  Demonstration Complete! 🎉")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

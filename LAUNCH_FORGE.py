#!/usr/bin/env python3
"""
THE FORGE - Complete Release & Launch Script
Compiles, tests, and launches THE FORGE with all features
"""

import subprocess
import sys
import os
import time

def print_banner():
    """Print THE FORGE banner"""
    banner = """
    ████████╗██╗  ██╗███████╗    ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
    ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
       ██║   ███████║█████╗      █████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
       ██║   ██╔══██║██╔══╝      ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
       ██║   ██║  ██║███████╗    ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
       ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    
    🚀 THE ULTIMATE FREE AI PROGRAMMING PLATFORM 🚀
    💰 Saves You $6,038/year vs GitHub Copilot + Codespaces + Others!
    """
    print(banner)

def run_compilation_tests():
    """Run compilation tests"""
    print("\n📋 Running Compilation Tests...")
    print("="*80)
    
    result = subprocess.run(
        ['python3', 'COMPILE_AND_TEST.py'],
        capture_output=False
    )
    
    return result.returncode == 0

def setup_remote_connections():
    """Setup remote connections"""
    print("\n🌐 Setting Up Remote Connections...")
    print("="*80)
    
    subprocess.run(['python3', 'remote_connections.py'])

def show_menu():
    """Show launch menu"""
    print("\n" + "="*80)
    print("  🎯 THE FORGE - LAUNCH MENU")
    print("="*80)
    print()
    print("  1. 🚀 Launch Full IDE (VS Code Clone + AI)")
    print("  2. 📊 Show AI Domination Dashboard (vs 22+ competitors)")
    print("  3. 🎨 Show Enhanced Session Tracker Dashboard")
    print("  4. 🔍 Detect Current Project")
    print("  5. 🌐 Setup Remote Connections")
    print("  6. 🧪 Run All Tests")
    print("  7. 📖 Show Documentation")
    print("  8. ❌ Exit")
    print()
    print("="*80)
    
    choice = input("\n👉 Enter your choice (1-8): ").strip()
    return choice

def launch_ide():
    """Launch the full IDE"""
    print("\n🚀 Launching THE FORGE IDE...")
    print("="*80)
    print()
    print("✅ Starting server on http://localhost:5000")
    print("✅ Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run(['python3', 'advanced_codespaces_server.py'])
    except KeyboardInterrupt:
        print("\n\n✅ THE FORGE IDE stopped")

def show_dashboard():
    """Show AI domination dashboard"""
    print("\n📊 AI Domination Dashboard...")
    print("="*80)
    subprocess.run(['python3', 'ai_domination_dashboard.py'])

def show_session_dashboard():
    """Show enhanced session dashboard"""
    print("\n🎨 Enhanced Session Tracker Dashboard...")
    print("="*80)
    subprocess.run(['python3', 'forge_enhanced_dashboard.py'])

def detect_project():
    """Detect current project"""
    print("\n🔍 Detecting Project...")
    print("="*80)
    subprocess.run([
        'python3', '-c',
        'from industrial_ai_detector import IndustrialProjectDetector; '
        'd=IndustrialProjectDetector("."); '
        'd.detect_everything(); '
        'd.print_comparison()'
    ])

def show_docs():
    """Show documentation"""
    print("\n📖 THE FORGE Documentation")
    print("="*80)
    print()
    print("📚 Available Documentation:")
    print()
    print("  ⭐ RUN_ME_FIRST.md               - Quick start guide (START HERE!)")
    print("  📦 COMPLETE_PACKAGE.md           - Full package inventory")
    print("  🎯 CODESPACES_README.md          - Complete features guide")
    print("  🛠️  INSTALLATION_GUIDE.md         - Setup instructions")
    print("  📊 SESSION_TRACKER_README.md     - Session tracking guide")
    print("  📈 SESSION_TRACKER_FINAL_SUMMARY.md - Session features summary")
    print("  🗺️  ROADMAP.md                    - Future development plans")
    print()
    
    doc = input("Enter filename to read (or press Enter to skip): ").strip()
    if doc and os.path.exists(doc):
        subprocess.run(['cat', doc])

def main():
    """Main function"""
    os.chdir('/home/runner/work/Kimi-K2/Kimi-K2')
    
    print_banner()
    
    # Check if this is first run
    if not os.path.exists('.forge_initialized'):
        print("\n🎉 Welcome to THE FORGE!")
        print("="*80)
        print("\nThis appears to be your first run. Let's set everything up!\n")
        
        # Run compilation tests
        if not run_compilation_tests():
            print("\n❌ Compilation tests failed!")
            print("   Please check the errors above")
            return 1
        
        # Setup remote connections
        setup_remote_connections()
        
        # Mark as initialized
        with open('.forge_initialized', 'w') as f:
            f.write('initialized')
        
        print("\n✅ THE FORGE is ready!")
        input("\nPress Enter to continue to main menu...")
    
    # Main loop
    while True:
        choice = show_menu()
        
        if choice == '1':
            launch_ide()
        elif choice == '2':
            show_dashboard()
        elif choice == '3':
            show_session_dashboard()
        elif choice == '4':
            detect_project()
        elif choice == '5':
            setup_remote_connections()
        elif choice == '6':
            run_compilation_tests()
        elif choice == '7':
            show_docs()
        elif choice == '8':
            print("\n👋 Thanks for using THE FORGE!")
            print("   🌟 Star us on GitHub!")
            print("   💰 You're saving $6,038/year!\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-8")
        
        if choice != '8':
            input("\nPress Enter to continue...")

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

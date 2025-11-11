#!/usr/bin/env python3
"""
Example: Package Manager Workflow

This example demonstrates the complete package manager workflow.
"""

import sys
from pathlib import Path

# Add nebula to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from package_manager.npm import PackageManager


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    print("=" * 60)
    print("Nebula Package Manager - Example Workflow")
    print("=" * 60)
    
    # Create package manager with a temporary directory
    pm = PackageManager(install_dir="/tmp/nebula_pm_example")
    
    # Show available packages
    print_section("Available Packages in Repository")
    pm.list_available()
    
    # Search for packages
    print_section("Searching for 'network' packages")
    pm.search("network")
    
    # Show package info
    print_section("Package Information: nebula-web")
    pm.info("nebula-web")
    
    # Install a package with dependencies
    print_section("Installing nebula-web (will install dependencies)")
    pm.install("nebula-web")
    
    # List installed packages
    print_section("Installed Packages")
    pm.list_installed()
    
    # Install another package
    print_section("Installing nebula-dev")
    pm.install("nebula-dev")
    
    # List installed packages again
    print_section("Updated Package List")
    pm.list_installed()
    
    # Try to remove a package with dependents
    print_section("Attempting to remove nebula-utils (has dependents)")
    pm.remove("nebula-utils")
    
    # Remove a package without dependents
    print_section("Removing nebula-dev (no dependents)")
    pm.remove("nebula-dev")
    
    # Final package list
    print_section("Final Package List")
    pm.list_installed()
    
    # Show info about remaining packages
    print_section("Information about installed packages")
    for pkg in pm.database.list_packages():
        print(f"\n{pkg.name} v{pkg.version}")
        print(f"  Description: {pkg.description}")
        print(f"  Dependencies: {', '.join(pkg.dependencies) if pkg.dependencies else 'None'}")
        print(f"  Size: {pkg.size // 1024}KB")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

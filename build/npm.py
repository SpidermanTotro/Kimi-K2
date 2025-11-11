#!/usr/bin/env python3
"""
Nebula Package Manager (npm - Nebula Package Manager)

A simple package management system for installing, updating, and removing packages.
"""

import os
import json
import hashlib
import shutil
from typing import Dict, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Package:
    """Package metadata"""
    name: str
    version: str
    description: str
    dependencies: List[str]
    size: int = 0
    installed_at: Optional[str] = None
    checksum: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Package':
        return cls(**data)


class PackageDatabase:
    """Package database manager"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.packages: Dict[str, Package] = {}
        self.load()
    
    def load(self) -> None:
        """Load package database from disk"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.packages = {
                        name: Package.from_dict(pkg_data)
                        for name, pkg_data in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load package database: {e}")
    
    def save(self) -> None:
        """Save package database to disk"""
        try:
            with open(self.db_path, 'w') as f:
                data = {
                    name: pkg.to_dict()
                    for name, pkg in self.packages.items()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error: Could not save package database: {e}")
    
    def add_package(self, package: Package) -> None:
        """Add a package to the database"""
        self.packages[package.name] = package
        self.save()
    
    def remove_package(self, name: str) -> bool:
        """Remove a package from the database"""
        if name in self.packages:
            del self.packages[name]
            self.save()
            return True
        return False
    
    def get_package(self, name: str) -> Optional[Package]:
        """Get a package by name"""
        return self.packages.get(name)
    
    def list_packages(self) -> List[Package]:
        """List all installed packages"""
        return list(self.packages.values())


class PackageManager:
    """Main package manager"""
    
    def __init__(self, install_dir: str = "/usr/local/nebula"):
        self.install_dir = Path(install_dir)
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.install_dir / "var" / "lib" / "npm" / "packages.json"
        self.cache_dir = self.install_dir / "var" / "cache" / "npm"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.database = PackageDatabase(str(self.db_path))
        
        # Available packages (in a real system, this would come from a repository)
        self.repository = self._create_sample_repository()
    
    def _create_sample_repository(self) -> Dict[str, Package]:
        """Create a sample package repository"""
        return {
            "nebula-utils": Package(
                name="nebula-utils",
                version="1.0.0",
                description="Essential utilities for Nebula OS",
                dependencies=[],
                size=1024 * 100  # 100KB
            ),
            "nebula-net": Package(
                name="nebula-net",
                version="1.2.0",
                description="Network utilities and tools",
                dependencies=["nebula-utils"],
                size=1024 * 500  # 500KB
            ),
            "nebula-dev": Package(
                name="nebula-dev",
                version="2.0.0",
                description="Development tools and libraries",
                dependencies=["nebula-utils"],
                size=1024 * 1024 * 5  # 5MB
            ),
            "nebula-web": Package(
                name="nebula-web",
                version="0.9.0",
                description="Web server and related tools",
                dependencies=["nebula-utils", "nebula-net"],
                size=1024 * 1024 * 2  # 2MB
            ),
        }
    
    def install(self, package_name: str, force: bool = False) -> bool:
        """Install a package"""
        # Check if already installed
        if self.database.get_package(package_name) and not force:
            print(f"Package '{package_name}' is already installed.")
            print("Use --force to reinstall.")
            return False
        
        # Check if package exists in repository
        if package_name not in self.repository:
            print(f"Error: Package '{package_name}' not found in repository.")
            return False
        
        package = self.repository[package_name]
        
        # Resolve and install dependencies
        print(f"Resolving dependencies for {package_name}...")
        if not self._install_dependencies(package):
            return False
        
        # Install the package
        print(f"Installing {package_name} v{package.version}...")
        
        # Simulate installation
        package.installed_at = datetime.now().isoformat()
        package.checksum = self._calculate_checksum(package)
        
        # Add to database
        self.database.add_package(package)
        
        print(f"Successfully installed {package_name} v{package.version}")
        return True
    
    def _install_dependencies(self, package: Package) -> bool:
        """Install package dependencies"""
        for dep_name in package.dependencies:
            if not self.database.get_package(dep_name):
                print(f"  Installing dependency: {dep_name}")
                if not self.install(dep_name):
                    print(f"Error: Failed to install dependency '{dep_name}'")
                    return False
        return True
    
    def _calculate_checksum(self, package: Package) -> str:
        """Calculate package checksum"""
        data = f"{package.name}{package.version}{package.size}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def remove(self, package_name: str, force: bool = False) -> bool:
        """Remove a package"""
        # Check if installed
        package = self.database.get_package(package_name)
        if not package:
            print(f"Package '{package_name}' is not installed.")
            return False
        
        # Check for dependencies
        if not force:
            dependents = self._find_dependents(package_name)
            if dependents:
                print(f"Error: Cannot remove '{package_name}' - required by:")
                for dep in dependents:
                    print(f"  - {dep}")
                print("Use --force to remove anyway.")
                return False
        
        # Remove the package
        print(f"Removing {package_name}...")
        self.database.remove_package(package_name)
        print(f"Successfully removed {package_name}")
        return True
    
    def _find_dependents(self, package_name: str) -> List[str]:
        """Find packages that depend on the given package"""
        dependents = []
        for pkg in self.database.list_packages():
            if package_name in pkg.dependencies:
                dependents.append(pkg.name)
        return dependents
    
    def update(self, package_name: Optional[str] = None) -> bool:
        """Update package(s)"""
        if package_name:
            return self._update_package(package_name)
        else:
            return self._update_all()
    
    def _update_package(self, package_name: str) -> bool:
        """Update a specific package"""
        installed = self.database.get_package(package_name)
        if not installed:
            print(f"Package '{package_name}' is not installed.")
            return False
        
        available = self.repository.get(package_name)
        if not available:
            print(f"Package '{package_name}' not found in repository.")
            return False
        
        if installed.version == available.version:
            print(f"{package_name} is already at the latest version ({installed.version})")
            return True
        
        print(f"Updating {package_name} from v{installed.version} to v{available.version}...")
        return self.install(package_name, force=True)
    
    def _update_all(self) -> bool:
        """Update all installed packages"""
        packages = self.database.list_packages()
        if not packages:
            print("No packages installed.")
            return True
        
        print(f"Updating {len(packages)} package(s)...")
        success = True
        for pkg in packages:
            if not self._update_package(pkg.name):
                success = False
        
        return success
    
    def list_installed(self) -> None:
        """List all installed packages"""
        packages = self.database.list_packages()
        
        if not packages:
            print("No packages installed.")
            return
        
        print(f"\n{'Package':<20} {'Version':<10} {'Size':<10} {'Installed':<20}")
        print("-" * 70)
        
        for pkg in sorted(packages, key=lambda p: p.name):
            size_str = self._format_size(pkg.size)
            installed_str = pkg.installed_at[:19] if pkg.installed_at else "N/A"
            print(f"{pkg.name:<20} {pkg.version:<10} {size_str:<10} {installed_str:<20}")
        
        total_size = sum(pkg.size for pkg in packages)
        print("-" * 70)
        print(f"Total: {len(packages)} package(s), {self._format_size(total_size)}")
    
    def list_available(self) -> None:
        """List all available packages in repository"""
        print(f"\n{'Package':<20} {'Version':<10} {'Size':<10} {'Description':<40}")
        print("-" * 85)
        
        for name, pkg in sorted(self.repository.items()):
            size_str = self._format_size(pkg.size)
            desc = pkg.description[:37] + "..." if len(pkg.description) > 40 else pkg.description
            installed = " [installed]" if self.database.get_package(name) else ""
            print(f"{pkg.name:<20} {pkg.version:<10} {size_str:<10} {desc:<40}{installed}")
    
    def search(self, query: str) -> None:
        """Search for packages"""
        results = []
        query_lower = query.lower()
        
        for name, pkg in self.repository.items():
            if query_lower in name.lower() or query_lower in pkg.description.lower():
                results.append(pkg)
        
        if not results:
            print(f"No packages found matching '{query}'")
            return
        
        print(f"\nFound {len(results)} package(s) matching '{query}':")
        print(f"\n{'Package':<20} {'Version':<10} {'Description':<50}")
        print("-" * 85)
        
        for pkg in sorted(results, key=lambda p: p.name):
            desc = pkg.description[:47] + "..." if len(pkg.description) > 50 else pkg.description
            print(f"{pkg.name:<20} {pkg.version:<10} {desc:<50}")
    
    def info(self, package_name: str) -> None:
        """Show package information"""
        # Check installed packages
        installed = self.database.get_package(package_name)
        # Check repository
        available = self.repository.get(package_name)
        
        if not installed and not available:
            print(f"Package '{package_name}' not found.")
            return
        
        pkg = installed or available
        
        print(f"\nPackage: {pkg.name}")
        print(f"Version: {pkg.version}")
        print(f"Description: {pkg.description}")
        print(f"Size: {self._format_size(pkg.size)}")
        print(f"Dependencies: {', '.join(pkg.dependencies) if pkg.dependencies else 'None'}")
        
        if installed:
            print(f"Status: Installed")
            print(f"Installed at: {installed.installed_at}")
            print(f"Checksum: {installed.checksum}")
        else:
            print(f"Status: Available (not installed)")
    
    def _format_size(self, size: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"


def main():
    """CLI interface for package manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nebula Package Manager")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package', help='Package name')
    install_parser.add_argument('--force', action='store_true', help='Force reinstall')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a package')
    remove_parser.add_argument('package', help='Package name')
    remove_parser.add_argument('--force', action='store_true', help='Force removal')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update package(s)')
    update_parser.add_argument('package', nargs='?', help='Package name (optional, updates all if not specified)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List installed packages')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for packages')
    search_parser.add_argument('query', help='Search query')
    
    # Available command
    available_parser = subparsers.add_parser('available', help='List available packages')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show package information')
    info_parser.add_argument('package', help='Package name')
    
    args = parser.parse_args()
    
    # Create package manager
    pm = PackageManager()
    
    # Execute command
    if args.command == 'install':
        pm.install(args.package, force=args.force)
    elif args.command == 'remove':
        pm.remove(args.package, force=args.force)
    elif args.command == 'update':
        pm.update(args.package)
    elif args.command == 'list':
        pm.list_installed()
    elif args.command == 'search':
        pm.search(args.query)
    elif args.command == 'available':
        pm.list_available()
    elif args.command == 'info':
        pm.info(args.package)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

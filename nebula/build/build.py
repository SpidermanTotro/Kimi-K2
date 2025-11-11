#!/usr/bin/env python3
"""
Nebula Build System

Build and manage Nebula OS components.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional


class BuildSystem:
    """Main build system class"""
    
    def __init__(self, source_dir: str = None):
        self.source_dir = Path(source_dir or os.getcwd())
        self.build_dir = self.source_dir / "build"
        self.dist_dir = self.source_dir / "dist"
        self.nebula_dir = self.source_dir / "nebula"
        
        self.components = {
            "kernel": self.nebula_dir / "kernel" / "kernel_module.py",
            "shell": self.nebula_dir / "cli" / "shell.py",
            "package_manager": self.nebula_dir / "package_manager" / "npm.py",
        }
    
    def clean(self) -> bool:
        """Clean build artifacts"""
        print("Cleaning build artifacts...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                print(f"  Removing {dir_path}")
                shutil.rmtree(dir_path)
        
        # Clean __pycache__ directories
        for pycache in self.source_dir.rglob("__pycache__"):
            shutil.rmtree(pycache)
        
        print("Clean complete.")
        return True
    
    def build(self) -> bool:
        """Build all components"""
        print("Building Nebula OS components...")
        
        # Create build directory
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify all components exist
        missing = []
        for name, path in self.components.items():
            if not path.exists():
                missing.append(f"{name}: {path}")
        
        if missing:
            print("Error: Missing components:")
            for m in missing:
                print(f"  - {m}")
            return False
        
        # Copy components to build directory
        for name, src_path in self.components.items():
            dest_path = self.build_dir / src_path.name
            print(f"  Building {name}...")
            shutil.copy2(src_path, dest_path)
            # Make executable
            os.chmod(dest_path, 0o755)
        
        print("Build complete.")
        return True
    
    def install(self, prefix: str = "/usr/local") -> bool:
        """Install built components"""
        print(f"Installing Nebula OS to {prefix}...")
        
        prefix_path = Path(prefix)
        bin_dir = prefix_path / "bin"
        lib_dir = prefix_path / "lib" / "nebula"
        
        # Create directories
        bin_dir.mkdir(parents=True, exist_ok=True)
        lib_dir.mkdir(parents=True, exist_ok=True)
        
        # Install executables
        executables = {
            "nebula-kernel": self.build_dir / "kernel_module.py",
            "nebula-shell": self.build_dir / "shell.py",
            "nebula-pkg": self.build_dir / "npm.py",
        }
        
        for name, src in executables.items():
            if src.exists():
                dest = bin_dir / name
                print(f"  Installing {name} to {dest}")
                shutil.copy2(src, dest)
                os.chmod(dest, 0o755)
        
        print("Installation complete.")
        return True
    
    def test(self) -> bool:
        """Run tests"""
        print("Running tests...")
        
        # Check if components can be imported
        test_passed = True
        
        for name, path in self.components.items():
            print(f"  Testing {name}...")
            try:
                # Try to run syntax check
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(path)],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"    FAILED: {result.stderr}")
                    test_passed = False
                else:
                    print(f"    PASSED")
            except Exception as e:
                print(f"    FAILED: {e}")
                test_passed = False
        
        if test_passed:
            print("\nAll tests passed!")
        else:
            print("\nSome tests failed.")
        
        return test_passed
    
    def package(self) -> bool:
        """Create distribution package"""
        print("Creating distribution package...")
        
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tar.gz archive
        archive_name = f"nebula-os-0.1.0"
        archive_path = self.dist_dir / archive_name
        
        print(f"  Creating archive {archive_path}.tar.gz...")
        
        # Copy files to staging directory
        staging_dir = self.build_dir / archive_name
        staging_dir.mkdir(parents=True, exist_ok=True)
        
        for name, src_path in self.components.items():
            dest_path = staging_dir / src_path.name
            shutil.copy2(src_path, dest_path)
        
        # Create README
        readme_content = """Nebula OS v0.1.0
================

A Linux-like operating system with kernel, shell, and package manager.

Installation:
  sudo python3 build.py install

Components:
  - nebula-kernel: Kernel module
  - nebula-shell: Command-line shell
  - nebula-pkg: Package manager

For more information, visit the documentation.
"""
        (staging_dir / "README.txt").write_text(readme_content)
        
        # Create tarball
        shutil.make_archive(str(archive_path), 'gztar', self.build_dir, archive_name)
        
        print(f"Package created: {archive_path}.tar.gz")
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nebula Build System")
    parser.add_argument('action', 
                       choices=['clean', 'build', 'test', 'install', 'package', 'all'],
                       help='Build action to perform')
    parser.add_argument('--prefix', 
                       default='/usr/local',
                       help='Installation prefix (default: /usr/local)')
    
    args = parser.parse_args()
    
    builder = BuildSystem()
    
    success = True
    
    if args.action == 'clean':
        success = builder.clean()
    elif args.action == 'build':
        success = builder.build()
    elif args.action == 'test':
        success = builder.test()
    elif args.action == 'install':
        if not builder.build():
            sys.exit(1)
        success = builder.install(args.prefix)
    elif args.action == 'package':
        if not builder.build():
            sys.exit(1)
        success = builder.package()
    elif args.action == 'all':
        success = (builder.clean() and 
                  builder.build() and 
                  builder.test() and 
                  builder.package())
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

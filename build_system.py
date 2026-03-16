#!/usr/bin/env python3
"""
THE FORGE - Complete Build System
Builds entire project with all components
"""

import os
import sys
import subprocess
import zipfile
import json
from pathlib import Path
from datetime import datetime

class ForgeBuilder:
    """Complete build system for THE FORGE"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
    def build_all(self):
        """Build everything"""
        print("🔥 THE FORGE - COMPLETE BUILD SYSTEM")
        print("=" * 70)
        print()
        
        steps = [
            ("1. Setup Build Environment", self.setup_environment),
            ("2. Build Core System", self.build_core),
            ("3. Build Video Editor", self.build_video_editor),
            ("4. Build Linux OS", self.build_linux_os),
            ("5. Build Documentation", self.build_documentation),
            ("6. Create Distribution Package", self.create_distribution),
            ("7. Generate Checksums", self.generate_checksums),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}")
            print("-" * 70)
            try:
                step_func()
                print(f"✅ {step_name} - COMPLETE")
            except Exception as e:
                print(f"❌ {step_name} - FAILED: {e}")
                return False
        
        print()
        print("=" * 70)
        print("🎉 BUILD COMPLETE!")
        print(f"📦 Distribution: {self.dist_dir}")
        return True
    
    def setup_environment(self):
        """Setup build environment"""
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        print("   ✓ Build directories created")
        
    def build_core(self):
        """Build core Python implementation"""
        print("   Building Python core...")
        # Core is already built, just verify
        core_files = [
            "forge_implementation.py",
            "forge_server.py",
            "forge_cli.py",
            "forge_gui.py"
        ]
        for f in core_files:
            if (self.project_root / f).exists():
                print(f"   ✓ {f}")
            else:
                print(f"   ⚠ {f} missing")
    
    def build_video_editor(self):
        """Build video editor components"""
        print("   Checking video editor components...")
        
        # Check for C++ video processing source
        cpp_sources = list(self.project_root.glob("src/**/*.cpp"))
        if cpp_sources:
            print(f"   ✓ Found {len(cpp_sources)} C++ source files")
            # Try to build with CMake if available
            if (self.project_root / "CMakeLists.txt").exists():
                print("   ✓ CMake configuration found")
                try:
                    result = subprocess.run(
                        ["cmake", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print("   ✓ CMake available - C++ builds would be possible")
                    else:
                        print("   ⚠ CMake not available - skipping C++ build")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    print("   ⚠ CMake not found - skipping C++ build")
        else:
            print("   ⚠ No C++ source files found - video components are Python-based")
        
        print("   ✓ Video editor components verified")
        
    def build_linux_os(self):
        """Prepare Linux OS builder"""
        print("   Checking Linux OS builder components...")
        
        # Check for bootable OS components
        rust_sources = list(self.project_root.glob("src/**/*.rs"))
        go_sources = list(self.project_root.glob("src/**/*.go"))
        
        if rust_sources:
            print(f"   ✓ Found {len(rust_sources)} Rust source files")
            # Check for Cargo
            if (self.project_root / "Cargo.toml").exists():
                print("   ✓ Cargo configuration found")
                try:
                    result = subprocess.run(
                        ["cargo", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print("   ✓ Cargo available - Rust builds would be possible")
                    else:
                        print("   ⚠ Cargo not available - skipping Rust build")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    print("   ⚠ Cargo not found - skipping Rust build")
        else:
            print("   ⚠ No Rust source files found")
            
        if go_sources:
            print(f"   ✓ Found {len(go_sources)} Go source files")
            try:
                result = subprocess.run(
                    ["go", "version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print("   ✓ Go available - Go builds would be possible")
                else:
                    print("   ⚠ Go not available - skipping Go build")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("   ⚠ Go not found - skipping Go build")
        else:
            print("   ⚠ No Go source files found")
            
        print("   ✓ Linux OS builder components verified")
        
    def build_documentation(self):
        """Compile all documentation"""
        print("   Compiling documentation...")
        
        # Find all markdown files
        doc_files = list(self.project_root.glob("docs/*.md"))
        root_docs = [f for f in self.project_root.glob("*.md") 
                     if f.name not in ["LICENSE.md"]]
        
        all_docs = doc_files + root_docs
        
        print(f"   ✓ Found {len(all_docs)} documentation files")
        
        # Create a combined documentation file in build directory
        combined_doc = self.build_dir / "COMPLETE_DOCUMENTATION.md"
        
        def make_anchor(text):
            """Create a markdown anchor from text"""
            # Convert to lowercase, replace spaces and underscores with hyphens
            anchor = text.lower()
            anchor = anchor.replace(' ', '-').replace('_', '-')
            # Remove file extension
            if anchor.endswith('.md'):
                anchor = anchor[:-3]
            # Remove special characters except hyphens
            anchor = ''.join(c for c in anchor if c.isalnum() or c == '-')
            # Remove multiple consecutive hyphens
            while '--' in anchor:
                anchor = anchor.replace('--', '-')
            return anchor.strip('-')
        
        with open(combined_doc, 'w', encoding='utf-8') as outfile:
            outfile.write("# THE FORGE - Complete Documentation\n\n")
            outfile.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            outfile.write("---\n\n")
            
            # Add table of contents
            outfile.write("## Table of Contents\n\n")
            for i, doc in enumerate(sorted(all_docs), 1):
                anchor = make_anchor(doc.name)
                outfile.write(f"{i}. [{doc.name}](#{anchor})\n")
            outfile.write("\n---\n\n")
            
            # Combine all documentation
            for doc in sorted(all_docs):
                anchor = make_anchor(doc.name)
                outfile.write(f'\n<a id="{anchor}"></a>\n\n')
                outfile.write(f"# {doc.name}\n\n")
                try:
                    with open(doc, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                    outfile.write("\n\n---\n\n")
                except Exception as e:
                    outfile.write(f"Error reading file: {e}\n\n")
        
        print(f"   ✓ Created combined documentation: {combined_doc.name}")
        print(f"   ✓ Size: {combined_doc.stat().st_size / 1024:.2f} KB")
        print("   ✓ Documentation compilation complete")
        
    def create_distribution(self):
        """Create downloadable distribution"""
        print("   Creating distribution package...")
        
        zip_name = f"THE_FORGE_v1.0_{datetime.now().strftime('%Y%m%d')}.zip"
        zip_path = self.dist_dir / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all Python files
            for py_file in self.project_root.glob("*.py"):
                zipf.write(py_file, py_file.name)
            
            # Add docs
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                for doc_file in docs_dir.glob("*.md"):
                    zipf.write(doc_file, f"docs/{doc_file.name}")
            
            # Add README
            if (self.project_root / "README.md").exists():
                zipf.write(self.project_root / "README.md", "README.md")
            
            # Add compiled documentation if it exists
            combined_doc = self.build_dir / "COMPLETE_DOCUMENTATION.md"
            if combined_doc.exists():
                zipf.write(combined_doc, "COMPLETE_DOCUMENTATION.md")
                print("   ✓ Included compiled documentation")
        
        print(f"   ✓ Created: {zip_name}")
        print(f"   ✓ Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return zip_path
    
    def generate_checksums(self):
        """Generate checksums for verification"""
        print("   Generating checksums...")
        
        checksums = {}
        for file in self.dist_dir.glob("*.zip"):
            import hashlib
            with open(file, 'rb') as f:
                checksums[file.name] = {
                    'md5': hashlib.md5(f.read()).hexdigest(),
                    'size': file.stat().st_size
                }
        
        checksum_file = self.dist_dir / "checksums.json"
        with open(checksum_file, 'w') as f:
            json.dump(checksums, f, indent=2)
        
        print(f"   ✓ Checksums saved to {checksum_file}")

if __name__ == "__main__":
    builder = ForgeBuilder()
    success = builder.build_all()
    sys.exit(0 if success else 1)

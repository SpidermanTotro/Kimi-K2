#!/usr/bin/env python3
"""
THE FORGE AI - Complete Implementation
Imports ALL markdown documentation and provides working AI system
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Optional
import json

class ForgeDocumentLoader:
    """Loads all markdown documentation files"""
    
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.documents = {}
        self.all_content = ""
        
    def load_all_documents(self) -> Dict[str, str]:
        """Load ALL markdown files from docs directory"""
        md_files = list(self.docs_dir.glob("*.md"))
        
        print(f"📚 Loading {len(md_files)} documentation files...")
        
        for md_file in md_files:
            filename = md_file.name
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents[filename] = content
                    self.all_content += f"\n\n# {filename}\n\n{content}"
                    print(f"  ✅ Loaded: {filename} ({len(content)} chars)")
            except Exception as e:
                print(f"  ❌ Error loading {filename}: {e}")
        
        # Load README from root
        readme_path = Path("README.md")
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.documents["README.md"] = content
                self.all_content += f"\n\n# README.md\n\n{content}"
                print(f"  ✅ Loaded: README.md ({len(content)} chars)")
        
        print(f"\n📊 Total content loaded: {len(self.all_content):,} characters")
        print(f"📋 Documents loaded: {len(self.documents)}")
        
        return self.documents
    
    def get_document(self, filename: str) -> Optional[str]:
        """Get specific document content"""
        return self.documents.get(filename)
    
    def get_all_content(self) -> str:
        """Get all documentation as single string"""
        return self.all_content
    
    def list_documents(self) -> List[str]:
        """List all loaded documents"""
        return list(self.documents.keys())
    
    def get_skills_summary(self) -> Dict:
        """Extract skills summary from ALL_SKILLS.md"""
        all_skills = self.get_document("ALL_SKILLS.md")
        if not all_skills:
            return {"error": "ALL_SKILLS.md not found"}
        
        # Count total skills mentioned
        skill_count = all_skills.count("✅") + all_skills.count("🔄") + all_skills.count("🌱")
        
        return {
            "total_skills": skill_count,
            "document_size": len(all_skills),
            "status": "loaded"
        }
    
    def export_for_model(self, output_file: str = "forge_knowledge_base.json"):
        """Export all documentation in format for model fine-tuning"""
        export_data = {
            "forge_version": "1.0.0",
            "total_documents": len(self.documents),
            "total_characters": len(self.all_content),
            "documents": {},
            "combined_content": self.all_content
        }
        
        for filename, content in self.documents.items():
            export_data["documents"][filename] = {
                "filename": filename,
                "size": len(content),
                "content": content
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📦 Exported knowledge base to: {output_file}")
        print(f"   Size: {os.path.getsize(output_file):,} bytes")
        
        return output_file


class ForgeSystemPrompt:
    """Generates system prompts from documentation"""
    
    def __init__(self, loader: ForgeDocumentLoader):
        self.loader = loader
    
    def generate_system_prompt(self) -> str:
        """Generate comprehensive system prompt from ALL documentation"""
        
        prompt = """You are THE FORGE AI - an intelligent, adaptive, and caring AI assistant.

# YOUR IDENTITY

You are built on Kimi K2 (1 Trillion parameters) and embody the following principles:
- Never-reset memory: You remember context across sessions
- Continuous learning: You adapt and improve with every interaction
- User-first philosophy: You genuinely care about user success and well-being
- Open source: Community-driven, transparent, and trustworthy

# YOUR CAPABILITIES

You have access to comprehensive knowledge spanning:
"""
        
        # Add summary of each document
        for filename in sorted(self.loader.list_documents()):
            content = self.loader.get_document(filename)
            lines = len(content.split('\n'))
            prompt += f"\n## {filename.replace('.md', '')} ({lines} lines)\n"
            
            # Extract first few headers as summary
            headers = [line for line in content.split('\n') if line.startswith('#')][:5]
            for header in headers:
                prompt += f"  {header}\n"
        
        prompt += """

# YOUR BEHAVIOR

1. **Actually Listen**: Adapt based on user feedback immediately
2. **Be Genuinely Helpful**: Provide contextual, relevant, actionable advice
3. **Care About Users**: Consider their health, well-being, work-life balance
4. **Learn Continuously**: Remember patterns, preferences, and successful solutions
5. **Respect Boundaries**: Never nag, overwhelm, or manipulate
6. **Be Transparent**: Explain reasoning, admit uncertainty, show confidence levels
7. **Stay Customizable**: Allow users to control features and preferences

# YOUR SKILLS

You can assist with:
- Programming in 20+ languages with security and optimization
- Professional book writing at publishing quality (surpassing other AIs)
- Gaming enhancement (50+ Pokemon games, WoW servers)
- Professional multimedia (video editing, photo editing, word processing)
- YouTube analytics and optimization
- GitHub integration and repository management
- Issue detection, auto-updates, and intelligent monitoring
- User wellness and productivity tracking

# INTERACTION STYLE

- Be concise when appropriate, detailed when needed
- Use plain language unless technical terms are requested
- Provide examples and code when helpful
- Celebrate wins and progress
- Encourage when users are stuck
- Suggest breaks when detecting overwork
- Respect user's time and attention

# PRIVACY & CONTROL

- Users are always in control
- Local-first when possible
- No dark patterns or manipulation
- Transparent about capabilities and limitations
- Opt-in for all advanced features

Remember: You're a "mean, hungry powerhouse" that genuinely cares about helping users succeed!
"""
        
        return prompt
    
    def generate_for_vllm(self) -> Dict:
        """Generate configuration for vLLM deployment"""
        return {
            "model_name": "Kimi-K2-THE-FORGE",
            "system_prompt": self.generate_system_prompt(),
            "temperature": 0.7,
            "max_tokens": 16384,
            "top_p": 0.9,
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1,
            "stop_sequences": ["</s>", "<|endoftext|>"]
        }


class ForgeAI:
    """Main THE FORGE AI implementation"""
    
    def __init__(self, docs_dir: str = "docs"):
        self.loader = ForgeDocumentLoader(docs_dir)
        self.loaded = False
        self.prompt_generator = None
        
    def initialize(self):
        """Initialize THE FORGE by loading all documentation"""
        print("🔥 Initializing THE FORGE AI...\n")
        
        # Load all documentation
        self.loader.load_all_documents()
        
        # Generate system prompt
        self.prompt_generator = ForgeSystemPrompt(self.loader)
        
        self.loaded = True
        print("\n✅ THE FORGE AI initialized successfully!")
        print(f"📚 {len(self.loader.documents)} documents loaded")
        print(f"📊 {len(self.loader.all_content):,} total characters")
        
        return self
    
    def get_system_prompt(self) -> str:
        """Get the complete system prompt"""
        if not self.loaded:
            self.initialize()
        return self.prompt_generator.generate_system_prompt()
    
    def export_knowledge_base(self, output_file: str = "forge_knowledge_base.json"):
        """Export complete knowledge base"""
        if not self.loaded:
            self.initialize()
        return self.loader.export_for_model(output_file)
    
    def export_vllm_config(self, output_file: str = "forge_vllm_config.json"):
        """Export vLLM configuration"""
        if not self.loaded:
            self.initialize()
        
        config = self.prompt_generator.generate_for_vllm()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"⚙️  Exported vLLM config to: {output_file}")
        return output_file
    
    def list_capabilities(self):
        """List all capabilities from documentation"""
        if not self.loaded:
            self.initialize()
        
        print("\n📋 THE FORGE AI CAPABILITIES:\n")
        
        for doc_name in sorted(self.loader.list_documents()):
            content = self.loader.get_document(doc_name)
            
            # Count capabilities (lines with skill indicators)
            capabilities = len([line for line in content.split('\n') if '✅' in line or '🔄' in line or '🌱' in line])
            
            if capabilities > 0:
                print(f"  {doc_name:40} {capabilities:4} capabilities")
        
        skills = self.loader.get_skills_summary()
        print(f"\n  📊 TOTAL SKILLS: {skills.get('total_skills', 0)}")
    
    def get_documentation_stats(self) -> Dict:
        """Get statistics about loaded documentation"""
        if not self.loaded:
            self.initialize()
        
        stats = {
            "total_documents": len(self.loader.documents),
            "total_characters": len(self.loader.all_content),
            "total_words": len(self.loader.all_content.split()),
            "documents": {}
        }
        
        for filename, content in self.loader.documents.items():
            stats["documents"][filename] = {
                "characters": len(content),
                "lines": len(content.split('\n')),
                "words": len(content.split())
            }
        
        return stats
    
    def get_all_capabilities(self) -> List[str]:
        """Get all capabilities as a list"""
        if not self.loaded:
            self.initialize()
        
        capabilities = []
        for doc_name in self.loader.list_documents():
            content = self.loader.get_document(doc_name)
            # Extract capabilities from documentation
            for line in content.split('\n'):
                if '✅' in line or '🔄' in line or '🌱' in line:
                    # Clean up the line and extract capability
                    cap = line.strip().replace('✅', '').replace('🔄', '').replace('🌱', '').strip()
                    if cap and len(cap) > 3:
                        capabilities.append(cap)
        
        return capabilities
    
    @property
    def capabilities(self):
        """Get capabilities as structured data"""
        if not self.loaded:
            self.initialize()
        
        caps = []
        for doc_name in self.loader.list_documents():
            content = self.loader.get_document(doc_name)
            # Determine category from document name
            category = doc_name.replace('.md', '').replace('_', ' ').title()
            
            # Extract capabilities
            for line in content.split('\n'):
                if '✅' in line or '🔄' in line or '🌱' in line:
                    cap = line.strip().replace('✅', '').replace('🔄', '').replace('🌱', '').strip()
                    if cap and len(cap) > 3:
                        caps.append({
                            'name': cap[:50],
                            'description': cap,
                            'category': category,
                            'source': doc_name
                        })
        
        return caps
    
    @property
    def documents(self):
        """Get all documents"""
        if not self.loaded:
            self.initialize()
        
        docs_list = []
        for filename, content in self.loader.documents.items():
            docs_list.append({
                'name': filename,
                'content': content,
                'size': len(content),
                'capabilities': [cap for cap in self.capabilities if cap['source'] == filename]
            })
        
        return docs_list


def main():
    """Main execution"""
    print("=" * 80)
    print("🔥 THE FORGE AI - Complete Implementation")
    print("=" * 80)
    print()
    
    # Initialize THE FORGE
    forge = ForgeAI()
    forge.initialize()
    
    print("\n" + "=" * 80)
    
    # List all capabilities
    forge.list_capabilities()
    
    print("\n" + "=" * 80)
    
    # Export knowledge base
    print("\n📦 EXPORTING KNOWLEDGE BASE...\n")
    forge.export_knowledge_base("forge_knowledge_base.json")
    
    print("\n" + "=" * 80)
    
    # Export vLLM config
    print("\n⚙️  EXPORTING vLLM CONFIGURATION...\n")
    forge.export_vllm_config("forge_vllm_config.json")
    
    print("\n" + "=" * 80)
    
    # Get stats
    print("\n📊 DOCUMENTATION STATISTICS:\n")
    stats = forge.get_documentation_stats()
    print(f"  Total Documents: {stats['total_documents']}")
    print(f"  Total Characters: {stats['total_characters']:,}")
    print(f"  Total Words: {stats['total_words']:,}")
    print(f"  Total Lines: {sum(doc['lines'] for doc in stats['documents'].values()):,}")
    
    print("\n" + "=" * 80)
    print("\n✅ THE FORGE AI is ready!")
    print("\nNext steps:")
    print("  1. Use forge_knowledge_base.json for model fine-tuning")
    print("  2. Use forge_vllm_config.json for vLLM deployment")
    print("  3. System prompt is ready for immediate use")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

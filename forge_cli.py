#!/usr/bin/env python3
"""
THE FORGE AI - Command Line Interface
Interactive CLI for using THE FORGE AI
"""

import sys
import os
from typing import List, Dict
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from forge_implementation import ForgeAI


class ForgeCLI:
    """Command-line interface for THE FORGE AI"""
    
    def __init__(self):
        self.forge = None
        self.session_history: List[Dict] = []
        self.current_mode = 'chat'
        
    def initialize(self):
        """Initialize THE FORGE"""
        print("🔥 Initializing THE FORGE AI...")
        print()
        
        self.forge = ForgeAI()
        self.forge.initialize()
        
        print()
        print("✅ THE FORGE AI is ready!")
        print()
        
    def print_welcome(self):
        """Print welcome message"""
        print("=" * 70)
        print("🔥 THE FORGE AI - Interactive CLI")
        print("=" * 70)
        print()
        print("Available commands:")
        print("  /help      - Show this help message")
        print("  /stats     - Show system statistics")
        print("  /caps      - List all capabilities")
        print("  /mode      - Change mode (chat, code, book, video)")
        print("  /history   - Show conversation history")
        print("  /clear     - Clear conversation history")
        print("  /exit      - Exit THE FORGE")
        print()
        print("=" * 70)
        print()
        
    def run(self):
        """Main CLI loop"""
        self.initialize()
        self.print_welcome()
        
        while True:
            try:
                # Get user input
                prompt = f"[{self.current_mode}] You: "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if not self.handle_command(user_input):
                        break  # Exit requested
                    continue
                
                # Process message
                self.process_message(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
    def handle_command(self, command: str) -> bool:
        """
        Handle CLI commands
        Returns False if exit requested, True otherwise
        """
        cmd = command.lower().split()[0]
        
        if cmd == '/exit' or cmd == '/quit':
            print("👋 Goodbye!")
            return False
            
        elif cmd == '/help':
            self.print_welcome()
            
        elif cmd == '/stats':
            self.show_stats()
            
        elif cmd == '/caps':
            self.show_capabilities()
            
        elif cmd == '/mode':
            self.change_mode(command)
            
        elif cmd == '/history':
            self.show_history()
            
        elif cmd == '/clear':
            self.session_history.clear()
            print("✅ Conversation history cleared")
            print()
            
        else:
            print(f"❌ Unknown command: {cmd}")
            print("Type /help for available commands")
            print()
            
        return True
        
    def process_message(self, message: str):
        """Process a user message"""
        # Add to history
        self.session_history.append({
            'role': 'user',
            'content': message
        })
        
        # Generate response based on mode
        response = self.generate_response(message)
        
        # Add response to history
        self.session_history.append({
            'role': 'assistant',
            'content': response
        })
        
        # Print response
        print()
        print(f"THE FORGE: {response}")
        print()
        
    def generate_response(self, message: str) -> str:
        """Generate a response based on the current mode"""
        if self.current_mode == 'chat':
            return self.generate_chat_response(message)
        elif self.current_mode == 'code':
            return self.generate_code_response(message)
        elif self.current_mode == 'book':
            return self.generate_book_response(message)
        elif self.current_mode == 'video':
            return self.generate_video_response(message)
        else:
            return "Mode not recognized. Use /mode to select a valid mode."
            
    def generate_chat_response(self, message: str) -> str:
        """Generate general chat response"""
        response = f"Processing: {message}\n\n"
        response += "This is THE FORGE AI in action. In production, this would:\n"
        response += "- Use the Kimi K3 model with 1T parameters\n"
        response += "- Apply the complete system prompt from all 15 documentation files\n"
        response += "- Utilize 865+ capabilities as needed\n"
        response += "- Learn from your interaction patterns\n"
        response += "- Provide context-aware, intelligent responses\n"
        return response
        
    def generate_code_response(self, message: str) -> str:
        """Generate code-focused response"""
        return ("Code mode active. I can help you with:\n"
                "- Writing code in 20+ languages\n"
                "- Code review and optimization\n"
                "- Debugging and error fixing\n"
                "- Architecture suggestions\n"
                "- Security scanning\n"
                "- Performance profiling\n\n"
                f"Your request: {message}")
        
    def generate_book_response(self, message: str) -> str:
        """Generate book writing response"""
        return ("Book writing mode active. I can help you with:\n"
                "- Writing in 50+ genres\n"
                "- Sequel detection and series planning\n"
                "- Character development and plot structure\n"
                "- Publishing preparation (EPUB, MOBI, PDF)\n"
                "- Marketing materials and book descriptions\n"
                "- Quality upscaling from draft to professional\n\n"
                f"Your request: {message}")
        
    def generate_video_response(self, message: str) -> str:
        """Generate video editing response"""
        return ("Video editing mode active. I can help you with:\n"
                "- Professional video editing guidance\n"
                "- Color grading and effects\n"
                "- Audio mixing and sync\n"
                "- Export settings for different platforms\n"
                "- YouTube optimization\n"
                "- Thumbnail and metadata suggestions\n\n"
                f"Your request: {message}")
        
    def show_stats(self):
        """Show system statistics"""
        print()
        print("=" * 70)
        print("📊 THE FORGE AI Statistics")
        print("=" * 70)
        print()
        
        if hasattr(self.forge, 'documents'):
            print(f"Documentation files loaded: {len(self.forge.documents)}")
            print(f"Total capabilities: {len(self.forge.get_all_capabilities())}")
        else:
            print(f"Total capabilities: {len(self.forge.get_all_capabilities())}")
        
        print(f"Messages in session: {len(self.session_history)}")
        print(f"Current mode: {self.current_mode}")
        print()
        
        # Show documentation breakdown
        if hasattr(self.forge, 'documents'):
            print("📚 Loaded Documentation:")
            for doc in self.forge.documents:
                size_kb = len(doc['content']) / 1024
                print(f"  ✅ {doc['filename']: <35} {size_kb:>8.1f} KB")
            print()
        
    def show_capabilities(self):
        """Show all capabilities"""
        capabilities = self.forge.get_all_capabilities()
        
        print()
        print("=" * 70)
        print(f"🎯 THE FORGE AI Capabilities ({len(capabilities)} total)")
        print("=" * 70)
        print()
        
        for cap in capabilities[:20]:  # Show first 20
            print(f"  ✅ {cap}")
        
        if len(capabilities) > 20:
            print(f"  ... and {len(capabilities) - 20} more")
        print()
        
    def change_mode(self, command: str):
        """Change interaction mode"""
        parts = command.split()
        
        if len(parts) < 2:
            print()
            print("Available modes:")
            print("  chat   - General conversation")
            print("  code   - Code generation and review")
            print("  book   - Book writing and publishing")
            print("  video  - Video editing guidance")
            print()
            print(f"Current mode: {self.current_mode}")
            print()
            print("Usage: /mode <mode_name>")
            print()
            return
            
        new_mode = parts[1].lower()
        
        if new_mode in ['chat', 'code', 'book', 'video']:
            self.current_mode = new_mode
            print(f"✅ Mode changed to: {new_mode}")
            print()
        else:
            print(f"❌ Invalid mode: {new_mode}")
            print()
            
    def show_history(self):
        """Show conversation history"""
        if not self.session_history:
            print()
            print("📝 No conversation history yet")
            print()
            return
            
        print()
        print("=" * 70)
        print("📝 Conversation History")
        print("=" * 70)
        print()
        
        for i, msg in enumerate(self.session_history, 1):
            role = msg['role'].capitalize()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"{i}. [{role}] {content}")
        
        print()


def main():
    """Main entry point"""
    cli = ForgeCLI()
    cli.run()


if __name__ == '__main__':
    main()

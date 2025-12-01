#!/usr/bin/env python3
"""
ChatGPT Export Parser
Extracts all text, conversations, and data from ChatGPT export files
Supports JSON, HTML, and ZIP formats
"""

import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from html.parser import HTMLParser

class ChatGPTExportParser:
    """
    Comprehensive parser for ChatGPT export files
    Handles conversations.json, HTML exports, and ZIP archives
    """
    
    def __init__(self, export_path: str):
        """
        Initialize parser with export file path
        
        Args:
            export_path: Path to ChatGPT export file (JSON, HTML, or ZIP)
        """
        self.export_path = Path(export_path)
        self.conversations = []
        self.metadata = {}
        self.extracted_text = []
        
        if not self.export_path.exists():
            raise FileNotFoundError(f"Export file not found: {export_path}")
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the export file and extract all data
        
        Returns:
            Dict containing parsed conversations and metadata
        """
        print(f"🔍 Parsing ChatGPT export: {self.export_path.name}")
        
        # Determine file type and parse accordingly
        if self.export_path.suffix == '.zip':
            return self._parse_zip()
        elif self.export_path.suffix == '.json':
            return self._parse_json()
        elif self.export_path.suffix in ['.html', '.htm']:
            return self._parse_html()
        else:
            raise ValueError(f"Unsupported file format: {self.export_path.suffix}")
    
    def _parse_zip(self) -> Dict[str, Any]:
        """Parse ZIP archive containing ChatGPT export"""
        print("📦 Extracting ZIP archive...")
        
        with zipfile.ZipFile(self.export_path, 'r') as zip_ref:
            # List all files
            file_list = zip_ref.namelist()
            print(f"   Found {len(file_list)} files in archive")
            
            # Look for conversations.json
            conversations_file = None
            for file in file_list:
                if 'conversations.json' in file.lower():
                    conversations_file = file
                    break
            
            if conversations_file:
                print(f"   ✓ Found conversations file: {conversations_file}")
                with zip_ref.open(conversations_file) as f:
                    data = json.load(f)
                    return self._process_json_data(data)
            else:
                # Try to find any JSON files
                json_files = [f for f in file_list if f.endswith('.json')]
                if json_files:
                    print(f"   ✓ Found {len(json_files)} JSON files")
                    all_data = []
                    for json_file in json_files:
                        with zip_ref.open(json_file) as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                all_data.extend(data)
                            else:
                                all_data.append(data)
                    return self._process_json_data(all_data)
                else:
                    raise ValueError("No conversations.json found in ZIP archive")
    
    def _parse_json(self) -> Dict[str, Any]:
        """Parse JSON export file"""
        print("📄 Parsing JSON file...")
        
        with open(self.export_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self._process_json_data(data)
    
    def _parse_html(self) -> Dict[str, Any]:
        """Parse HTML export file"""
        print("🌐 Parsing HTML file...")
        
        with open(self.export_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract conversations from HTML
        parser = ChatGPTHTMLParser()
        parser.feed(html_content)
        
        return {
            'conversations': parser.conversations,
            'total_conversations': len(parser.conversations),
            'total_messages': sum(len(c.get('messages', [])) for c in parser.conversations),
            'extracted_text': parser.extracted_text
        }
    
    def _process_json_data(self, data: Any) -> Dict[str, Any]:
        """Process JSON data and extract conversations"""
        print("⚙️  Processing conversations...")
        
        if isinstance(data, list):
            conversations = data
        elif isinstance(data, dict):
            # Handle different JSON structures
            if 'conversations' in data:
                conversations = data['conversations']
            elif 'items' in data:
                conversations = data['items']
            else:
                conversations = [data]
        else:
            conversations = []
        
        # Process each conversation
        processed_conversations = []
        total_messages = 0
        
        for conv in conversations:
            processed_conv = self._process_conversation(conv)
            if processed_conv:
                processed_conversations.append(processed_conv)
                total_messages += len(processed_conv.get('messages', []))
        
        print(f"   ✓ Processed {len(processed_conversations)} conversations")
        print(f"   ✓ Total messages: {total_messages}")
        
        return {
            'conversations': processed_conversations,
            'total_conversations': len(processed_conversations),
            'total_messages': total_messages,
            'export_date': datetime.now().isoformat()
        }
    
    def _process_conversation(self, conv: Dict) -> Optional[Dict]:
        """Process a single conversation"""
        try:
            # Extract conversation metadata
            conversation = {
                'id': conv.get('id', conv.get('conversation_id', 'unknown')),
                'title': conv.get('title', 'Untitled'),
                'create_time': conv.get('create_time', conv.get('created_at')),
                'update_time': conv.get('update_time', conv.get('updated_at')),
                'messages': []
            }
            
            # Extract messages
            mapping = conv.get('mapping', {})
            if mapping:
                # Process message mapping
                for msg_id, msg_data in mapping.items():
                    message = msg_data.get('message')
                    if message and message.get('content'):
                        processed_msg = self._process_message(message)
                        if processed_msg:
                            conversation['messages'].append(processed_msg)
            else:
                # Try direct messages array
                messages = conv.get('messages', [])
                for msg in messages:
                    processed_msg = self._process_message(msg)
                    if processed_msg:
                        conversation['messages'].append(processed_msg)
            
            return conversation if conversation['messages'] else None
            
        except Exception as e:
            print(f"   ⚠️  Error processing conversation: {e}")
            return None
    
    def _process_message(self, message: Dict) -> Optional[Dict]:
        """Process a single message"""
        try:
            content = message.get('content', {})
            
            # Handle different content structures
            if isinstance(content, dict):
                parts = content.get('parts', [])
                text = ' '.join(str(part) for part in parts if part)
            elif isinstance(content, str):
                text = content
            else:
                text = str(content)
            
            if not text or text.strip() == '':
                return None
            
            return {
                'role': message.get('author', {}).get('role', message.get('role', 'unknown')),
                'text': text,
                'create_time': message.get('create_time'),
                'metadata': message.get('metadata', {})
            }
            
        except Exception as e:
            print(f"   ⚠️  Error processing message: {e}")
            return None
    
    def extract_all_text(self) -> str:
        """Extract all text from conversations"""
        result = self.parse()
        all_text = []
        
        for conv in result['conversations']:
            all_text.append(f"\n{'='*80}\n")
            all_text.append(f"CONVERSATION: {conv['title']}\n")
            all_text.append(f"{'='*80}\n\n")
            
            for msg in conv['messages']:
                role = msg['role'].upper()
                text = msg['text']
                all_text.append(f"[{role}]\n{text}\n\n")
        
        return ''.join(all_text)
    
    def export_to_markdown(self, output_path: str):
        """Export conversations to Markdown format"""
        result = self.parse()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# ChatGPT Conversations Export\n\n")
            f.write(f"**Total Conversations:** {result['total_conversations']}\n")
            f.write(f"**Total Messages:** {result['total_messages']}\n")
            f.write(f"**Export Date:** {result.get('export_date', 'Unknown')}\n\n")
            f.write(f"---\n\n")
            
            for i, conv in enumerate(result['conversations'], 1):
                f.write(f"## {i}. {conv['title']}\n\n")
                f.write(f"**ID:** `{conv['id']}`\n")
                if conv.get('create_time'):
                    f.write(f"**Created:** {conv['create_time']}\n")
                f.write(f"**Messages:** {len(conv['messages'])}\n\n")
                
                for msg in conv['messages']:
                    role = msg['role'].upper()
                    text = msg['text']
                    f.write(f"### {role}\n\n")
                    f.write(f"{text}\n\n")
                
                f.write(f"---\n\n")
        
        print(f"✅ Exported to Markdown: {output_path}")
    
    def export_to_json(self, output_path: str):
        """Export parsed data to JSON"""
        result = self.parse()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported to JSON: {output_path}")
    
    def export_to_text(self, output_path: str):
        """Export all text to plain text file"""
        text = self.extract_all_text()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✅ Exported to text: {output_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the export"""
        result = self.parse()
        
        stats = {
            'total_conversations': result['total_conversations'],
            'total_messages': result['total_messages'],
            'conversations_by_month': {},
            'messages_by_role': {'user': 0, 'assistant': 0, 'system': 0, 'other': 0},
            'average_messages_per_conversation': 0,
            'total_characters': 0,
            'total_words': 0
        }
        
        for conv in result['conversations']:
            # Count messages by role
            for msg in conv['messages']:
                role = msg['role'].lower()
                if role in stats['messages_by_role']:
                    stats['messages_by_role'][role] += 1
                else:
                    stats['messages_by_role']['other'] += 1
                
                # Count characters and words
                text = msg['text']
                stats['total_characters'] += len(text)
                stats['total_words'] += len(text.split())
        
        if stats['total_conversations'] > 0:
            stats['average_messages_per_conversation'] = stats['total_messages'] / stats['total_conversations']
        
        return stats


class ChatGPTHTMLParser(HTMLParser):
    """Parser for HTML exports"""
    
    def __init__(self):
        super().__init__()
        self.conversations = []
        self.extracted_text = []
        self.current_text = []
    
    def handle_data(self, data):
        if data.strip():
            self.current_text.append(data.strip())
            self.extracted_text.append(data.strip())


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ChatGPT Export Parser - Extract all text and conversations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse and display statistics
  python chatgpt_parser.py export.zip
  
  # Export to Markdown
  python chatgpt_parser.py export.zip --markdown output.md
  
  # Export to JSON
  python chatgpt_parser.py export.json --json output.json
  
  # Export all text
  python chatgpt_parser.py export.zip --text all_text.txt
  
  # Export all formats
  python chatgpt_parser.py export.zip --all output_prefix
        """
    )
    
    parser.add_argument('export_file', help='ChatGPT export file (ZIP, JSON, or HTML)')
    parser.add_argument('--markdown', '-m', help='Export to Markdown file')
    parser.add_argument('--json', '-j', help='Export to JSON file')
    parser.add_argument('--text', '-t', help='Export to text file')
    parser.add_argument('--all', '-a', help='Export to all formats with prefix')
    parser.add_argument('--stats', '-s', action='store_true', help='Show statistics only')
    
    args = parser.parse_args()
    
    try:
        # Initialize parser
        chatgpt_parser = ChatGPTExportParser(args.export_file)
        
        # Export to all formats if requested
        if args.all:
            print(f"\n📦 Exporting to all formats with prefix: {args.all}\n")
            chatgpt_parser.export_to_markdown(f"{args.all}.md")
            chatgpt_parser.export_to_json(f"{args.all}.json")
            chatgpt_parser.export_to_text(f"{args.all}.txt")
        else:
            # Export to specific formats
            if args.markdown:
                chatgpt_parser.export_to_markdown(args.markdown)
            
            if args.json:
                chatgpt_parser.export_to_json(args.json)
            
            if args.text:
                chatgpt_parser.export_to_text(args.text)
        
        # Show statistics
        if args.stats or not (args.markdown or args.json or args.text or args.all):
            print("\n📊 Statistics:\n")
            stats = chatgpt_parser.get_statistics()
            print(f"   Total Conversations: {stats['total_conversations']}")
            print(f"   Total Messages: {stats['total_messages']}")
            print(f"   Average Messages/Conversation: {stats['average_messages_per_conversation']:.1f}")
            print(f"\n   Messages by Role:")
            for role, count in stats['messages_by_role'].items():
                if count > 0:
                    print(f"      {role.capitalize()}: {count}")
            print(f"\n   Total Characters: {stats['total_characters']:,}")
            print(f"   Total Words: {stats['total_words']:,}")
        
        print("\n✅ Done!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
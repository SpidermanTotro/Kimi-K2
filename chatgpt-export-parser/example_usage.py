#!/usr/bin/env python3
"""
ChatGPT Export Parser - Example Usage
Demonstrates various ways to use the parser
"""

from chatgpt_parser import ChatGPTExportParser
from pathlib import Path

def example_1_basic_parsing():
    """Example 1: Basic parsing and statistics"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Parsing")
    print("=" * 80)
    
    # Initialize parser
    parser = ChatGPTExportParser('your_export.zip')
    
    # Parse the file
    result = parser.parse()
    
    # Display basic info
    print(f"\nTotal Conversations: {result['total_conversations']}")
    print(f"Total Messages: {result['total_messages']}")
    
    # Get statistics
    stats = parser.get_statistics()
    print(f"\nStatistics:")
    print(f"  Average Messages/Conversation: {stats['average_messages_per_conversation']:.1f}")
    print(f"  Total Words: {stats['total_words']:,}")
    print(f"  Total Characters: {stats['total_characters']:,}")


def example_2_export_formats():
    """Example 2: Export to different formats"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Export to Different Formats")
    print("=" * 80)
    
    parser = ChatGPTExportParser('your_export.zip')
    
    # Export to Markdown
    parser.export_to_markdown('conversations.md')
    print("\n✓ Exported to Markdown: conversations.md")
    
    # Export to JSON
    parser.export_to_json('conversations.json')
    print("✓ Exported to JSON: conversations.json")
    
    # Export to Text
    parser.export_to_text('conversations.txt')
    print("✓ Exported to Text: conversations.txt")


def example_3_extract_specific_conversations():
    """Example 3: Extract specific conversations"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Extract Specific Conversations")
    print("=" * 80)
    
    parser = ChatGPTExportParser('your_export.zip')
    result = parser.parse()
    
    # Find conversations about Python
    python_conversations = []
    for conv in result['conversations']:
        if 'python' in conv['title'].lower():
            python_conversations.append(conv)
    
    print(f"\nFound {len(python_conversations)} conversations about Python:")
    for conv in python_conversations[:5]:  # Show first 5
        print(f"  • {conv['title']}")


def example_4_analyze_usage_patterns():
    """Example 4: Analyze usage patterns"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Analyze Usage Patterns")
    print("=" * 80)
    
    parser = ChatGPTExportParser('your_export.zip')
    result = parser.parse()
    stats = parser.get_statistics()
    
    # Analyze message distribution
    print("\nMessage Distribution:")
    for role, count in stats['messages_by_role'].items():
        if count > 0:
            percentage = (count / stats['total_messages']) * 100
            print(f"  {role.capitalize()}: {count} ({percentage:.1f}%)")
    
    # Find longest conversations
    conversations_by_length = sorted(
        result['conversations'],
        key=lambda c: len(c['messages']),
        reverse=True
    )
    
    print("\nTop 5 Longest Conversations:")
    for i, conv in enumerate(conversations_by_length[:5], 1):
        print(f"  {i}. {conv['title']} ({len(conv['messages'])} messages)")


def example_5_search_conversations():
    """Example 5: Search through conversations"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Search Conversations")
    print("=" * 80)
    
    parser = ChatGPTExportParser('your_export.zip')
    result = parser.parse()
    
    # Search for specific keywords
    search_term = "machine learning"
    matches = []
    
    for conv in result['conversations']:
        for msg in conv['messages']:
            if search_term.lower() in msg['text'].lower():
                matches.append({
                    'conversation': conv['title'],
                    'role': msg['role'],
                    'text': msg['text'][:200] + '...'  # First 200 chars
                })
    
    print(f"\nFound {len(matches)} messages containing '{search_term}':")
    for match in matches[:3]:  # Show first 3
        print(f"\n  Conversation: {match['conversation']}")
        print(f"  Role: {match['role']}")
        print(f"  Text: {match['text']}")


def example_6_batch_processing():
    """Example 6: Batch process multiple exports"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Batch Processing")
    print("=" * 80)
    
    # Process multiple export files
    export_files = [
        'export_2024_01.zip',
        'export_2024_02.zip',
        'export_2024_03.zip'
    ]
    
    total_conversations = 0
    total_messages = 0
    
    for export_file in export_files:
        if Path(export_file).exists():
            parser = ChatGPTExportParser(export_file)
            result = parser.parse()
            
            total_conversations += result['total_conversations']
            total_messages += result['total_messages']
            
            print(f"\n{export_file}:")
            print(f"  Conversations: {result['total_conversations']}")
            print(f"  Messages: {result['total_messages']}")
    
    print(f"\nTotal across all exports:")
    print(f"  Conversations: {total_conversations}")
    print(f"  Messages: {total_messages}")


def example_7_custom_filtering():
    """Example 7: Custom filtering and processing"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Custom Filtering")
    print("=" * 80)
    
    parser = ChatGPTExportParser('your_export.zip')
    result = parser.parse()
    
    # Filter conversations by date
    from datetime import datetime
    
    recent_conversations = []
    cutoff_date = datetime(2024, 1, 1).timestamp()
    
    for conv in result['conversations']:
        if conv.get('create_time') and conv['create_time'] > cutoff_date:
            recent_conversations.append(conv)
    
    print(f"\nConversations since 2024:")
    print(f"  Total: {len(recent_conversations)}")
    
    # Filter by message count
    long_conversations = [
        conv for conv in result['conversations']
        if len(conv['messages']) > 20
    ]
    
    print(f"\nConversations with >20 messages:")
    print(f"  Total: {len(long_conversations)}")


def example_8_export_subset():
    """Example 8: Export subset of conversations"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Export Subset")
    print("=" * 80)
    
    parser = ChatGPTExportParser('your_export.zip')
    result = parser.parse()
    
    # Get only coding-related conversations
    coding_keywords = ['python', 'javascript', 'code', 'programming', 'function']
    coding_conversations = []
    
    for conv in result['conversations']:
        title_lower = conv['title'].lower()
        if any(keyword in title_lower for keyword in coding_keywords):
            coding_conversations.append(conv)
    
    # Create custom export
    custom_result = {
        'conversations': coding_conversations,
        'total_conversations': len(coding_conversations),
        'total_messages': sum(len(c['messages']) for c in coding_conversations),
        'filter': 'Coding-related conversations'
    }
    
    # Export filtered results
    import json
    with open('coding_conversations.json', 'w') as f:
        json.dump(custom_result, f, indent=2)
    
    print(f"\nExported {len(coding_conversations)} coding conversations")
    print("  Output: coding_conversations.json")


def main():
    """Run all examples"""
    print("\n🔍 ChatGPT Export Parser - Example Usage\n")
    
    examples = [
        ("Basic Parsing", example_1_basic_parsing),
        ("Export Formats", example_2_export_formats),
        ("Extract Specific", example_3_extract_specific_conversations),
        ("Analyze Patterns", example_4_analyze_usage_patterns),
        ("Search", example_5_search_conversations),
        ("Batch Processing", example_6_batch_processing),
        ("Custom Filtering", example_7_custom_filtering),
        ("Export Subset", example_8_export_subset),
    ]
    
    print("Available Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nNote: Update 'your_export.zip' with your actual export file path")
    print("\nTo run an example, uncomment the function call below:")
    
    # Uncomment to run examples:
    # example_1_basic_parsing()
    # example_2_export_formats()
    # example_3_extract_specific_conversations()
    # example_4_analyze_usage_patterns()
    # example_5_search_conversations()
    # example_6_batch_processing()
    # example_7_custom_filtering()
    # example_8_export_subset()


if __name__ == '__main__':
    main()
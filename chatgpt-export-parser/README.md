# 🔍 ChatGPT Export Parser

**Extract all text, conversations, and data from ChatGPT export files**

Supports JSON, HTML, and ZIP formats from ChatGPT data exports.

---

## 🚀 Features

- ✅ Parse ChatGPT export files (ZIP, JSON, HTML)
- ✅ Extract all conversations and messages
- ✅ Export to multiple formats (Markdown, JSON, Text)
- ✅ Get detailed statistics
- ✅ Handle all ChatGPT export structures
- ✅ Clean, formatted output
- ✅ Command-line interface

---

## 📦 Installation

### Requirements
- Python 3.7+
- No external dependencies (uses only standard library)

### Quick Start
```bash
# Make executable
chmod +x chatgpt_parser.py

# Run directly
./chatgpt_parser.py your_export.zip
```

---

## 🎯 Usage

### Basic Usage

**Parse and show statistics:**
```bash
python chatgpt_parser.py conversations.json
```

**Export to Markdown:**
```bash
python chatgpt_parser.py export.zip --markdown output.md
```

**Export to JSON:**
```bash
python chatgpt_parser.py export.zip --json output.json
```

**Export to plain text:**
```bash
python chatgpt_parser.py export.zip --text all_conversations.txt
```

**Export to all formats:**
```bash
python chatgpt_parser.py export.zip --all my_export
# Creates: my_export.md, my_export.json, my_export.txt
```

**Show statistics only:**
```bash
python chatgpt_parser.py export.zip --stats
```

---

## 📋 Supported Export Formats

### 1. ZIP Archives
ChatGPT's standard export format containing `conversations.json`

```bash
python chatgpt_parser.py chatgpt_export.zip --all output
```

### 2. JSON Files
Direct `conversations.json` file

```bash
python chatgpt_parser.py conversations.json --markdown output.md
```

### 3. HTML Files
HTML exports from ChatGPT

```bash
python chatgpt_parser.py export.html --text output.txt
```

---

## 📊 Output Formats

### Markdown Format
Clean, readable format with headers and formatting:

```markdown
# ChatGPT Conversations Export

**Total Conversations:** 50
**Total Messages:** 500

---

## 1. How to learn Python

**ID:** `abc123`
**Created:** 2024-01-01
**Messages:** 10

### USER

How do I learn Python?

### ASSISTANT

Here's a comprehensive guide...
```

### JSON Format
Structured data for programmatic access:

```json
{
  "conversations": [
    {
      "id": "abc123",
      "title": "How to learn Python",
      "messages": [
        {
          "role": "user",
          "text": "How do I learn Python?",
          "create_time": "2024-01-01T10:00:00"
        }
      ]
    }
  ],
  "total_conversations": 50,
  "total_messages": 500
}
```

### Text Format
Plain text with all conversations:

```
================================================================================
CONVERSATION: How to learn Python
================================================================================

[USER]
How do I learn Python?

[ASSISTANT]
Here's a comprehensive guide...
```

---

## 📈 Statistics

The parser provides detailed statistics:

- **Total Conversations** - Number of conversation threads
- **Total Messages** - Total messages across all conversations
- **Average Messages/Conversation** - Average length of conversations
- **Messages by Role** - Breakdown by user/assistant/system
- **Total Characters** - Total character count
- **Total Words** - Total word count

Example output:
```
📊 Statistics:

   Total Conversations: 50
   Total Messages: 500
   Average Messages/Conversation: 10.0

   Messages by Role:
      User: 250
      Assistant: 248
      System: 2

   Total Characters: 125,000
   Total Words: 25,000
```

---

## 🔧 Advanced Usage

### Python API

Use the parser in your own Python code:

```python
from chatgpt_parser import ChatGPTExportParser

# Initialize parser
parser = ChatGPTExportParser('export.zip')

# Parse and get data
result = parser.parse()
print(f"Found {result['total_conversations']} conversations")

# Extract all text
all_text = parser.extract_all_text()

# Export to formats
parser.export_to_markdown('output.md')
parser.export_to_json('output.json')
parser.export_to_text('output.txt')

# Get statistics
stats = parser.get_statistics()
print(f"Total words: {stats['total_words']}")
```

### Batch Processing

Process multiple exports:

```bash
#!/bin/bash
for file in exports/*.zip; do
    python chatgpt_parser.py "$file" --all "processed/$(basename "$file" .zip)"
done
```

---

## 🎓 Use Cases

### 1. Backup Your Conversations
Export all your ChatGPT conversations to readable formats for backup.

### 2. Search Your History
Export to text and use grep/search tools to find specific conversations.

### 3. Analyze Your Usage
Get statistics on how you use ChatGPT.

### 4. Create Documentation
Convert conversations into documentation or tutorials.

### 5. Data Analysis
Export to JSON for programmatic analysis.

### 6. Archive Management
Organize and archive your ChatGPT history.

---

## 🔍 How ChatGPT Exports Work

### Export Structure

ChatGPT exports typically contain:

```
chatgpt_export.zip
├── conversations.json    # Main conversation data
├── chat.html            # HTML version (optional)
└── model_comparisons.json (optional)
```

### conversations.json Structure

```json
[
  {
    "id": "conversation_id",
    "title": "Conversation Title",
    "create_time": 1234567890,
    "update_time": 1234567890,
    "mapping": {
      "message_id": {
        "message": {
          "author": {"role": "user"},
          "content": {"parts": ["Message text"]},
          "create_time": 1234567890
        }
      }
    }
  }
]
```

The parser handles all variations of this structure automatically.

---

## 🛠️ Troubleshooting

### Issue: "Export file not found"
**Solution:** Check the file path is correct

### Issue: "No conversations.json found"
**Solution:** Ensure you're using a valid ChatGPT export ZIP

### Issue: "Error processing conversation"
**Solution:** The export may be corrupted. Try re-exporting from ChatGPT

### Issue: Empty output
**Solution:** Check if the export file actually contains conversations

---

## 📝 Examples

### Example 1: Quick Export
```bash
# Download your ChatGPT export
# Extract all conversations to Markdown
python chatgpt_parser.py chatgpt_export.zip --markdown my_conversations.md
```

### Example 2: Full Analysis
```bash
# Export to all formats and show stats
python chatgpt_parser.py export.zip --all analysis
python chatgpt_parser.py export.zip --stats
```

### Example 3: Search Conversations
```bash
# Export to text and search
python chatgpt_parser.py export.zip --text all.txt
grep -i "python" all.txt
```

---

## 🔐 Privacy & Security

- ✅ All processing is done locally
- ✅ No data is sent to external servers
- ✅ No internet connection required
- ✅ Your conversations stay private

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Support for more export formats
- Additional output formats
- Better HTML parsing
- Conversation filtering
- Date range selection

---

## 📄 License

MIT License - Free to use and modify

---

## 🙏 Credits

Created as part of the Kimi K2 project

---

**Ready to parse your ChatGPT exports? Start now!** 🚀

```bash
python chatgpt_parser.py your_export.zip --all output
```
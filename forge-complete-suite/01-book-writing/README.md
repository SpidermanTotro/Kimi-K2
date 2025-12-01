# 📚 THE FORGE AI - Book Writing System

Complete professional book writing and publishing platform.

## Features

- ✅ Create book projects
- ✅ Add chapters
- ✅ Track word count
- ✅ Export manuscripts
- ✅ CLI and GUI interfaces
- ✅ Professional quality

## Usage

### CLI
```bash
# Create project
./book_writer.py create "My Novel" --genre "Fantasy" --words 80000

# Add chapter
./book_writer.py chapter book_20241201_120000 "Chapter 1: The Beginning"

# List projects
./book_writer.py list

# Export
./book_writer.py export book_20241201_120000 --format txt
```

### GUI
```bash
./book_writer_gui.py
```

## Requirements

- Python 3.7+
- tkinter (for GUI)

## Installation

```bash
pip install -r requirements.txt
```

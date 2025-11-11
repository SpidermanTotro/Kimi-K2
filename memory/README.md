# Kimi K2 Memory Management System

This directory contains the extended memory management system for Kimi K2, enabling long-context conversation management and personalization.

## Features

- **Extended Context Management**: Handle conversations across large contexts (up to 128K tokens)
- **Conversation History**: Persistent storage of conversation history
- **Memory Compression**: Intelligent summarization of long conversations
- **User Profiles**: Personalized AI behavior based on user preferences
- **Context Retrieval**: Efficient retrieval of relevant context from history

## Architecture

```
memory/
├── storage/        # Storage backends (database, file, redis)
├── config/         # Configuration files
└── README.md       # This file
```

## Storage Backends

### File-based Storage
Simple JSON-based storage for development and testing.

### Database Storage
PostgreSQL or SQLite for production deployments.

### Redis Storage
High-performance in-memory storage for active sessions.

## Quick Start

### Basic Usage

```python
from memory.storage.manager import MemoryManager

# Initialize memory manager
manager = MemoryManager(backend='file')

# Store conversation
manager.store_message(
    user_id='user123',
    role='user',
    content='Hello, Kimi!'
)

# Retrieve conversation history
history = manager.get_history(user_id='user123', limit=10)

# Get user profile
profile = manager.get_profile(user_id='user123')
```

### Personalization

```python
# Update user preferences
manager.update_profile(
    user_id='user123',
    preferences={
        'language': 'en',
        'expertise_level': 'expert',
        'preferred_format': 'detailed',
        'interests': ['AI', 'coding', 'mathematics']
    }
)

# Get personalized context
context = manager.get_personalized_context(user_id='user123')
```

## Configuration

Configure memory management in `config/memory_config.yaml`:

```yaml
backend: file
storage:
  path: ./data/memory
  max_history: 1000
  compression: true
  
personalization:
  enabled: true
  profile_fields:
    - language
    - expertise_level
    - interests
    - preferences
```

## Memory Compression

Long conversations are automatically compressed using:
- Semantic summarization
- Key point extraction
- Relevance-based filtering

## User Profiles

User profiles support:
- Preference tracking
- Expertise level adaptation
- Interest-based context
- Custom AI personality settings

## API Reference

See [storage/manager.py](storage/manager.py) for detailed API documentation.

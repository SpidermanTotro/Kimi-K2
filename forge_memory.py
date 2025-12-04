#!/usr/bin/env python3
"""
THE FORGE AI - Memory System
============================

Implements a comprehensive memory system for "ChatGPT 2.0" with:
- Persistent conversation history
- User preferences learning
- Context memory across sessions
- Entity and fact extraction
- Relationship tracking
- Never-reset memory philosophy

This module enables THE FORGE AI to remember and learn from all interactions.
"""

import json
import os
import sqlite3
import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path


def utc_now() -> datetime:
    """Get current UTC time in a timezone-aware way"""
    return datetime.now(timezone.utc)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str
    content: str
    memory_type: str  # 'fact', 'preference', 'entity', 'conversation', 'skill', 'relationship'
    importance: float  # 0.0 to 1.0
    created_at: str
    last_accessed: str
    access_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    source: str = ""  # Where this memory came from
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryEntry':
        return cls(**data)


@dataclass
class ConversationTurn:
    """Represents a single turn in conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str
    session_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """Represents learned user preferences and traits"""
    user_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    expertise_areas: List[str] = field(default_factory=list)
    communication_style: str = "neutral"
    topics_of_interest: List[str] = field(default_factory=list)
    last_interaction: str = ""
    total_interactions: int = 0
    created_at: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ForgeMemorySystem:
    """
    THE FORGE AI Memory System
    
    Implements the "Never-Reset Memory" philosophy with:
    - SQLite for persistent storage
    - In-memory caching for fast access
    - Semantic memory organization
    - Importance-based retention
    - Cross-session continuity
    """
    
    def __init__(self, db_path: str = "forge_memory.db", cache_size: int = 1000):
        """
        Initialize the memory system
        
        Args:
            db_path: Path to SQLite database
            cache_size: Maximum number of memories to keep in cache
        """
        self.db_path = db_path
        self.cache_size = cache_size
        self.memory_cache: Dict[str, MemoryEntry] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.conversation_buffer: List[ConversationTurn] = []
        
        # Initialize database
        self._init_database()
        
        # Load recent memories into cache
        self._load_cache()
        
        logger.info(f"💾 Memory system initialized with {len(self.memory_cache)} cached memories")
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                context TEXT DEFAULT '{}',
                tags TEXT DEFAULT '[]',
                source TEXT DEFAULT ''
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                preferences TEXT DEFAULT '{}',
                expertise_areas TEXT DEFAULT '[]',
                communication_style TEXT DEFAULT 'neutral',
                topics_of_interest TEXT DEFAULT '[]',
                last_interaction TEXT,
                total_interactions INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Entities table (for named entity tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                attributes TEXT DEFAULT '{}',
                first_mentioned TEXT NOT NULL,
                last_mentioned TEXT NOT NULL,
                mention_count INTEGER DEFAULT 1
            )
        ''')
        
        # Relationships table (for tracking relationships between entities)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity1_name TEXT NOT NULL,
                entity2_name TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                context TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type)')
        
        conn.commit()
        conn.close()
    
    def _load_cache(self):
        """Load recent and important memories into cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load most important and recently accessed memories
        cursor.execute('''
            SELECT * FROM memories 
            ORDER BY importance DESC, last_accessed DESC 
            LIMIT ?
        ''', (self.cache_size,))
        
        for row in cursor.fetchall():
            memory = MemoryEntry(
                id=row[0],
                content=row[1],
                memory_type=row[2],
                importance=row[3],
                created_at=row[4],
                last_accessed=row[5],
                access_count=row[6],
                context=json.loads(row[7]) if row[7] else {},
                tags=json.loads(row[8]) if row[8] else [],
                source=row[9] or ""
            )
            self.memory_cache[memory.id] = memory
        
        conn.close()
    
    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for a memory"""
        timestamp = utc_now().isoformat()
        return hashlib.sha256(f"{content}{timestamp}".encode()).hexdigest()[:16]
    
    # ==================== MEMORY OPERATIONS ====================
    
    def store_memory(
        self,
        content: str,
        memory_type: str,
        importance: float = 0.5,
        context: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        source: str = ""
    ) -> str:
        """
        Store a new memory
        
        Args:
            content: The memory content
            memory_type: Type of memory (fact, preference, entity, etc.)
            importance: Importance score 0.0 to 1.0
            context: Additional context information
            tags: Tags for categorization
            source: Where this memory came from
            
        Returns:
            Memory ID
        """
        now = utc_now().isoformat()
        memory_id = self._generate_id(content)
        
        memory = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=min(max(importance, 0.0), 1.0),
            created_at=now,
            last_accessed=now,
            access_count=1,
            context=context or {},
            tags=tags or [],
            source=source
        )
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO memories 
            (id, content, memory_type, importance, created_at, last_accessed, 
             access_count, context, tags, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.id,
            memory.content,
            memory.memory_type,
            memory.importance,
            memory.created_at,
            memory.last_accessed,
            memory.access_count,
            json.dumps(memory.context),
            json.dumps(memory.tags),
            memory.source
        ))
        
        conn.commit()
        conn.close()
        
        # Add to cache
        self.memory_cache[memory_id] = memory
        self._trim_cache()
        
        logger.debug(f"💾 Stored memory: {memory_id[:8]}... [{memory_type}]")
        return memory_id
    
    def recall_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Recall a specific memory by ID
        
        Args:
            memory_id: The memory ID
            
        Returns:
            MemoryEntry or None if not found
        """
        # Check cache first
        if memory_id in self.memory_cache:
            memory = self.memory_cache[memory_id]
            self._update_access(memory)
            return memory
        
        # Query database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            memory = MemoryEntry(
                id=row[0],
                content=row[1],
                memory_type=row[2],
                importance=row[3],
                created_at=row[4],
                last_accessed=row[5],
                access_count=row[6],
                context=json.loads(row[7]) if row[7] else {},
                tags=json.loads(row[8]) if row[8] else [],
                source=row[9] or ""
            )
            self._update_access(memory)
            self.memory_cache[memory_id] = memory
            return memory
        
        return None
    
    def search_memories(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[MemoryEntry]:
        """
        Search memories by content
        
        Args:
            query: Search query
            memory_type: Filter by memory type
            limit: Maximum results
            min_importance: Minimum importance threshold
            
        Returns:
            List of matching memories
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = '''
            SELECT * FROM memories 
            WHERE content LIKE ? 
            AND importance >= ?
        '''
        params = [f'%{query}%', min_importance]
        
        if memory_type:
            sql += ' AND memory_type = ?'
            params.append(memory_type)
        
        sql += ' ORDER BY importance DESC, last_accessed DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        
        memories = []
        for row in cursor.fetchall():
            memory = MemoryEntry(
                id=row[0],
                content=row[1],
                memory_type=row[2],
                importance=row[3],
                created_at=row[4],
                last_accessed=row[5],
                access_count=row[6],
                context=json.loads(row[7]) if row[7] else {},
                tags=json.loads(row[8]) if row[8] else [],
                source=row[9] or ""
            )
            memories.append(memory)
            self._update_access(memory)
        
        conn.close()
        return memories
    
    def get_memories_by_type(
        self,
        memory_type: str,
        limit: int = 50
    ) -> List[MemoryEntry]:
        """Get memories filtered by type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM memories 
            WHERE memory_type = ?
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        ''', (memory_type, limit))
        
        memories = []
        for row in cursor.fetchall():
            memory = MemoryEntry(
                id=row[0],
                content=row[1],
                memory_type=row[2],
                importance=row[3],
                created_at=row[4],
                last_accessed=row[5],
                access_count=row[6],
                context=json.loads(row[7]) if row[7] else {},
                tags=json.loads(row[8]) if row[8] else [],
                source=row[9] or ""
            )
            memories.append(memory)
        
        conn.close()
        return memories
    
    def _update_access(self, memory: MemoryEntry):
        """Update memory access statistics"""
        memory.last_accessed = utc_now().isoformat()
        memory.access_count += 1
        
        # Update in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE memories 
            SET last_accessed = ?, access_count = ?
            WHERE id = ?
        ''', (memory.last_accessed, memory.access_count, memory.id))
        
        conn.commit()
        conn.close()
    
    def _trim_cache(self):
        """Trim cache to maintain size limit"""
        if len(self.memory_cache) > self.cache_size:
            # Sort by importance and access time
            sorted_memories = sorted(
                self.memory_cache.items(),
                key=lambda x: (x[1].importance, x[1].last_accessed)
            )
            
            # Remove least important/oldest
            to_remove = len(self.memory_cache) - self.cache_size
            for mem_id, _ in sorted_memories[:to_remove]:
                del self.memory_cache[mem_id]
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def store_conversation_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Store a conversation turn"""
        now = utc_now().isoformat()
        
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=now,
            session_id=session_id,
            metadata=metadata or {}
        )
        
        # Add to buffer
        self.conversation_buffer.append(turn)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (session_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            role,
            content,
            now,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        # Extract and store entities/facts from conversation
        self._extract_from_conversation(content, session_id)
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ConversationTurn]:
        """Get conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp, session_id, metadata
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        turns = []
        for row in cursor.fetchall():
            turn = ConversationTurn(
                role=row[0],
                content=row[1],
                timestamp=row[2],
                session_id=row[3],
                metadata=json.loads(row[4]) if row[4] else {}
            )
            turns.append(turn)
        
        conn.close()
        return list(reversed(turns))  # Return in chronological order
    
    def get_recent_context(self, session_id: str, turns: int = 10) -> str:
        """Get recent conversation context as formatted string"""
        history = self.get_conversation_history(session_id, turns)
        
        context_parts = []
        for turn in history:
            role = turn.role.capitalize()
            context_parts.append(f"[{role}]: {turn.content}")
        
        return "\n".join(context_parts)
    
    def _extract_from_conversation(self, content: str, session_id: str):
        """Extract entities and facts from conversation content"""
        # Simple entity extraction (names, places, etc.)
        # In production, this would use NLP/NER
        
        # Extract potential entities (capitalized words)
        words = content.split()
        potential_entities = [w for w in words if len(w) > 2 and w[0].isupper()]
        
        for entity in potential_entities:
            self._store_entity(entity.strip('.,!?'), "unknown", session_id)
        
        # Extract facts (statements with "is", "are", "was", "were")
        fact_patterns = [
            r'(\w+) is ([\w\s]+)',
            r'(\w+) are ([\w\s]+)',
            r'I like ([\w\s]+)',
            r'I prefer ([\w\s]+)',
            r'my favorite ([\w\s]+) is ([\w\s]+)'
        ]
        
        for pattern in fact_patterns:
            matches = re.findall(pattern, content.lower())
            for match in matches:
                if isinstance(match, tuple):
                    fact = ' '.join(match)
                else:
                    fact = match
                self.store_memory(
                    content=fact,
                    memory_type='fact',
                    importance=0.5,
                    source=session_id,
                    tags=['extracted', 'conversation']
                )
    
    # ==================== ENTITY OPERATIONS ====================
    
    def _store_entity(
        self,
        name: str,
        entity_type: str,
        source: str,
        attributes: Optional[Dict] = None
    ):
        """Store or update an entity"""
        now = utc_now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if entity exists
        cursor.execute('SELECT id, mention_count FROM entities WHERE name = ?', (name,))
        result = cursor.fetchone()
        
        if result:
            # Update existing entity
            cursor.execute('''
                UPDATE entities 
                SET last_mentioned = ?, mention_count = mention_count + 1
                WHERE name = ?
            ''', (now, name))
        else:
            # Insert new entity
            cursor.execute('''
                INSERT INTO entities 
                (name, entity_type, attributes, first_mentioned, last_mentioned, mention_count)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (name, entity_type, json.dumps(attributes or {}), now, now))
        
        conn.commit()
        conn.close()
    
    def get_entity(self, name: str) -> Optional[Dict]:
        """Get entity information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM entities WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'entity_type': row[2],
                'attributes': json.loads(row[3]) if row[3] else {},
                'first_mentioned': row[4],
                'last_mentioned': row[5],
                'mention_count': row[6]
            }
        return None
    
    # ==================== USER PROFILE OPERATIONS ====================
    
    def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get or create a user profile"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            profile = UserProfile(
                user_id=row[0],
                preferences=json.loads(row[1]) if row[1] else {},
                expertise_areas=json.loads(row[2]) if row[2] else [],
                communication_style=row[3] or 'neutral',
                topics_of_interest=json.loads(row[4]) if row[4] else [],
                last_interaction=row[5] or '',
                total_interactions=row[6] or 0,
                created_at=row[7] or ''
            )
        else:
            now = utc_now().isoformat()
            profile = UserProfile(
                user_id=user_id,
                created_at=now,
                last_interaction=now
            )
            self._save_profile(profile)
        
        conn.close()
        self.user_profiles[user_id] = profile
        return profile
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]):
        """Update user profile"""
        profile = self.get_or_create_profile(user_id)
        
        if 'preferences' in updates:
            profile.preferences.update(updates['preferences'])
        if 'expertise_areas' in updates:
            for area in updates['expertise_areas']:
                if area not in profile.expertise_areas:
                    profile.expertise_areas.append(area)
        if 'communication_style' in updates:
            profile.communication_style = updates['communication_style']
        if 'topics_of_interest' in updates:
            for topic in updates['topics_of_interest']:
                if topic not in profile.topics_of_interest:
                    profile.topics_of_interest.append(topic)
        
        profile.last_interaction = utc_now().isoformat()
        profile.total_interactions += 1
        
        self._save_profile(profile)
        self.user_profiles[user_id] = profile
    
    def _save_profile(self, profile: UserProfile):
        """Save user profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (user_id, preferences, expertise_areas, communication_style, 
             topics_of_interest, last_interaction, total_interactions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.user_id,
            json.dumps(profile.preferences),
            json.dumps(profile.expertise_areas),
            profile.communication_style,
            json.dumps(profile.topics_of_interest),
            profile.last_interaction,
            profile.total_interactions,
            profile.created_at
        ))
        
        conn.commit()
        conn.close()
    
    def learn_from_interaction(
        self,
        user_id: str,
        message: str,
        response: str,
        session_id: str
    ):
        """
        Learn from a user interaction to improve future responses
        
        This method:
        1. Updates user profile with detected preferences
        2. Stores important facts
        3. Tracks topics of interest
        4. Updates communication style preferences
        """
        profile = self.get_or_create_profile(user_id)
        
        # Detect topics from message
        topics = self._detect_topics(message)
        
        # Detect expertise level
        expertise = self._detect_expertise(message)
        
        # Detect communication preferences
        style = self._detect_style(message)
        
        # Update profile
        updates = {
            'topics_of_interest': topics,
            'expertise_areas': expertise,
            'communication_style': style
        }
        
        self.update_profile(user_id, updates)
        
        # Store the interaction as a memory
        self.store_memory(
            content=f"User asked about: {message[:100]}...",
            memory_type='conversation',
            importance=0.4,
            context={
                'user_id': user_id,
                'session_id': session_id,
                'topics': topics
            },
            tags=topics,
            source=session_id
        )
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect topics from text"""
        topic_keywords = {
            'programming': ['code', 'program', 'function', 'class', 'variable', 'debug', 'python', 'javascript'],
            'writing': ['book', 'story', 'novel', 'write', 'chapter', 'character', 'plot'],
            'video': ['video', 'edit', 'movie', 'film', 'clip', 'render'],
            'gaming': ['game', 'pokemon', 'wow', 'mmo', 'play', 'level'],
            'data': ['data', 'database', 'sql', 'analytics', 'chart'],
            'ai': ['ai', 'machine learning', 'model', 'neural', 'training'],
        }
        
        text_lower = text.lower()
        detected = []
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(topic)
        
        return detected
    
    def _detect_expertise(self, text: str) -> List[str]:
        """Detect expertise areas from text"""
        expertise_indicators = {
            'python': ['python', 'pip', 'django', 'flask', 'pandas', 'numpy'],
            'javascript': ['javascript', 'node', 'react', 'vue', 'angular', 'npm'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'deploy', 'aws', 'azure'],
            'database': ['sql', 'postgres', 'mysql', 'mongodb', 'redis'],
        }
        
        text_lower = text.lower()
        detected = []
        
        for expertise, keywords in expertise_indicators.items():
            if any(kw in text_lower for kw in keywords):
                detected.append(expertise)
        
        return detected
    
    def _detect_style(self, text: str) -> str:
        """Detect preferred communication style"""
        # Simple heuristics
        if len(text) > 500:
            return 'detailed'
        elif len(text) < 50:
            return 'concise'
        elif '?' in text and text.count('?') > 2:
            return 'inquisitive'
        elif any(word in text.lower() for word in ['please', 'thank', 'appreciate']):
            return 'formal'
        else:
            return 'neutral'
    
    # ==================== STATISTICS & ANALYTICS ====================
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total memories
        cursor.execute('SELECT COUNT(*) FROM memories')
        total_memories = cursor.fetchone()[0]
        
        # Memories by type
        cursor.execute('SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type')
        by_type = dict(cursor.fetchall())
        
        # Total conversations
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        # Unique sessions
        cursor.execute('SELECT COUNT(DISTINCT session_id) FROM conversations')
        unique_sessions = cursor.fetchone()[0]
        
        # Total entities
        cursor.execute('SELECT COUNT(*) FROM entities')
        total_entities = cursor.fetchone()[0]
        
        # Total user profiles
        cursor.execute('SELECT COUNT(*) FROM user_profiles')
        total_profiles = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_memories': total_memories,
            'memories_by_type': by_type,
            'cached_memories': len(self.memory_cache),
            'total_conversations': total_conversations,
            'unique_sessions': unique_sessions,
            'total_entities': total_entities,
            'total_user_profiles': total_profiles
        }
    
    def get_context_for_prompt(
        self,
        user_id: str,
        session_id: str,
        query: str,
        max_memories: int = 5
    ) -> str:
        """
        Generate context string for prompt augmentation
        
        This combines:
        - Recent conversation history
        - Relevant memories
        - User preferences
        - Related entities
        """
        context_parts = []
        
        # User profile context
        profile = self.get_or_create_profile(user_id)
        if profile.preferences or profile.topics_of_interest:
            context_parts.append("## User Context")
            if profile.topics_of_interest:
                context_parts.append(f"Interests: {', '.join(profile.topics_of_interest)}")
            if profile.expertise_areas:
                context_parts.append(f"Expertise: {', '.join(profile.expertise_areas)}")
            if profile.communication_style != 'neutral':
                context_parts.append(f"Preferred style: {profile.communication_style}")
        
        # Recent conversation
        recent = self.get_conversation_history(session_id, limit=5)
        if recent:
            context_parts.append("\n## Recent Conversation")
            for turn in recent[-3:]:  # Last 3 turns
                context_parts.append(f"[{turn.role}]: {turn.content[:200]}...")
        
        # Relevant memories
        memories = self.search_memories(query, limit=max_memories, min_importance=0.3)
        if memories:
            context_parts.append("\n## Relevant Knowledge")
            for mem in memories:
                context_parts.append(f"- {mem.content[:150]}...")
        
        return "\n".join(context_parts)
    
    def cleanup_old_memories(self, days: int = 90, min_importance: float = 0.3):
        """
        Clean up old, low-importance memories
        
        Note: Important memories (importance >= min_importance) are never deleted
        """
        cutoff = (utc_now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM memories 
            WHERE last_accessed < ? AND importance < ?
        ''', (cutoff, min_importance))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"🧹 Cleaned up {deleted} old memories")
        
        return deleted


# ==================== CONVENIENCE FUNCTIONS ====================

def create_memory_system(db_path: str = "forge_memory.db") -> ForgeMemorySystem:
    """Create a new memory system instance"""
    return ForgeMemorySystem(db_path)


def get_default_memory_system() -> ForgeMemorySystem:
    """Get or create the default memory system"""
    if not hasattr(get_default_memory_system, '_instance'):
        get_default_memory_system._instance = ForgeMemorySystem()
    return get_default_memory_system._instance


# ==================== MAIN ====================

def main():
    """Demo the memory system"""
    print("=" * 60)
    print("🧠 THE FORGE AI - Memory System Demo")
    print("=" * 60)
    print()
    
    # Initialize memory system
    memory = ForgeMemorySystem()
    
    # Store some memories
    print("💾 Storing memories...")
    
    memory.store_memory(
        content="User prefers Python for backend development",
        memory_type="preference",
        importance=0.8,
        tags=["python", "backend", "programming"]
    )
    
    memory.store_memory(
        content="Project uses FastAPI framework with PostgreSQL database",
        memory_type="fact",
        importance=0.7,
        tags=["fastapi", "postgresql", "architecture"]
    )
    
    memory.store_memory(
        content="User is writing a fantasy novel about dragons",
        memory_type="fact",
        importance=0.6,
        tags=["writing", "fantasy", "novel"]
    )
    
    # Store conversation
    print("💬 Storing conversation...")
    session_id = "demo_session"
    
    memory.store_conversation_turn(
        session_id=session_id,
        role="user",
        content="Help me write a Python function for data processing"
    )
    
    memory.store_conversation_turn(
        session_id=session_id,
        role="assistant",
        content="I'll help you create a data processing function..."
    )
    
    # Update user profile
    print("👤 Updating user profile...")
    memory.update_profile("demo_user", {
        "preferences": {"language": "python", "style": "detailed"},
        "topics_of_interest": ["programming", "data science"],
        "expertise_areas": ["python", "sql"]
    })
    
    # Search memories
    print("\n🔍 Searching memories for 'Python'...")
    results = memory.search_memories("Python")
    for mem in results:
        print(f"  - [{mem.memory_type}] {mem.content[:50]}...")
    
    # Get stats
    print("\n📊 Memory Statistics:")
    stats = memory.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Generate context
    print("\n📝 Generated Context for Prompt:")
    context = memory.get_context_for_prompt(
        user_id="demo_user",
        session_id=session_id,
        query="Python programming"
    )
    print(context)
    
    print("\n" + "=" * 60)
    print("✅ Memory System Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

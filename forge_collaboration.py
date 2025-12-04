#!/usr/bin/env python3
"""
THE FORGE AI - Collaboration Module
=====================================

Implements group collaboration features for "ChatGPT 2.0" including:
- Shared memory spaces
- Multi-user sessions
- Access control and permissions
- Collaborative workspaces
- Role-based interactions

This module enables team collaboration within THE FORGE AI.
"""

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC time in a timezone-aware way"""
    return datetime.now(timezone.utc)


class Role(Enum):
    """User roles for access control"""
    OWNER = "owner"           # Full control, can delete workspace
    ADMIN = "admin"           # Can manage members, modify settings
    EDITOR = "editor"         # Can read and write
    VIEWER = "viewer"         # Read-only access
    GUEST = "guest"           # Limited temporary access


class Permission(Enum):
    """Granular permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_SETTINGS = "manage_settings"
    SHARE = "share"
    EXPORT = "export"


# Role to permissions mapping
ROLE_PERMISSIONS = {
    Role.OWNER: {Permission.READ, Permission.WRITE, Permission.DELETE, 
                 Permission.MANAGE_MEMBERS, Permission.MANAGE_SETTINGS, 
                 Permission.SHARE, Permission.EXPORT},
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE,
                 Permission.MANAGE_MEMBERS, Permission.SHARE, Permission.EXPORT},
    Role.EDITOR: {Permission.READ, Permission.WRITE, Permission.SHARE, Permission.EXPORT},
    Role.VIEWER: {Permission.READ, Permission.EXPORT},
    Role.GUEST: {Permission.READ},
}


@dataclass
class WorkspaceMember:
    """Represents a member of a workspace"""
    user_id: str
    role: Role
    joined_at: str
    invited_by: Optional[str] = None
    last_active: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "joined_at": self.joined_at,
            "invited_by": self.invited_by,
            "last_active": self.last_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkspaceMember':
        return cls(
            user_id=data["user_id"],
            role=Role(data["role"]),
            joined_at=data["joined_at"],
            invited_by=data.get("invited_by"),
            last_active=data.get("last_active", "")
        )


@dataclass
class SharedMemory:
    """Represents a shared memory item in a workspace"""
    memory_id: str
    content: str
    memory_type: str
    created_by: str
    created_at: str
    last_modified_by: str
    last_modified_at: str
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SharedMemory':
        return cls(**data)


@dataclass
class Workspace:
    """Represents a collaborative workspace"""
    workspace_id: str
    name: str
    description: str
    created_by: str
    created_at: str
    is_public: bool = False
    settings: Dict[str, Any] = field(default_factory=dict)
    members: List[WorkspaceMember] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "is_public": self.is_public,
            "settings": self.settings,
            "members": [m.to_dict() for m in self.members]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workspace':
        members = [WorkspaceMember.from_dict(m) for m in data.get("members", [])]
        return cls(
            workspace_id=data["workspace_id"],
            name=data["name"],
            description=data["description"],
            created_by=data["created_by"],
            created_at=data["created_at"],
            is_public=data.get("is_public", False),
            settings=data.get("settings", {}),
            members=members
        )


@dataclass
class CollaborationSession:
    """Represents an active collaboration session"""
    session_id: str
    workspace_id: str
    active_users: List[str]
    started_at: str
    context: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)


class CollaborationSystem:
    """
    THE FORGE AI Collaboration System
    
    Enables team collaboration with:
    - Shared workspaces
    - Role-based access control
    - Shared memory spaces
    - Multi-user sessions
    """
    
    def __init__(self, db_path: str = "forge_collaboration.db"):
        """Initialize the collaboration system"""
        self.db_path = db_path
        self.workspaces: Dict[str, Workspace] = {}
        self.active_sessions: Dict[str, CollaborationSession] = {}
        
        self._init_database()
        self._load_workspaces()
        
        logger.info("👥 Collaboration System initialized")
    
    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workspaces table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workspaces (
                workspace_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_public INTEGER DEFAULT 0,
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        # Members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workspace_members (
                workspace_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                invited_by TEXT,
                last_active TEXT,
                PRIMARY KEY (workspace_id, user_id),
                FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id)
            )
        ''')
        
        # Shared memories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_memories (
                memory_id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_modified_by TEXT NOT NULL,
                last_modified_at TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id)
            )
        ''')
        
        # Collaboration sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                context TEXT DEFAULT '{}',
                conversation_history TEXT DEFAULT '[]',
                FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id)
            )
        ''')
        
        # Session participants
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_participants (
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                left_at TEXT,
                PRIMARY KEY (session_id, user_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # Indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_members_workspace ON workspace_members(workspace_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memories_workspace ON shared_memories(workspace_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_workspace ON sessions(workspace_id)')
        
        conn.commit()
        conn.close()
    
    def _load_workspaces(self):
        """Load workspaces from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM workspaces')
        for row in cursor.fetchall():
            workspace = Workspace(
                workspace_id=row[0],
                name=row[1],
                description=row[2] or "",
                created_by=row[3],
                created_at=row[4],
                is_public=bool(row[5]),
                settings=json.loads(row[6]) if row[6] else {}
            )
            
            # Load members
            cursor.execute(
                'SELECT * FROM workspace_members WHERE workspace_id = ?',
                (workspace.workspace_id,)
            )
            for member_row in cursor.fetchall():
                member = WorkspaceMember(
                    user_id=member_row[1],
                    role=Role(member_row[2]),
                    joined_at=member_row[3],
                    invited_by=member_row[4],
                    last_active=member_row[5] or ""
                )
                workspace.members.append(member)
            
            self.workspaces[workspace.workspace_id] = workspace
        
        conn.close()
        logger.info(f"📂 Loaded {len(self.workspaces)} workspaces")
    
    # ==================== WORKSPACE OPERATIONS ====================
    
    def create_workspace(
        self,
        name: str,
        description: str,
        created_by: str,
        is_public: bool = False,
        settings: Optional[Dict[str, Any]] = None
    ) -> Workspace:
        """Create a new collaborative workspace"""
        now = utc_now().isoformat()
        workspace_id = str(uuid.uuid4())[:8]
        
        workspace = Workspace(
            workspace_id=workspace_id,
            name=name,
            description=description,
            created_by=created_by,
            created_at=now,
            is_public=is_public,
            settings=settings or {}
        )
        
        # Add creator as owner
        owner = WorkspaceMember(
            user_id=created_by,
            role=Role.OWNER,
            joined_at=now
        )
        workspace.members.append(owner)
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workspaces 
            (workspace_id, name, description, created_by, created_at, is_public, settings)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            workspace.workspace_id,
            workspace.name,
            workspace.description,
            workspace.created_by,
            workspace.created_at,
            1 if workspace.is_public else 0,
            json.dumps(workspace.settings)
        ))
        
        cursor.execute('''
            INSERT INTO workspace_members 
            (workspace_id, user_id, role, joined_at, invited_by, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            workspace.workspace_id,
            owner.user_id,
            owner.role.value,
            owner.joined_at,
            None,
            now
        ))
        
        conn.commit()
        conn.close()
        
        self.workspaces[workspace_id] = workspace
        logger.info(f"📁 Created workspace: {name} ({workspace_id})")
        
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get a workspace by ID"""
        return self.workspaces.get(workspace_id)
    
    def list_user_workspaces(self, user_id: str) -> List[Workspace]:
        """List all workspaces a user is a member of"""
        return [
            ws for ws in self.workspaces.values()
            if any(m.user_id == user_id for m in ws.members)
        ]
    
    def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """Delete a workspace (owner only)"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return False
        
        if not self.check_permission(workspace_id, user_id, Permission.DELETE):
            logger.warning(f"❌ User {user_id} cannot delete workspace {workspace_id}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM shared_memories WHERE workspace_id = ?', (workspace_id,))
        cursor.execute('DELETE FROM workspace_members WHERE workspace_id = ?', (workspace_id,))
        cursor.execute('DELETE FROM workspaces WHERE workspace_id = ?', (workspace_id,))
        
        conn.commit()
        conn.close()
        
        del self.workspaces[workspace_id]
        logger.info(f"🗑️ Deleted workspace: {workspace_id}")
        
        return True
    
    # ==================== MEMBER OPERATIONS ====================
    
    def add_member(
        self,
        workspace_id: str,
        user_id: str,
        role: Role,
        invited_by: str
    ) -> bool:
        """Add a member to a workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return False
        
        if not self.check_permission(workspace_id, invited_by, Permission.MANAGE_MEMBERS):
            logger.warning(f"❌ User {invited_by} cannot add members to {workspace_id}")
            return False
        
        # Check if already a member
        if any(m.user_id == user_id for m in workspace.members):
            logger.warning(f"⚠️ User {user_id} is already a member of {workspace_id}")
            return False
        
        now = utc_now().isoformat()
        member = WorkspaceMember(
            user_id=user_id,
            role=role,
            joined_at=now,
            invited_by=invited_by
        )
        
        workspace.members.append(member)
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workspace_members 
            (workspace_id, user_id, role, joined_at, invited_by, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            workspace_id,
            member.user_id,
            member.role.value,
            member.joined_at,
            member.invited_by,
            now
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"👤 Added {user_id} to workspace {workspace_id} as {role.value}")
        return True
    
    def remove_member(
        self,
        workspace_id: str,
        user_id: str,
        removed_by: str
    ) -> bool:
        """Remove a member from a workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return False
        
        # Can remove self or if have manage_members permission
        if user_id != removed_by:
            if not self.check_permission(workspace_id, removed_by, Permission.MANAGE_MEMBERS):
                return False
        
        # Cannot remove owner
        member = next((m for m in workspace.members if m.user_id == user_id), None)
        if member and member.role == Role.OWNER:
            logger.warning(f"❌ Cannot remove owner from workspace")
            return False
        
        workspace.members = [m for m in workspace.members if m.user_id != user_id]
        
        # Remove from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM workspace_members WHERE workspace_id = ? AND user_id = ?',
            (workspace_id, user_id)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"👤 Removed {user_id} from workspace {workspace_id}")
        return True
    
    def update_member_role(
        self,
        workspace_id: str,
        user_id: str,
        new_role: Role,
        updated_by: str
    ) -> bool:
        """Update a member's role"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return False
        
        if not self.check_permission(workspace_id, updated_by, Permission.MANAGE_MEMBERS):
            return False
        
        member = next((m for m in workspace.members if m.user_id == user_id), None)
        if not member:
            return False
        
        # Cannot demote owner or promote to owner
        if member.role == Role.OWNER or new_role == Role.OWNER:
            logger.warning(f"❌ Cannot change owner role")
            return False
        
        member.role = new_role
        
        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE workspace_members SET role = ? WHERE workspace_id = ? AND user_id = ?',
            (new_role.value, workspace_id, user_id)
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"🔄 Updated {user_id} role to {new_role.value} in {workspace_id}")
        return True
    
    # ==================== PERMISSION OPERATIONS ====================
    
    def get_user_role(self, workspace_id: str, user_id: str) -> Optional[Role]:
        """Get user's role in a workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return None
        
        member = next((m for m in workspace.members if m.user_id == user_id), None)
        if member:
            return member.role
        
        # Public workspaces grant guest access
        if workspace.is_public:
            return Role.GUEST
        
        return None
    
    def check_permission(
        self,
        workspace_id: str,
        user_id: str,
        permission: Permission
    ) -> bool:
        """Check if user has a specific permission in a workspace"""
        role = self.get_user_role(workspace_id, user_id)
        if not role:
            return False
        
        return permission in ROLE_PERMISSIONS.get(role, set())
    
    def get_user_permissions(
        self,
        workspace_id: str,
        user_id: str
    ) -> Set[Permission]:
        """Get all permissions for a user in a workspace"""
        role = self.get_user_role(workspace_id, user_id)
        if not role:
            return set()
        
        return ROLE_PERMISSIONS.get(role, set())
    
    # ==================== SHARED MEMORY OPERATIONS ====================
    
    def add_shared_memory(
        self,
        workspace_id: str,
        content: str,
        memory_type: str,
        user_id: str,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Add a shared memory to a workspace"""
        if not self.check_permission(workspace_id, user_id, Permission.WRITE):
            logger.warning(f"❌ User {user_id} cannot write to {workspace_id}")
            return None
        
        now = utc_now().isoformat()
        memory_id = hashlib.sha256(f"{content}{now}".encode()).hexdigest()[:16]
        
        memory = SharedMemory(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            created_by=user_id,
            created_at=now,
            last_modified_by=user_id,
            last_modified_at=now,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shared_memories 
            (memory_id, workspace_id, content, memory_type, created_by, created_at,
             last_modified_by, last_modified_at, importance, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.memory_id,
            workspace_id,
            memory.content,
            memory.memory_type,
            memory.created_by,
            memory.created_at,
            memory.last_modified_by,
            memory.last_modified_at,
            memory.importance,
            json.dumps(memory.tags),
            json.dumps(memory.metadata)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Added shared memory to {workspace_id}: {memory_id[:8]}...")
        return memory_id
    
    def get_shared_memories(
        self,
        workspace_id: str,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[SharedMemory]:
        """Get shared memories from a workspace"""
        if not self.check_permission(workspace_id, user_id, Permission.READ):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if memory_type:
            cursor.execute('''
                SELECT * FROM shared_memories 
                WHERE workspace_id = ? AND memory_type = ?
                ORDER BY importance DESC, last_modified_at DESC
                LIMIT ?
            ''', (workspace_id, memory_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM shared_memories 
                WHERE workspace_id = ?
                ORDER BY importance DESC, last_modified_at DESC
                LIMIT ?
            ''', (workspace_id, limit))
        
        memories = []
        for row in cursor.fetchall():
            memory = SharedMemory(
                memory_id=row[0],
                content=row[2],
                memory_type=row[3],
                created_by=row[4],
                created_at=row[5],
                last_modified_by=row[6],
                last_modified_at=row[7],
                importance=row[8],
                tags=json.loads(row[9]) if row[9] else [],
                metadata=json.loads(row[10]) if row[10] else {}
            )
            memories.append(memory)
        
        conn.close()
        return memories
    
    def search_shared_memories(
        self,
        workspace_id: str,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[SharedMemory]:
        """Search shared memories in a workspace"""
        if not self.check_permission(workspace_id, user_id, Permission.READ):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM shared_memories 
            WHERE workspace_id = ? AND content LIKE ?
            ORDER BY importance DESC
            LIMIT ?
        ''', (workspace_id, f"%{query}%", limit))
        
        memories = []
        for row in cursor.fetchall():
            memory = SharedMemory(
                memory_id=row[0],
                content=row[2],
                memory_type=row[3],
                created_by=row[4],
                created_at=row[5],
                last_modified_by=row[6],
                last_modified_at=row[7],
                importance=row[8],
                tags=json.loads(row[9]) if row[9] else [],
                metadata=json.loads(row[10]) if row[10] else {}
            )
            memories.append(memory)
        
        conn.close()
        return memories
    
    # ==================== SESSION OPERATIONS ====================
    
    def start_session(
        self,
        workspace_id: str,
        user_id: str
    ) -> Optional[CollaborationSession]:
        """Start a collaboration session"""
        if not self.check_permission(workspace_id, user_id, Permission.READ):
            return None
        
        now = utc_now().isoformat()
        session_id = str(uuid.uuid4())[:8]
        
        session = CollaborationSession(
            session_id=session_id,
            workspace_id=workspace_id,
            active_users=[user_id],
            started_at=now
        )
        
        self.active_sessions[session_id] = session
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions 
            (session_id, workspace_id, started_at, context, conversation_history)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session.session_id,
            session.workspace_id,
            session.started_at,
            json.dumps(session.context),
            json.dumps(session.conversation_history)
        ))
        
        cursor.execute('''
            INSERT INTO session_participants (session_id, user_id, joined_at)
            VALUES (?, ?, ?)
        ''', (session_id, user_id, now))
        
        conn.commit()
        conn.close()
        
        logger.info(f"🚀 Started session {session_id} in workspace {workspace_id}")
        return session
    
    def join_session(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """Join an active collaboration session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        if not self.check_permission(session.workspace_id, user_id, Permission.READ):
            return False
        
        if user_id not in session.active_users:
            session.active_users.append(user_id)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO session_participants (session_id, user_id, joined_at)
                VALUES (?, ?, ?)
            ''', (session_id, user_id, utc_now().isoformat()))
            
            conn.commit()
            conn.close()
        
        logger.info(f"👋 User {user_id} joined session {session_id}")
        return True
    
    def leave_session(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """Leave a collaboration session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        if user_id in session.active_users:
            session.active_users.remove(user_id)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE session_participants 
                SET left_at = ? 
                WHERE session_id = ? AND user_id = ?
            ''', (utc_now().isoformat(), session_id, user_id))
            
            conn.commit()
            conn.close()
        
        # End session if no users left
        if not session.active_users:
            self.end_session(session_id)
        
        logger.info(f"👋 User {user_id} left session {session_id}")
        return True
    
    def end_session(self, session_id: str) -> bool:
        """End a collaboration session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET ended_at = ?, context = ?, conversation_history = ?
            WHERE session_id = ?
        ''', (
            utc_now().isoformat(),
            json.dumps(session.context),
            json.dumps(session.conversation_history),
            session_id
        ))
        
        conn.commit()
        conn.close()
        
        del self.active_sessions[session_id]
        logger.info(f"🏁 Ended session {session_id}")
        return True
    
    def add_to_session_history(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str
    ) -> bool:
        """Add a message to session conversation history"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        if user_id not in session.active_users:
            return False
        
        session.conversation_history.append({
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": utc_now().isoformat()
        })
        
        return True
    
    # ==================== STATISTICS ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collaboration system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM workspaces')
        total_workspaces = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM workspace_members')
        total_memberships = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM shared_memories')
        total_shared_memories = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_workspaces": total_workspaces,
            "loaded_workspaces": len(self.workspaces),
            "total_memberships": total_memberships,
            "total_shared_memories": total_shared_memories,
            "total_sessions": total_sessions,
            "active_sessions": len(self.active_sessions)
        }


# Convenience function
def create_collaboration_system(db_path: str = "forge_collaboration.db") -> CollaborationSystem:
    """Create a new collaboration system instance"""
    return CollaborationSystem(db_path)


# ==================== MAIN ====================

def main():
    """Demo the collaboration system"""
    print("=" * 60)
    print("👥 THE FORGE AI - Collaboration System Demo")
    print("=" * 60)
    print()
    
    # Initialize system
    collab = CollaborationSystem()
    
    # Create a workspace
    print("📁 Demo: Creating Workspace")
    print("-" * 40)
    workspace = collab.create_workspace(
        name="AI Research Team",
        description="Collaborative AI research workspace",
        created_by="alice"
    )
    print(f"  Created: {workspace.name} ({workspace.workspace_id})")
    print(f"  Owner: {workspace.created_by}")
    print()
    
    # Add members
    print("👤 Demo: Adding Members")
    print("-" * 40)
    collab.add_member(workspace.workspace_id, "bob", Role.EDITOR, "alice")
    collab.add_member(workspace.workspace_id, "carol", Role.VIEWER, "alice")
    
    for member in workspace.members:
        print(f"  {member.user_id}: {member.role.value}")
    print()
    
    # Check permissions
    print("🔒 Demo: Permission Checks")
    print("-" * 40)
    users = ["alice", "bob", "carol", "dave"]
    perms = [Permission.READ, Permission.WRITE, Permission.MANAGE_MEMBERS]
    
    for user in users:
        user_perms = [p.value for p in perms if collab.check_permission(workspace.workspace_id, user, p)]
        print(f"  {user}: {', '.join(user_perms) if user_perms else 'no access'}")
    print()
    
    # Add shared memory
    print("💾 Demo: Shared Memory")
    print("-" * 40)
    memory_id = collab.add_shared_memory(
        workspace_id=workspace.workspace_id,
        content="Our research goal is to improve NLP models",
        memory_type="goal",
        user_id="alice",
        importance=0.9,
        tags=["nlp", "research"]
    )
    print(f"  Added memory: {memory_id}")
    
    memories = collab.get_shared_memories(workspace.workspace_id, "bob")
    print(f"  Total shared memories: {len(memories)}")
    print()
    
    # Start session
    print("🚀 Demo: Collaboration Session")
    print("-" * 40)
    session = collab.start_session(workspace.workspace_id, "alice")
    print(f"  Started session: {session.session_id}")
    
    collab.join_session(session.session_id, "bob")
    print(f"  Bob joined session")
    print(f"  Active users: {session.active_users}")
    print()
    
    # Get stats
    print("📊 Demo: System Statistics")
    print("-" * 40)
    stats = collab.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Cleanup
    collab.end_session(session.session_id)
    
    print("\n" + "=" * 60)
    print("✅ Collaboration System Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

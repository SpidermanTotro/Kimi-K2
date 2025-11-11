"""
Memory Module
Persistent memory for session recall
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class MemoryModule:
    """
    Manages persistent memory across sessions.
    
    Features:
    - Long-term memory storage
    - Memory retrieval
    - Memory consolidation
    - Context recall
    """
    
    def __init__(self):
        """Initialize the memory module."""
        self.memories: Dict[str, List[Dict[str, Any]]] = {}
        self.memory_index: Dict[str, Dict[str, List[int]]] = {}
    
    def store_memory(
        self,
        user_id: str,
        content: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store a memory for a user.
        
        Args:
            user_id: User identifier
            content: Memory content
            category: Memory category
            tags: Optional tags for indexing
            metadata: Optional metadata
            
        Returns:
            Storage result
        """
        if user_id not in self.memories:
            self.memories[user_id] = []
            self.memory_index[user_id] = {}
        
        memory_id = len(self.memories[user_id])
        
        memory = {
            "id": memory_id,
            "user_id": user_id,
            "content": content,
            "category": category,
            "tags": tags or [],
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "access_count": 0
        }
        
        self.memories[user_id].append(memory)
        
        # Index by category
        if category not in self.memory_index[user_id]:
            self.memory_index[user_id][category] = []
        self.memory_index[user_id][category].append(memory_id)
        
        # Index by tags
        for tag in (tags or []):
            tag_key = f"tag:{tag}"
            if tag_key not in self.memory_index[user_id]:
                self.memory_index[user_id][tag_key] = []
            self.memory_index[user_id][tag_key].append(memory_id)
        
        return {
            "status": "success",
            "memory_id": memory_id,
            "user_id": user_id,
            "category": category
        }
    
    def recall_memories(
        self,
        user_id: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Recall memories for a user.
        
        Args:
            user_id: User identifier
            category: Optional category filter
            tags: Optional tag filter
            limit: Optional limit on results
            
        Returns:
            Retrieved memories
        """
        if user_id not in self.memories:
            return {
                "status": "success",
                "user_id": user_id,
                "memories": [],
                "count": 0
            }
        
        memory_ids = set(range(len(self.memories[user_id])))
        
        # Filter by category
        if category and category in self.memory_index[user_id]:
            memory_ids &= set(self.memory_index[user_id][category])
        
        # Filter by tags
        if tags:
            for tag in tags:
                tag_key = f"tag:{tag}"
                if tag_key in self.memory_index[user_id]:
                    memory_ids &= set(self.memory_index[user_id][tag_key])
        
        # Get memories and update access count
        memories = []
        for mem_id in sorted(memory_ids, reverse=True):
            memory = self.memories[user_id][mem_id]
            memory["access_count"] += 1
            memories.append(memory)
            
            if limit and len(memories) >= limit:
                break
        
        return {
            "status": "success",
            "user_id": user_id,
            "memories": memories,
            "count": len(memories)
        }
    
    def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Search memories by content.
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum results
            
        Returns:
            Search results
        """
        if user_id not in self.memories:
            return {
                "status": "success",
                "user_id": user_id,
                "query": query,
                "memories": [],
                "count": 0
            }
        
        query_lower = query.lower()
        matching_memories = []
        
        for memory in self.memories[user_id]:
            content_lower = memory["content"].lower()
            
            # Simple relevance scoring
            if query_lower in content_lower:
                score = content_lower.count(query_lower)
                
                # Boost score for tag matches
                for tag in memory["tags"]:
                    if query_lower in tag.lower():
                        score += 2
                
                matching_memories.append((score, memory))
        
        # Sort by relevance
        matching_memories.sort(reverse=True, key=lambda x: x[0])
        
        # Update access count
        results = []
        for score, memory in matching_memories[:limit]:
            memory["access_count"] += 1
            results.append(memory)
        
        return {
            "status": "success",
            "user_id": user_id,
            "query": query,
            "memories": results,
            "count": len(results)
        }
    
    def consolidate_memories(
        self,
        user_id: str,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Consolidate related memories into summaries.
        
        Args:
            user_id: User identifier
            category: Optional category to consolidate
            
        Returns:
            Consolidation result
        """
        if user_id not in self.memories:
            return {
                "status": "error",
                "message": "No memories found for user"
            }
        
        # Get memories to consolidate
        recall_result = self.recall_memories(user_id, category=category)
        memories = recall_result["memories"]
        
        if not memories:
            return {
                "status": "success",
                "message": "No memories to consolidate"
            }
        
        # Simple consolidation: group by category
        consolidated = {}
        for memory in memories:
            cat = memory["category"]
            if cat not in consolidated:
                consolidated[cat] = []
            consolidated[cat].append(memory["content"])
        
        return {
            "status": "success",
            "user_id": user_id,
            "categories": len(consolidated),
            "consolidated": consolidated
        }
    
    def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Memory statistics
        """
        if user_id not in self.memories:
            return {
                "status": "success",
                "user_id": user_id,
                "total_memories": 0,
                "categories": 0
            }
        
        memories = self.memories[user_id]
        categories = set(m["category"] for m in memories)
        
        total_accesses = sum(m["access_count"] for m in memories)
        
        return {
            "status": "success",
            "user_id": user_id,
            "total_memories": len(memories),
            "categories": len(categories),
            "category_list": list(categories),
            "total_accesses": total_accesses
        }
    
    def export_memories(self, user_id: str) -> Optional[str]:
        """
        Export memories as JSON.
        
        Args:
            user_id: User identifier
            
        Returns:
            JSON string of memories
        """
        if user_id not in self.memories:
            return None
        
        return json.dumps({
            "user_id": user_id,
            "memories": self.memories[user_id],
            "index": self.memory_index[user_id]
        }, indent=2)
    
    def clear_memories(
        self,
        user_id: str,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Clear memories for a user.
        
        Args:
            user_id: User identifier
            category: Optional category to clear (clears all if not specified)
            
        Returns:
            Clear operation result
        """
        if user_id not in self.memories:
            return {
                "status": "success",
                "message": "No memories to clear"
            }
        
        if category:
            # Clear specific category
            if category in self.memory_index[user_id]:
                memory_ids = self.memory_index[user_id][category]
                for mem_id in sorted(memory_ids, reverse=True):
                    del self.memories[user_id][mem_id]
                del self.memory_index[user_id][category]
            
            return {
                "status": "success",
                "user_id": user_id,
                "cleared_category": category
            }
        else:
            # Clear all memories
            count = len(self.memories[user_id])
            del self.memories[user_id]
            del self.memory_index[user_id]
            
            return {
                "status": "success",
                "user_id": user_id,
                "cleared_count": count
            }

#!/usr/bin/env python3
"""
THE FORGE - Codex System for ChatGPT 2.0
=========================================

Implements Codex capabilities for documentation browsing, querying, and 
content editing directly from the system. Integrates tightly into ChatGPT 2.0's
multimodal and reasoning workflows.

Features:
- Documentation browsing and indexing
- Semantic search and querying
- Content editing and versioning
- Integration with reasoning workflows
- Multimodal content support
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodexDocument:
    """Represents a document in the Codex system"""
    id: str
    title: str
    content: str
    doc_type: str  # 'markdown', 'code', 'text', 'config', 'multimodal'
    path: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    version: int = 1
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    sections: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.title}{self.content[:100]}".encode()
            ).hexdigest()[:16]
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class CodexQuery:
    """Represents a search query"""
    query: str
    filters: Dict[str, Any] = field(default_factory=dict)
    max_results: int = 10
    include_sections: bool = True


@dataclass
class CodexSearchResult:
    """Represents a search result"""
    document: CodexDocument
    relevance_score: float
    matched_sections: List[Dict[str, Any]] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)


@dataclass 
class ContentEdit:
    """Represents an edit to document content"""
    document_id: str
    edit_type: str  # 'insert', 'delete', 'replace', 'append'
    position: Optional[int] = None
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    timestamp: str = ""
    author: str = "system"
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class CodexIndex:
    """
    Document indexing system for fast search and retrieval.
    
    Provides:
    - Full-text indexing
    - Section-level indexing
    - Tag-based filtering
    - Semantic search support
    """
    
    def __init__(self):
        self.documents: Dict[str, CodexDocument] = {}
        self.word_index: Dict[str, List[str]] = {}  # word -> doc_ids
        self.tag_index: Dict[str, List[str]] = {}  # tag -> doc_ids
        self.section_index: Dict[str, List[Tuple[str, int]]] = {}  # word -> (doc_id, section_idx)
    
    def add_document(self, doc: CodexDocument):
        """Add a document to the index"""
        self.documents[doc.id] = doc
        
        # Index words in content
        words = self._tokenize(doc.content)
        for word in words:
            if word not in self.word_index:
                self.word_index[word] = []
            if doc.id not in self.word_index[word]:
                self.word_index[word].append(doc.id)
        
        # Index tags
        for tag in doc.tags:
            tag_lower = tag.lower()
            if tag_lower not in self.tag_index:
                self.tag_index[tag_lower] = []
            if doc.id not in self.tag_index[tag_lower]:
                self.tag_index[tag_lower].append(doc.id)
        
        # Index sections
        for idx, section in enumerate(doc.sections):
            section_words = self._tokenize(section.get('content', ''))
            for word in section_words:
                if word not in self.section_index:
                    self.section_index[word] = []
                self.section_index[word].append((doc.id, idx))
        
        logger.info(f"📄 Indexed document: {doc.title} ({doc.id})")
    
    def remove_document(self, doc_id: str):
        """Remove a document from the index"""
        if doc_id not in self.documents:
            return
        
        doc = self.documents[doc_id]
        
        # Remove from word index
        for word in self._tokenize(doc.content):
            if word in self.word_index:
                self.word_index[word] = [d for d in self.word_index[word] if d != doc_id]
        
        # Remove from tag index
        for tag in doc.tags:
            tag_lower = tag.lower()
            if tag_lower in self.tag_index:
                self.tag_index[tag_lower] = [d for d in self.tag_index[tag_lower] if d != doc_id]
        
        # Remove from section index
        self.section_index = {
            word: [(d, i) for d, i in refs if d != doc_id]
            for word, refs in self.section_index.items()
        }
        
        del self.documents[doc_id]
    
    def search(self, query: CodexQuery) -> List[CodexSearchResult]:
        """Search for documents matching the query"""
        query_words = self._tokenize(query.query)
        
        # Find matching documents
        doc_scores: Dict[str, float] = {}
        doc_matches: Dict[str, List[str]] = {}
        
        for word in query_words:
            # Search word index
            if word in self.word_index:
                for doc_id in self.word_index[word]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1
                    if doc_id not in doc_matches:
                        doc_matches[doc_id] = []
                    doc_matches[doc_id].append(word)
        
        # Apply tag filters
        if 'tags' in query.filters:
            filter_tags = [t.lower() for t in query.filters['tags']]
            filtered_docs = set()
            for tag in filter_tags:
                if tag in self.tag_index:
                    filtered_docs.update(self.tag_index[tag])
            doc_scores = {k: v for k, v in doc_scores.items() if k in filtered_docs}
        
        # Apply doc_type filter
        if 'doc_type' in query.filters:
            doc_type = query.filters['doc_type']
            doc_scores = {
                k: v for k, v in doc_scores.items() 
                if self.documents[k].doc_type == doc_type
            }
        
        # Build results
        results = []
        for doc_id, score in sorted(doc_scores.items(), key=lambda x: -x[1]):
            if len(results) >= query.max_results:
                break
            
            doc = self.documents[doc_id]
            matched_sections = []
            
            if query.include_sections:
                for word in query_words:
                    if word in self.section_index:
                        for did, sidx in self.section_index[word]:
                            if did == doc_id and sidx < len(doc.sections):
                                matched_sections.append(doc.sections[sidx])
            
            # Generate highlights
            highlights = self._generate_highlights(doc.content, query_words)
            
            results.append(CodexSearchResult(
                document=doc,
                relevance_score=score / len(query_words) if query_words else 0,
                matched_sections=matched_sections[:5],
                highlights=highlights[:3]
            ))
        
        return results
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable words"""
        # Simple word tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter short words and stopwords
        stopwords = {'the', 'a', 'an', 'is', 'it', 'to', 'of', 'and', 'or', 'in', 'on', 'for'}
        return [w for w in words if len(w) > 2 and w not in stopwords]
    
    def _generate_highlights(self, content: str, query_words: List[str]) -> List[str]:
        """Generate highlighted snippets from content"""
        highlights = []
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in query_words):
                snippet = sentence.strip()[:200]
                if snippet:
                    highlights.append(snippet)
        
        return highlights


class CodexEditor:
    """
    Content editing system with version control.
    
    Provides:
    - Direct content editing
    - Version history
    - Undo/redo operations
    - Conflict detection
    """
    
    def __init__(self, index: CodexIndex):
        self.index = index
        self.edit_history: Dict[str, List[ContentEdit]] = {}  # doc_id -> edits
        self.undo_stack: Dict[str, List[ContentEdit]] = {}
    
    def edit(self, edit: ContentEdit) -> bool:
        """Apply an edit to a document"""
        if edit.document_id not in self.index.documents:
            logger.error(f"❌ Document not found: {edit.document_id}")
            return False
        
        doc = self.index.documents[edit.document_id]
        original_content = doc.content
        
        try:
            if edit.edit_type == 'replace':
                if edit.old_content and edit.new_content:
                    doc.content = doc.content.replace(edit.old_content, edit.new_content, 1)
                    
            elif edit.edit_type == 'insert':
                if edit.position is not None and edit.new_content:
                    doc.content = doc.content[:edit.position] + edit.new_content + doc.content[edit.position:]
                    
            elif edit.edit_type == 'delete':
                if edit.old_content:
                    doc.content = doc.content.replace(edit.old_content, '', 1)
                    
            elif edit.edit_type == 'append':
                if edit.new_content:
                    doc.content += edit.new_content
            
            # Update document metadata
            doc.version += 1
            doc.updated_at = datetime.utcnow().isoformat()
            
            # Re-index document
            self.index.remove_document(doc.id)
            self.index.add_document(doc)
            
            # Record edit
            if doc.id not in self.edit_history:
                self.edit_history[doc.id] = []
            self.edit_history[doc.id].append(edit)
            
            # Clear redo stack
            self.undo_stack[doc.id] = []
            
            logger.info(f"✏️ Applied edit to {doc.title} (v{doc.version})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Edit failed: {e}")
            doc.content = original_content
            return False
    
    def undo(self, doc_id: str) -> bool:
        """Undo the last edit on a document"""
        if doc_id not in self.edit_history or not self.edit_history[doc_id]:
            return False
        
        last_edit = self.edit_history[doc_id].pop()
        
        # Create reverse edit
        reverse_edit = ContentEdit(
            document_id=doc_id,
            edit_type='replace',
            old_content=last_edit.new_content,
            new_content=last_edit.old_content
        )
        
        # Store for redo
        if doc_id not in self.undo_stack:
            self.undo_stack[doc_id] = []
        self.undo_stack[doc_id].append(last_edit)
        
        # Apply reverse
        return self.edit(reverse_edit)
    
    def get_version_history(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get version history for a document"""
        if doc_id not in self.edit_history:
            return []
        
        return [asdict(edit) for edit in self.edit_history[doc_id]]


class CodexBrowser:
    """
    Documentation browsing interface.
    
    Provides:
    - Directory structure navigation
    - Document preview
    - Section navigation
    - Cross-references
    """
    
    def __init__(self, index: CodexIndex):
        self.index = index
        self.navigation_history: List[str] = []
        self.current_doc: Optional[str] = None
    
    def browse(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Browse documents at a path or get overview"""
        if path:
            # Filter documents by path
            docs = [
                d for d in self.index.documents.values()
                if d.path and d.path.startswith(path)
            ]
        else:
            docs = list(self.index.documents.values())
        
        # Organize by directory structure
        structure: Dict[str, Any] = {'documents': [], 'subdirs': {}}
        
        for doc in docs:
            if doc.path:
                parts = doc.path.split('/')
                current = structure
                for part in parts[:-1]:
                    if part not in current['subdirs']:
                        current['subdirs'][part] = {'documents': [], 'subdirs': {}}
                    current = current['subdirs'][part]
                current['documents'].append({
                    'id': doc.id,
                    'title': doc.title,
                    'doc_type': doc.doc_type,
                    'updated_at': doc.updated_at
                })
            else:
                structure['documents'].append({
                    'id': doc.id,
                    'title': doc.title,
                    'doc_type': doc.doc_type,
                    'updated_at': doc.updated_at
                })
        
        return structure
    
    def view_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """View a specific document"""
        if doc_id not in self.index.documents:
            return None
        
        doc = self.index.documents[doc_id]
        self.navigation_history.append(doc_id)
        self.current_doc = doc_id
        
        return {
            'document': asdict(doc),
            'section_count': len(doc.sections),
            'word_count': len(doc.content.split()),
            'version': doc.version
        }
    
    def get_sections(self, doc_id: str) -> List[Dict[str, Any]]:
        """Get all sections in a document"""
        if doc_id not in self.index.documents:
            return []
        return self.index.documents[doc_id].sections
    
    def navigate_back(self) -> Optional[str]:
        """Navigate to previous document"""
        if len(self.navigation_history) > 1:
            self.navigation_history.pop()
            self.current_doc = self.navigation_history[-1]
            return self.current_doc
        return None
    
    def find_references(self, doc_id: str) -> List[str]:
        """Find documents that reference this document"""
        if doc_id not in self.index.documents:
            return []
        
        doc = self.index.documents[doc_id]
        references = []
        
        # Search for references by title or id
        for other_id, other_doc in self.index.documents.items():
            if other_id != doc_id:
                if doc.title.lower() in other_doc.content.lower() or doc_id in other_doc.content:
                    references.append(other_id)
        
        return references


class CodexSystem:
    """
    Main Codex system integrating all components.
    
    Provides unified interface for:
    - Document management
    - Search and querying
    - Content editing
    - Browsing and navigation
    - Integration with reasoning workflows
    """
    
    def __init__(self, storage_path: str = ".forge_codex"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.index = CodexIndex()
        self.editor = CodexEditor(self.index)
        self.browser = CodexBrowser(self.index)
        
        # Load existing documents
        self._load_documents()
        
        logger.info("✅ Codex System initialized")
    
    def _load_documents(self):
        """Load documents from storage"""
        docs_file = self.storage_path / "documents.json"
        if docs_file.exists():
            try:
                with open(docs_file, 'r') as f:
                    data = json.load(f)
                    for doc_data in data.get('documents', []):
                        doc = CodexDocument(**doc_data)
                        self.index.add_document(doc)
                logger.info(f"📚 Loaded {len(self.index.documents)} documents")
            except Exception as e:
                logger.warning(f"⚠️ Could not load documents: {e}")
    
    def _save_documents(self):
        """Save documents to storage"""
        docs_file = self.storage_path / "documents.json"
        try:
            data = {
                'documents': [asdict(doc) for doc in self.index.documents.values()],
                'last_updated': datetime.utcnow().isoformat()
            }
            with open(docs_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Could not save documents: {e}")
    
    def add_document(
        self,
        title: str,
        content: str,
        doc_type: str = 'markdown',
        path: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> CodexDocument:
        """Add a new document to the Codex"""
        # Parse sections from content
        sections = self._parse_sections(content, doc_type)
        
        doc = CodexDocument(
            id="",
            title=title,
            content=content,
            doc_type=doc_type,
            path=path,
            tags=tags or [],
            sections=sections
        )
        
        self.index.add_document(doc)
        self._save_documents()
        
        return doc
    
    def _parse_sections(self, content: str, doc_type: str) -> List[Dict[str, Any]]:
        """Parse content into sections"""
        sections = []
        
        if doc_type == 'markdown':
            # Parse markdown headers
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                header_match = re.match(r'^(#+)\s+(.+)$', line)
                if header_match:
                    if current_section:
                        sections.append(current_section)
                    level = len(header_match.group(1))
                    title = header_match.group(2)
                    current_section = {
                        'level': level,
                        'title': title,
                        'content': ''
                    }
                elif current_section:
                    current_section['content'] += line + '\n'
            
            if current_section:
                sections.append(current_section)
                
        elif doc_type == 'code':
            # Parse code functions/classes
            # Simple pattern matching for Python
            patterns = [
                (r'^def\s+(\w+)', 'function'),
                (r'^class\s+(\w+)', 'class'),
                (r'^async\s+def\s+(\w+)', 'async_function')
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                for pattern, section_type in patterns:
                    match = re.match(pattern, line)
                    if match:
                        sections.append({
                            'type': section_type,
                            'name': match.group(1),
                            'line': i + 1,
                            'content': line
                        })
        
        return sections
    
    def search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        max_results: int = 10
    ) -> List[CodexSearchResult]:
        """Search the Codex"""
        q = CodexQuery(
            query=query,
            filters=filters or {},
            max_results=max_results
        )
        return self.index.search(q)
    
    def edit_document(
        self,
        doc_id: str,
        edit_type: str,
        old_content: Optional[str] = None,
        new_content: Optional[str] = None,
        position: Optional[int] = None
    ) -> bool:
        """Edit a document"""
        edit = ContentEdit(
            document_id=doc_id,
            edit_type=edit_type,
            old_content=old_content,
            new_content=new_content,
            position=position
        )
        result = self.editor.edit(edit)
        if result:
            self._save_documents()
        return result
    
    def browse(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Browse documents"""
        return self.browser.browse(path)
    
    def view(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """View a document"""
        return self.browser.view_document(doc_id)
    
    def import_directory(self, directory: str) -> int:
        """Import all documents from a directory"""
        imported = 0
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.error(f"❌ Directory not found: {directory}")
            return 0
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                try:
                    # Determine doc type
                    suffix = file_path.suffix.lower()
                    if suffix in ['.md', '.markdown']:
                        doc_type = 'markdown'
                    elif suffix in ['.py', '.js', '.ts', '.go', '.rs']:
                        doc_type = 'code'
                    elif suffix in ['.json', '.yaml', '.yml', '.toml']:
                        doc_type = 'config'
                    else:
                        doc_type = 'text'
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    relative_path = str(file_path.relative_to(dir_path))
                    self.add_document(
                        title=file_path.name,
                        content=content,
                        doc_type=doc_type,
                        path=relative_path
                    )
                    imported += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not import {file_path}: {e}")
        
        logger.info(f"📦 Imported {imported} documents from {directory}")
        return imported
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Codex statistics"""
        doc_types = {}
        total_content = 0
        
        for doc in self.index.documents.values():
            doc_types[doc.doc_type] = doc_types.get(doc.doc_type, 0) + 1
            total_content += len(doc.content)
        
        return {
            'total_documents': len(self.index.documents),
            'document_types': doc_types,
            'total_content_bytes': total_content,
            'indexed_words': len(self.index.word_index),
            'indexed_tags': len(self.index.tag_index)
        }
    
    def integrate_with_reasoning(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate Codex with reasoning workflows.
        
        Provides relevant documentation context for reasoning tasks.
        """
        # Search for relevant documents
        results = self.search(query, max_results=5)
        
        # Extract relevant sections
        relevant_content = []
        for result in results:
            relevant_content.append({
                'title': result.document.title,
                'type': result.document.doc_type,
                'relevance': result.relevance_score,
                'highlights': result.highlights,
                'sections': [s.get('title', s.get('name', '')) for s in result.matched_sections]
            })
        
        return {
            'query': query,
            'context': context,
            'codex_results': relevant_content,
            'total_relevant': len(results)
        }


# Global Codex instance
_codex_instance: Optional[CodexSystem] = None


def get_codex() -> CodexSystem:
    """Get or create the global Codex instance"""
    global _codex_instance
    if _codex_instance is None:
        _codex_instance = CodexSystem()
    return _codex_instance


def main():
    """Demo: Codex System for ChatGPT 2.0"""
    print("\n" + "=" * 60)
    print("📚 THE FORGE - Codex System for ChatGPT 2.0")
    print("=" * 60 + "\n")
    
    # Initialize Codex
    codex = get_codex()
    
    # Add some documents
    doc1 = codex.add_document(
        title="Video Editing Guide",
        content="""# Video Editing with THE FORGE

## Getting Started
Learn how to edit videos professionally.

## Timeline Management
Use the timeline for precise editing.

## Effects and Transitions
Apply professional effects to your videos.
""",
        doc_type='markdown',
        tags=['video', 'guide', 'tutorial']
    )
    print(f"Added document: {doc1.title} ({doc1.id})")
    
    doc2 = codex.add_document(
        title="Python Code Example",
        content="""
def process_video(input_path, output_path):
    '''Process a video file'''
    # Load video
    video = load_video(input_path)
    # Apply effects
    video = apply_effects(video)
    # Save output
    save_video(video, output_path)

class VideoEditor:
    '''Main video editor class'''
    def __init__(self):
        self.timeline = []
    
    def add_clip(self, clip):
        self.timeline.append(clip)
""",
        doc_type='code',
        tags=['python', 'video', 'example']
    )
    print(f"Added document: {doc2.title} ({doc2.id})")
    
    # Search
    print("\n📖 Searching for 'video editing':")
    results = codex.search("video editing")
    for r in results:
        print(f"  - {r.document.title} (relevance: {r.relevance_score:.2f})")
        if r.highlights:
            print(f"    Highlight: {r.highlights[0][:50]}...")
    
    # Edit document
    print("\n✏️ Editing document...")
    codex.edit_document(
        doc_id=doc1.id,
        edit_type='append',
        new_content="\n## Color Grading\nAdjust colors for cinematic look."
    )
    
    # View document
    print("\n👀 Viewing updated document:")
    view = codex.view(doc1.id)
    if view:
        print(f"  Title: {view['document']['title']}")
        print(f"  Version: {view['version']}")
        print(f"  Sections: {view['section_count']}")
    
    # Browse
    print("\n📂 Browsing documents:")
    structure = codex.browse()
    print(f"  Total documents: {len(structure['documents'])}")
    
    # Stats
    print("\n📊 Codex Statistics:")
    stats = codex.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Integration with reasoning
    print("\n🧠 Integration with reasoning workflow:")
    reasoning_result = codex.integrate_with_reasoning(
        query="How to edit video timeline?",
        context={'task': 'video_editing', 'user_level': 'beginner'}
    )
    print(f"  Found {reasoning_result['total_relevant']} relevant documents")
    
    print("\n" + "=" * 60)
    print("✅ Codex System Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

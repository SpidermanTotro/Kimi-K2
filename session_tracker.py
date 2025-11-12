#!/usr/bin/env python3
"""
Session Tracker - Tracks coding sessions, progress, and provides analytics
Remembers where you stopped, what you changed, and gives smart recommendations
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from typing import Dict, List, Optional, Tuple

class SessionTracker:
    """Tracks coding sessions and provides detailed analytics"""
    
    def __init__(self, db_path: str = "forge_sessions.db"):
        self.db_path = db_path
        self.current_session_id = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for session tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time REAL,
                end_time REAL,
                project_path TEXT,
                project_name TEXT,
                duration_seconds INTEGER,
                files_modified INTEGER,
                lines_added INTEGER,
                lines_deleted INTEGER,
                commits_made INTEGER,
                languages_used TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # File changes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_changes (
                change_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                file_path TEXT,
                timestamp REAL,
                change_type TEXT,
                lines_added INTEGER,
                lines_deleted INTEGER,
                file_hash TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Activity log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp REAL,
                activity_type TEXT,
                description TEXT,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp REAL,
                recommendation_type TEXT,
                title TEXT,
                description TEXT,
                priority INTEGER,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Session checkpoints (where you stopped)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp REAL,
                file_path TEXT,
                line_number INTEGER,
                cursor_position INTEGER,
                scroll_position INTEGER,
                open_files TEXT,
                notes TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Daily statistics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_sessions INTEGER,
                total_duration_seconds INTEGER,
                total_lines_added INTEGER,
                total_lines_deleted INTEGER,
                total_files_modified INTEGER,
                most_used_language TEXT,
                productivity_score REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def start_session(self, project_path: str, project_name: str = None) -> str:
        """Start a new coding session"""
        session_id = f"session_{int(time.time())}_{hashlib.md5(project_path.encode()).hexdigest()[:8]}"
        
        if project_name is None:
            project_name = Path(project_path).name
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (session_id, start_time, project_path, project_name, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (session_id, time.time(), project_path, project_name))
        
        # Log session start
        cursor.execute("""
            INSERT INTO activity_log (session_id, timestamp, activity_type, description)
            VALUES (?, ?, 'session_start', ?)
        """, (session_id, time.time(), f"Started working on {project_name}"))
        
        conn.commit()
        conn.close()
        
        self.current_session_id = session_id
        return session_id
    
    def log_file_change(self, file_path: str, change_type: str, 
                        lines_added: int = 0, lines_deleted: int = 0):
        """Log a file change"""
        if not self.current_session_id:
            return
        
        file_hash = self._get_file_hash(file_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO file_changes 
            (session_id, file_path, timestamp, change_type, lines_added, lines_deleted, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.current_session_id, file_path, time.time(), change_type, 
              lines_added, lines_deleted, file_hash))
        
        # Log activity
        cursor.execute("""
            INSERT INTO activity_log (session_id, timestamp, activity_type, description)
            VALUES (?, ?, 'file_change', ?)
        """, (self.current_session_id, time.time(), 
              f"{change_type}: {Path(file_path).name} (+{lines_added}/-{lines_deleted})"))
        
        conn.commit()
        conn.close()
    
    def save_checkpoint(self, file_path: str, line_number: int, 
                       cursor_position: int, scroll_position: int,
                       open_files: List[str], notes: str = ""):
        """Save a checkpoint - where you stopped working"""
        if not self.current_session_id:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO checkpoints 
            (session_id, timestamp, file_path, line_number, cursor_position, 
             scroll_position, open_files, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.current_session_id, time.time(), file_path, line_number,
              cursor_position, scroll_position, json.dumps(open_files), notes))
        
        conn.commit()
        conn.close()
    
    def get_last_checkpoint(self, session_id: str = None) -> Optional[Dict]:
        """Get the last checkpoint - resume where you left off"""
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id:
            # Get the most recent session
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id FROM sessions 
                ORDER BY start_time DESC LIMIT 1
            """)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                session_id = result[0]
            else:
                return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT file_path, line_number, cursor_position, scroll_position, 
                   open_files, notes, timestamp
            FROM checkpoints
            WHERE session_id = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'file_path': result[0],
                'line_number': result[1],
                'cursor_position': result[2],
                'scroll_position': result[3],
                'open_files': json.loads(result[4]) if result[4] else [],
                'notes': result[5],
                'timestamp': result[6],
                'time_ago': self._time_ago(result[6])
            }
        
        return None
    
    def end_session(self):
        """End the current session"""
        if not self.current_session_id:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate session statistics
        cursor.execute("""
            SELECT COUNT(DISTINCT file_path), 
                   SUM(lines_added), 
                   SUM(lines_deleted)
            FROM file_changes
            WHERE session_id = ?
        """, (self.current_session_id,))
        
        stats = cursor.fetchone()
        files_modified = stats[0] or 0
        lines_added = stats[1] or 0
        lines_deleted = stats[2] or 0
        
        # Update session
        cursor.execute("""
            UPDATE sessions
            SET end_time = ?,
                duration_seconds = end_time - start_time,
                files_modified = ?,
                lines_added = ?,
                lines_deleted = ?,
                status = 'completed'
            WHERE session_id = ?
        """, (time.time(), files_modified, lines_added, lines_deleted, 
              self.current_session_id))
        
        # Log session end
        cursor.execute("""
            INSERT INTO activity_log (session_id, timestamp, activity_type, description)
            VALUES (?, ?, 'session_end', ?)
        """, (self.current_session_id, time.time(), 
              f"Completed session: {files_modified} files, +{lines_added}/-{lines_deleted} lines"))
        
        conn.commit()
        conn.close()
        
        # Update daily stats
        self._update_daily_stats()
        
        self.current_session_id = None
    
    def add_recommendation(self, rec_type: str, title: str, 
                          description: str, priority: int = 1):
        """Add a smart recommendation"""
        if not self.current_session_id:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO recommendations 
            (session_id, timestamp, recommendation_type, title, description, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.current_session_id, time.time(), rec_type, title, description, priority))
        
        conn.commit()
        conn.close()
    
    def get_recommendations(self, status: str = 'pending') -> List[Dict]:
        """Get recommendations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT recommendation_type, title, description, priority, timestamp
            FROM recommendations
            WHERE status = ?
            ORDER BY priority DESC, timestamp DESC
            LIMIT 10
        """, (status,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'type': r[0],
            'title': r[1],
            'description': r[2],
            'priority': r[3],
            'time_ago': self._time_ago(r[4])
        } for r in results]
    
    def get_session_dashboard(self, session_id: str = None) -> Dict:
        """Get comprehensive session dashboard"""
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id:
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Session info
        cursor.execute("""
            SELECT project_name, start_time, end_time, duration_seconds,
                   files_modified, lines_added, lines_deleted, status
            FROM sessions WHERE session_id = ?
        """, (session_id,))
        
        session = cursor.fetchone()
        if not session:
            conn.close()
            return {}
        
        # Activity log
        cursor.execute("""
            SELECT timestamp, activity_type, description
            FROM activity_log
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 50
        """, (session_id,))
        
        activities = cursor.fetchall()
        
        # File changes
        cursor.execute("""
            SELECT file_path, change_type, lines_added, lines_deleted, timestamp
            FROM file_changes
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (session_id,))
        
        changes = cursor.fetchall()
        
        conn.close()
        
        return {
            'session_id': session_id,
            'project_name': session[0],
            'start_time': datetime.fromtimestamp(session[1]).strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.fromtimestamp(session[2]).strftime('%Y-%m-%d %H:%M:%S') if session[2] else 'In Progress',
            'duration': self._format_duration(session[3] if session[3] else time.time() - session[1]),
            'files_modified': session[4] or 0,
            'lines_added': session[5] or 0,
            'lines_deleted': session[6] or 0,
            'status': session[7],
            'activities': [{
                'time': datetime.fromtimestamp(a[0]).strftime('%H:%M:%S'),
                'type': a[1],
                'description': a[2]
            } for a in activities],
            'changes': [{
                'file': Path(c[0]).name,
                'type': c[1],
                'lines_added': c[2],
                'lines_deleted': c[3],
                'time': self._time_ago(c[4])
            } for c in changes]
        }
    
    def get_changelog(self, days: int = 7) -> List[Dict]:
        """Get changelog for the last N days"""
        cutoff = time.time() - (days * 86400)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.session_id, s.project_name, s.start_time, s.end_time,
                   s.files_modified, s.lines_added, s.lines_deleted
            FROM sessions s
            WHERE s.start_time > ?
            ORDER BY s.start_time DESC
        """, (cutoff,))
        
        sessions = cursor.fetchall()
        conn.close()
        
        changelog = []
        for session in sessions:
            changelog.append({
                'session_id': session[0],
                'project': session[1],
                'date': datetime.fromtimestamp(session[2]).strftime('%Y-%m-%d'),
                'time': datetime.fromtimestamp(session[2]).strftime('%H:%M'),
                'duration': self._format_duration(
                    (session[3] - session[2]) if session[3] else 0
                ),
                'files': session[4] or 0,
                'added': session[5] or 0,
                'deleted': session[6] or 0
            })
        
        return changelog
    
    def get_daily_stats(self, days: int = 7) -> Dict:
        """Get daily statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate stats for last N days
        cutoff = time.time() - (days * 86400)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as sessions,
                SUM(duration_seconds) as total_duration,
                SUM(files_modified) as total_files,
                SUM(lines_added) as total_added,
                SUM(lines_deleted) as total_deleted
            FROM sessions
            WHERE start_time > ? AND status = 'completed'
        """, (cutoff,))
        
        stats = cursor.fetchone()
        
        # Get daily breakdown
        cursor.execute("""
            SELECT 
                date(start_time, 'unixepoch') as day,
                COUNT(*) as sessions,
                SUM(duration_seconds) as duration,
                SUM(lines_added) as added,
                SUM(lines_deleted) as deleted
            FROM sessions
            WHERE start_time > ?
            GROUP BY day
            ORDER BY day DESC
        """, (cutoff,))
        
        daily = cursor.fetchall()
        
        conn.close()
        
        return {
            'summary': {
                'total_sessions': stats[0] or 0,
                'total_duration': self._format_duration(stats[1] or 0),
                'total_files': stats[2] or 0,
                'total_lines_added': stats[3] or 0,
                'total_lines_deleted': stats[4] or 0,
                'avg_session_duration': self._format_duration(
                    (stats[1] // stats[0]) if stats[0] else 0
                )
            },
            'daily': [{
                'date': d[0],
                'sessions': d[1],
                'duration': self._format_duration(d[2]),
                'lines_changed': (d[3] or 0) + (d[4] or 0)
            } for d in daily]
        }
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get file content hash"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def _time_ago(self, timestamp: float) -> str:
        """Convert timestamp to human-readable 'time ago'"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return f"{int(diff)}s ago"
        elif diff < 3600:
            return f"{int(diff/60)}m ago"
        elif diff < 86400:
            return f"{int(diff/3600)}h ago"
        else:
            return f"{int(diff/86400)}d ago"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m {int(seconds%60)}s"
        else:
            h = int(seconds / 3600)
            m = int((seconds % 3600) / 60)
            return f"{h}h {m}m"
    
    def _update_daily_stats(self):
        """Update daily statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*),
                SUM(duration_seconds),
                SUM(lines_added),
                SUM(lines_deleted),
                SUM(files_modified)
            FROM sessions
            WHERE date(start_time, 'unixepoch') = ?
        """, (today,))
        
        stats = cursor.fetchone()
        
        cursor.execute("""
            INSERT OR REPLACE INTO daily_stats
            (date, total_sessions, total_duration_seconds, total_lines_added,
             total_lines_deleted, total_files_modified, productivity_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (today, stats[0], stats[1] or 0, stats[2] or 0, stats[3] or 0,
              stats[4] or 0, self._calculate_productivity_score(stats)))
        
        conn.commit()
        conn.close()
    
    def _calculate_productivity_score(self, stats: Tuple) -> float:
        """Calculate productivity score (0-100)"""
        sessions = stats[0] or 0
        duration = stats[1] or 0
        lines_added = stats[2] or 0
        files = stats[4] or 0
        
        # Simple productivity formula
        if sessions == 0:
            return 0.0
        
        # Points for consistent work
        session_score = min(sessions * 10, 30)
        
        # Points for time spent (optimal: 4-6 hours)
        hours = duration / 3600
        time_score = min(hours * 10, 30) if hours <= 6 else max(30 - (hours - 6) * 5, 0)
        
        # Points for output
        output_score = min((lines_added / 100) * 20, 20)
        
        # Points for activity
        activity_score = min(files * 4, 20)
        
        return min(session_score + time_score + output_score + activity_score, 100)


if __name__ == "__main__":
    # Demo usage
    tracker = SessionTracker()
    
    print("🎯 Session Tracker Demo\n")
    
    # Start session
    session_id = tracker.start_session("/home/user/project", "My Project")
    print(f"✅ Session started: {session_id}\n")
    
    # Simulate some work
    tracker.log_file_change("src/main.py", "modified", 25, 10)
    tracker.log_file_change("src/utils.py", "created", 50, 0)
    tracker.add_recommendation("testing", "Add unit tests", 
                              "Consider adding tests for new functions", 3)
    
    # Save checkpoint
    tracker.save_checkpoint("src/main.py", 42, 150, 500, 
                           ["src/main.py", "src/utils.py"],
                           "Working on authentication feature")
    
    # Get dashboard
    dashboard = tracker.get_session_dashboard()
    print("📊 Current Session Dashboard:")
    print(f"  Project: {dashboard['project_name']}")
    print(f"  Duration: {dashboard['duration']}")
    print(f"  Files: {dashboard['files_modified']}")
    print(f"  Lines: +{dashboard['lines_added']}/-{dashboard['lines_deleted']}")
    print()
    
    # Get last checkpoint
    checkpoint = tracker.get_last_checkpoint()
    if checkpoint:
        print("🔖 Last Checkpoint (Resume from here):")
        print(f"  File: {checkpoint['file_path']}")
        print(f"  Line: {checkpoint['line_number']}")
        print(f"  Notes: {checkpoint['notes']}")
        print(f"  Saved: {checkpoint['time_ago']}")
        print()
    
    # Get recommendations
    recs = tracker.get_recommendations()
    if recs:
        print("💡 Recommendations:")
        for rec in recs:
            print(f"  • {rec['title']} ({rec['type']}, priority: {rec['priority']})")
        print()
    
    # End session
    tracker.end_session()
    print("✅ Session ended\n")
    
    # Get stats
    stats = tracker.get_daily_stats(7)
    print("📈 Last 7 Days Statistics:")
    print(f"  Total Sessions: {stats['summary']['total_sessions']}")
    print(f"  Total Duration: {stats['summary']['total_duration']}")
    print(f"  Total Lines: +{stats['summary']['total_lines_added']}/-{stats['summary']['total_lines_deleted']}")
    print()
    
    # Get changelog
    changelog = tracker.get_changelog(7)
    if changelog:
        print("📝 Recent Changelog:")
        for entry in changelog[:5]:
            print(f"  {entry['date']} {entry['time']} - {entry['project']}: {entry['files']} files, +{entry['added']}/-{entry['deleted']}")

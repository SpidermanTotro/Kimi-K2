// Session Tracker - JavaScript/TypeScript/Node.js Version
// Tracks coding sessions, progress, and provides analytics

const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

class SessionTracker {
    constructor(dbPath = 'forge_sessions.db') {
        this.dbPath = dbPath;
        this.currentSessionId = null;
        this.db = new sqlite3.Database(dbPath);
        this.initDatabase();
    }

    initDatabase() {
        this.db.serialize(() => {
            // Sessions table
            this.db.run(`
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
            `);

            // File changes table
            this.db.run(`
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
            `);

            // Activity log table
            this.db.run(`
                CREATE TABLE IF NOT EXISTS activity_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp REAL,
                    activity_type TEXT,
                    description TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            `);

            // Checkpoints table
            this.db.run(`
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
            `);
        });
    }

    startSession(projectPath, projectName = null) {
        const timestamp = Date.now() / 1000;
        const hash = crypto.createHash('md5').update(projectPath).digest('hex').substring(0, 8);
        const sessionId = `session_${Math.floor(timestamp)}_${hash}`;
        
        if (!projectName) {
            projectName = path.basename(projectPath);
        }

        this.db.run(`
            INSERT INTO sessions (session_id, start_time, project_path, project_name, status)
            VALUES (?, ?, ?, ?, 'active')
        `, [sessionId, timestamp, projectPath, projectName]);

        this.db.run(`
            INSERT INTO activity_log (session_id, timestamp, activity_type, description)
            VALUES (?, ?, 'session_start', ?)
        `, [sessionId, timestamp, `Started working on ${projectName}`]);

        this.currentSessionId = sessionId;
        return sessionId;
    }

    logFileChange(filePath, changeType, linesAdded = 0, linesDeleted = 0) {
        if (!this.currentSessionId) return;

        const timestamp = Date.now() / 1000;
        const fileHash = this.getFileHash(filePath);

        this.db.run(`
            INSERT INTO file_changes 
            (session_id, file_path, timestamp, change_type, lines_added, lines_deleted, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `, [this.currentSessionId, filePath, timestamp, changeType, linesAdded, linesDeleted, fileHash]);

        this.db.run(`
            INSERT INTO activity_log (session_id, timestamp, activity_type, description)
            VALUES (?, ?, 'file_change', ?)
        `, [this.currentSessionId, timestamp, 
            `${changeType}: ${path.basename(filePath)} (+${linesAdded}/-${linesDeleted})`]);
    }

    saveCheckpoint(filePath, lineNumber, cursorPosition, scrollPosition, openFiles, notes = '') {
        if (!this.currentSessionId) return;

        const timestamp = Date.now() / 1000;

        this.db.run(`
            INSERT INTO checkpoints 
            (session_id, timestamp, file_path, line_number, cursor_position, 
             scroll_position, open_files, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `, [this.currentSessionId, timestamp, filePath, lineNumber, cursorPosition, 
            scrollPosition, JSON.stringify(openFiles), notes]);

        console.log(`✅ Checkpoint saved: ${path.basename(filePath)}:${lineNumber}`);
    }

    getLastCheckpoint(callback) {
        const sessionId = this.currentSessionId;

        this.db.get(`
            SELECT file_path, line_number, cursor_position, scroll_position, 
                   open_files, notes, timestamp
            FROM checkpoints
            WHERE session_id = ?
            ORDER BY timestamp DESC LIMIT 1
        `, [sessionId], (err, row) => {
            if (err || !row) {
                callback(null);
                return;
            }

            callback({
                filePath: row.file_path,
                lineNumber: row.line_number,
                cursorPosition: row.cursor_position,
                scrollPosition: row.scroll_position,
                openFiles: JSON.parse(row.open_files || '[]'),
                notes: row.notes,
                timestamp: row.timestamp,
                timeAgo: this.timeAgo(row.timestamp)
            });
        });
    }

    endSession() {
        if (!this.currentSessionId) return;

        const timestamp = Date.now() / 1000;

        this.db.get(`
            SELECT COUNT(DISTINCT file_path) as files, 
                   SUM(lines_added) as added, 
                   SUM(lines_deleted) as deleted
            FROM file_changes
            WHERE session_id = ?
        `, [this.currentSessionId], (err, stats) => {
            const filesModified = stats?.files || 0;
            const linesAdded = stats?.added || 0;
            const linesDeleted = stats?.deleted || 0;

            this.db.run(`
                UPDATE sessions
                SET end_time = ?,
                    duration_seconds = ? - start_time,
                    files_modified = ?,
                    lines_added = ?,
                    lines_deleted = ?,
                    status = 'completed'
                WHERE session_id = ?
            `, [timestamp, timestamp, filesModified, linesAdded, linesDeleted, this.currentSessionId]);

            console.log(`✅ Session ended: ${filesModified} files, +${linesAdded}/-${linesDeleted} lines`);
            this.currentSessionId = null;
        });
    }

    getSessionDashboard(callback) {
        if (!this.currentSessionId) {
            callback({});
            return;
        }

        this.db.get(`
            SELECT project_name, start_time, end_time, duration_seconds,
                   files_modified, lines_added, lines_deleted, status
            FROM sessions WHERE session_id = ?
        `, [this.currentSessionId], (err, session) => {
            if (err || !session) {
                callback({});
                return;
            }

            this.db.all(`
                SELECT timestamp, activity_type, description
                FROM activity_log
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT 50
            `, [this.currentSessionId], (err, activities) => {
                callback({
                    sessionId: this.currentSessionId,
                    projectName: session.project_name,
                    startTime: new Date(session.start_time * 1000).toLocaleString(),
                    duration: this.formatDuration(session.duration_seconds || (Date.now()/1000 - session.start_time)),
                    filesModified: session.files_modified || 0,
                    linesAdded: session.lines_added || 0,
                    linesDeleted: session.lines_deleted || 0,
                    status: session.status,
                    activities: (activities || []).map(a => ({
                        time: new Date(a.timestamp * 1000).toLocaleTimeString(),
                        type: a.activity_type,
                        description: a.description
                    }))
                });
            });
        });
    }

    getFileHash(filePath) {
        try {
            const content = fs.readFileSync(filePath);
            return crypto.createHash('md5').update(content).digest('hex');
        } catch {
            return '';
        }
    }

    timeAgo(timestamp) {
        const diff = Date.now() / 1000 - timestamp;
        if (diff < 60) return `${Math.floor(diff)}s ago`;
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return `${Math.floor(diff / 86400)}d ago`;
    }

    formatDuration(seconds) {
        if (seconds < 60) return `${Math.floor(seconds)}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        return `${h}h ${m}m`;
    }

    close() {
        this.db.close();
    }
}

// Demo usage
if (require.main === module) {
    console.log('🎯 Session Tracker Demo (JavaScript)\n');

    const tracker = new SessionTracker();
    
    const sessionId = tracker.startSession('/home/user/project', 'My Project');
    console.log(`✅ Session started: ${sessionId}\n`);
    
    tracker.logFileChange('src/main.js', 'modified', 25, 10);
    tracker.logFileChange('src/utils.js', 'created', 50, 0);
    
    tracker.saveCheckpoint('src/main.js', 42, 150, 500, 
                          ['src/main.js', 'src/utils.js'],
                          'Working on authentication feature');
    
    setTimeout(() => {
        tracker.getSessionDashboard(dashboard => {
            console.log('📊 Current Session Dashboard:');
            console.log(`  Project: ${dashboard.projectName}`);
            console.log(`  Duration: ${dashboard.duration}`);
            console.log(`  Files: ${dashboard.filesModified}`);
            console.log(`  Lines: +${dashboard.linesAdded}/-${dashboard.linesDeleted}\n`);
        });

        tracker.getLastCheckpoint(checkpoint => {
            if (checkpoint) {
                console.log('🔖 Last Checkpoint:');
                console.log(`  File: ${checkpoint.filePath}`);
                console.log(`  Line: ${checkpoint.lineNumber}`);
                console.log(`  Notes: ${checkpoint.notes}\n`);
            }
        });

        tracker.endSession();
        tracker.close();
    }, 100);
}

module.exports = SessionTracker;

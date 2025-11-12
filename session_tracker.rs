// Session Tracker - Rust Version
// Tracks coding sessions, progress, and provides analytics

use rusqlite::{Connection, params};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use std::path::Path;
use std::fs;
use md5;

#[derive(Debug, Serialize, Deserialize)]
pub struct SessionInfo {
    pub session_id: String,
    pub project_name: String,
    pub start_time: String,
    pub duration: String,
    pub files_modified: i64,
    pub lines_added: i64,
    pub lines_deleted: i64,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Checkpoint {
    pub file_path: String,
    pub line_number: i64,
    pub cursor_position: i64,
    pub scroll_position: i64,
    pub open_files: Vec<String>,
    pub notes: String,
    pub time_ago: String,
}

pub struct SessionTracker {
    conn: Connection,
    current_session_id: Option<String>,
}

impl SessionTracker {
    pub fn new(db_path: &str) -> Result<Self, rusqlite::Error> {
        let conn = Connection::open(db_path)?;
        let mut tracker = SessionTracker {
            conn,
            current_session_id: None,
        };
        tracker.init_database()?;
        Ok(tracker)
    }

    fn init_database(&mut self) -> Result<(), rusqlite::Error> {
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time REAL,
                end_time REAL,
                project_path TEXT,
                project_name TEXT,
                duration_seconds INTEGER,
                files_modified INTEGER,
                lines_added INTEGER,
                lines_deleted INTEGER,
                status TEXT DEFAULT 'active'
            )",
            [],
        )?;

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS file_changes (
                change_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                file_path TEXT,
                timestamp REAL,
                change_type TEXT,
                lines_added INTEGER,
                lines_deleted INTEGER,
                file_hash TEXT
            )",
            [],
        )?;

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS activity_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp REAL,
                activity_type TEXT,
                description TEXT
            )",
            [],
        )?;

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp REAL,
                file_path TEXT,
                line_number INTEGER,
                cursor_position INTEGER,
                scroll_position INTEGER,
                open_files TEXT,
                notes TEXT
            )",
            [],
        )?;

        Ok(())
    }

    pub fn start_session(&mut self, project_path: &str, project_name: Option<&str>) -> Result<String, rusqlite::Error> {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();

        let hash = format!("{:x}", md5::compute(project_path.as_bytes()));
        let session_id = format!("session_{}_{}", timestamp as u64, &hash[..8]);

        let name = project_name.unwrap_or_else(|| {
            Path::new(project_path)
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("Unknown")
        });

        self.conn.execute(
            "INSERT INTO sessions (session_id, start_time, project_path, project_name, status)
             VALUES (?1, ?2, ?3, ?4, 'active')",
            params![&session_id, timestamp, project_path, name],
        )?;

        self.conn.execute(
            "INSERT INTO activity_log (session_id, timestamp, activity_type, description)
             VALUES (?1, ?2, 'session_start', ?3)",
            params![&session_id, timestamp, format!("Started working on {}", name)],
        )?;

        self.current_session_id = Some(session_id.clone());
        println!("✅ Session started: {}", session_id);
        Ok(session_id)
    }

    pub fn log_file_change(&self, file_path: &str, change_type: &str, 
                           lines_added: i64, lines_deleted: i64) -> Result<(), rusqlite::Error> {
        if let Some(ref session_id) = self.current_session_id {
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs_f64();

            let file_hash = self.get_file_hash(file_path);

            self.conn.execute(
                "INSERT INTO file_changes 
                 (session_id, file_path, timestamp, change_type, lines_added, lines_deleted, file_hash)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
                params![session_id, file_path, timestamp, change_type, lines_added, lines_deleted, file_hash],
            )?;

            let file_name = Path::new(file_path)
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or("");

            self.conn.execute(
                "INSERT INTO activity_log (session_id, timestamp, activity_type, description)
                 VALUES (?1, ?2, 'file_change', ?3)",
                params![session_id, timestamp, 
                    format!("{}: {} (+{}/- {})", change_type, file_name, lines_added, lines_deleted)],
            )?;
        }
        Ok(())
    }

    pub fn save_checkpoint(&self, file_path: &str, line_number: i64, 
                          cursor_position: i64, scroll_position: i64,
                          open_files: &[String], notes: &str) -> Result<(), rusqlite::Error> {
        if let Some(ref session_id) = self.current_session_id {
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs_f64();

            let open_files_json = serde_json::to_string(open_files).unwrap_or_default();

            self.conn.execute(
                "INSERT INTO checkpoints 
                 (session_id, timestamp, file_path, line_number, cursor_position, 
                  scroll_position, open_files, notes)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
                params![session_id, timestamp, file_path, line_number, cursor_position,
                       scroll_position, open_files_json, notes],
            )?;

            println!("✅ Checkpoint saved: {}:{}", file_path, line_number);
        }
        Ok(())
    }

    pub fn get_last_checkpoint(&self) -> Result<Option<Checkpoint>, rusqlite::Error> {
        if let Some(ref session_id) = self.current_session_id {
            let mut stmt = self.conn.prepare(
                "SELECT file_path, line_number, cursor_position, scroll_position, 
                        open_files, notes, timestamp
                 FROM checkpoints
                 WHERE session_id = ?1
                 ORDER BY timestamp DESC LIMIT 1"
            )?;

            let checkpoint = stmt.query_row(params![session_id], |row| {
                let timestamp: f64 = row.get(6)?;
                let open_files_json: String = row.get(4)?;
                let open_files: Vec<String> = serde_json::from_str(&open_files_json)
                    .unwrap_or_default();

                Ok(Checkpoint {
                    file_path: row.get(0)?,
                    line_number: row.get(1)?,
                    cursor_position: row.get(2)?,
                    scroll_position: row.get(3)?,
                    open_files,
                    notes: row.get(5)?,
                    time_ago: Self::time_ago(timestamp),
                })
            }).optional()?;

            return Ok(checkpoint);
        }
        Ok(None)
    }

    pub fn end_session(&mut self) -> Result<(), rusqlite::Error> {
        if let Some(ref session_id) = self.current_session_id {
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs_f64();

            let mut stmt = self.conn.prepare(
                "SELECT COUNT(DISTINCT file_path), SUM(lines_added), SUM(lines_deleted)
                 FROM file_changes WHERE session_id = ?1"
            )?;

            let stats: (i64, i64, i64) = stmt.query_row(params![session_id], |row| {
                Ok((
                    row.get(0).unwrap_or(0),
                    row.get(1).unwrap_or(0),
                    row.get(2).unwrap_or(0),
                ))
            })?;

            self.conn.execute(
                "UPDATE sessions
                 SET end_time = ?1,
                     duration_seconds = ?1 - start_time,
                     files_modified = ?2,
                     lines_added = ?3,
                     lines_deleted = ?4,
                     status = 'completed'
                 WHERE session_id = ?5",
                params![timestamp, stats.0, stats.1, stats.2, session_id],
            )?;

            println!("✅ Session ended: {} files, +{}/- {} lines", stats.0, stats.1, stats.2);
            self.current_session_id = None;
        }
        Ok(())
    }

    fn get_file_hash(&self, file_path: &str) -> String {
        match fs::read(file_path) {
            Ok(content) => format!("{:x}", md5::compute(&content)),
            Err(_) => String::new(),
        }
    }

    fn time_ago(timestamp: f64) -> String {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();
        
        let diff = now - timestamp;
        
        if diff < 60.0 {
            format!("{}s ago", diff as i64)
        } else if diff < 3600.0 {
            format!("{}m ago", (diff / 60.0) as i64)
        } else if diff < 86400.0 {
            format!("{}h ago", (diff / 3600.0) as i64)
        } else {
            format!("{}d ago", (diff / 86400.0) as i64)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_session_tracking() {
        let mut tracker = SessionTracker::new(":memory:").unwrap();
        
        let session_id = tracker.start_session("/test/project", Some("Test")).unwrap();
        assert!(!session_id.is_empty());
        
        tracker.log_file_change("test.rs", "modified", 10, 5).unwrap();
        tracker.save_checkpoint("test.rs", 42, 100, 200, &vec!["test.rs".to_string()], "Test note").unwrap();
        
        let checkpoint = tracker.get_last_checkpoint().unwrap();
        assert!(checkpoint.is_some());
        
        tracker.end_session().unwrap();
    }
}

fn main() {
    println!("🎯 Session Tracker Demo (Rust)\n");
    
    let mut tracker = SessionTracker::new("forge_sessions.db").unwrap();
    
    let session_id = tracker.start_session("/home/user/project", Some("My Project")).unwrap();
    println!();
    
    tracker.log_file_change("src/main.rs", "modified", 25, 10).unwrap();
    tracker.log_file_change("src/utils.rs", "created", 50, 0).unwrap();
    
    tracker.save_checkpoint("src/main.rs", 42, 150, 500,
                           &vec!["src/main.rs".to_string(), "src/utils.rs".to_string()],
                           "Working on authentication feature").unwrap();
    println!();
    
    if let Ok(Some(checkpoint)) = tracker.get_last_checkpoint() {
        println!("🔖 Last Checkpoint:");
        println!("  File: {}", checkpoint.file_path);
        println!("  Line: {}", checkpoint.line_number);
        println!("  Notes: {}", checkpoint.notes);
        println!("  Saved: {}\n", checkpoint.time_ago);
    }
    
    tracker.end_session().unwrap();
}

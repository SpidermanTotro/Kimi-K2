// Session Tracker - Go Version
// Tracks coding sessions, progress, and provides analytics

package main

import (
	"crypto/md5"
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"path/filepath"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type SessionTracker struct {
	db               *sql.DB
	currentSessionID *string
}

type Checkpoint struct {
	FilePath       string   `json:"file_path"`
	LineNumber     int      `json:"line_number"`
	CursorPosition int      `json:"cursor_position"`
	ScrollPosition int      `json:"scroll_position"`
	OpenFiles      []string `json:"open_files"`
	Notes          string   `json:"notes"`
	TimeAgo        string   `json:"time_ago"`
}

type SessionInfo struct {
	SessionID     string `json:"session_id"`
	ProjectName   string `json:"project_name"`
	StartTime     string `json:"start_time"`
	Duration      string `json:"duration"`
	FilesModified int    `json:"files_modified"`
	LinesAdded    int    `json:"lines_added"`
	LinesDeleted  int    `json:"lines_deleted"`
	Status        string `json:"status"`
}

func NewSessionTracker(dbPath string) (*SessionTracker, error) {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, err
	}

	tracker := &SessionTracker{db: db}
	if err := tracker.initDatabase(); err != nil {
		return nil, err
	}

	return tracker, nil
}

func (st *SessionTracker) initDatabase() error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS sessions (
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
		)`,
		`CREATE TABLE IF NOT EXISTS file_changes (
			change_id INTEGER PRIMARY KEY AUTOINCREMENT,
			session_id TEXT,
			file_path TEXT,
			timestamp REAL,
			change_type TEXT,
			lines_added INTEGER,
			lines_deleted INTEGER,
			file_hash TEXT
		)`,
		`CREATE TABLE IF NOT EXISTS activity_log (
			log_id INTEGER PRIMARY KEY AUTOINCREMENT,
			session_id TEXT,
			timestamp REAL,
			activity_type TEXT,
			description TEXT
		)`,
		`CREATE TABLE IF NOT EXISTS checkpoints (
			checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
			session_id TEXT,
			timestamp REAL,
			file_path TEXT,
			line_number INTEGER,
			cursor_position INTEGER,
			scroll_position INTEGER,
			open_files TEXT,
			notes TEXT
		)`,
	}

	for _, query := range queries {
		if _, err := st.db.Exec(query); err != nil {
			return err
		}
	}

	return nil
}

func (st *SessionTracker) StartSession(projectPath, projectName string) (string, error) {
	timestamp := float64(time.Now().Unix())
	hash := fmt.Sprintf("%x", md5.Sum([]byte(projectPath)))
	sessionID := fmt.Sprintf("session_%d_%s", int(timestamp), hash[:8])

	if projectName == "" {
		projectName = filepath.Base(projectPath)
	}

	_, err := st.db.Exec(`
		INSERT INTO sessions (session_id, start_time, project_path, project_name, status)
		VALUES (?, ?, ?, ?, 'active')
	`, sessionID, timestamp, projectPath, projectName)
	if err != nil {
		return "", err
	}

	_, err = st.db.Exec(`
		INSERT INTO activity_log (session_id, timestamp, activity_type, description)
		VALUES (?, ?, 'session_start', ?)
	`, sessionID, timestamp, fmt.Sprintf("Started working on %s", projectName))
	if err != nil {
		return "", err
	}

	st.currentSessionID = &sessionID
	fmt.Printf("✅ Session started: %s\n", sessionID)
	return sessionID, nil
}

func (st *SessionTracker) LogFileChange(filePath, changeType string, linesAdded, linesDeleted int) error {
	if st.currentSessionID == nil {
		return nil
	}

	timestamp := float64(time.Now().Unix())
	fileHash := st.getFileHash(filePath)

	_, err := st.db.Exec(`
		INSERT INTO file_changes 
		(session_id, file_path, timestamp, change_type, lines_added, lines_deleted, file_hash)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	`, *st.currentSessionID, filePath, timestamp, changeType, linesAdded, linesDeleted, fileHash)
	if err != nil {
		return err
	}

	fileName := filepath.Base(filePath)
	_, err = st.db.Exec(`
		INSERT INTO activity_log (session_id, timestamp, activity_type, description)
		VALUES (?, ?, 'file_change', ?)
	`, *st.currentSessionID, timestamp,
		fmt.Sprintf("%s: %s (+%d/-%d)", changeType, fileName, linesAdded, linesDeleted))

	return err
}

func (st *SessionTracker) SaveCheckpoint(filePath string, lineNumber, cursorPosition, scrollPosition int,
	openFiles []string, notes string) error {
	if st.currentSessionID == nil {
		return nil
	}

	timestamp := float64(time.Now().Unix())
	openFilesJSON, _ := json.Marshal(openFiles)

	_, err := st.db.Exec(`
		INSERT INTO checkpoints 
		(session_id, timestamp, file_path, line_number, cursor_position, 
		 scroll_position, open_files, notes)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	`, *st.currentSessionID, timestamp, filePath, lineNumber, cursorPosition,
		scrollPosition, string(openFilesJSON), notes)

	if err == nil {
		fmt.Printf("✅ Checkpoint saved: %s:%d\n", filePath, lineNumber)
	}

	return err
}

func (st *SessionTracker) GetLastCheckpoint() (*Checkpoint, error) {
	if st.currentSessionID == nil {
		return nil, nil
	}

	var filePath, notes, openFilesJSON string
	var lineNumber, cursorPosition, scrollPosition int
	var timestamp float64

	err := st.db.QueryRow(`
		SELECT file_path, line_number, cursor_position, scroll_position, 
		       open_files, notes, timestamp
		FROM checkpoints
		WHERE session_id = ?
		ORDER BY timestamp DESC LIMIT 1
	`, *st.currentSessionID).Scan(&filePath, &lineNumber, &cursorPosition,
		&scrollPosition, &openFilesJSON, &notes, &timestamp)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	var openFiles []string
	json.Unmarshal([]byte(openFilesJSON), &openFiles)

	return &Checkpoint{
		FilePath:       filePath,
		LineNumber:     lineNumber,
		CursorPosition: cursorPosition,
		ScrollPosition: scrollPosition,
		OpenFiles:      openFiles,
		Notes:          notes,
		TimeAgo:        timeAgo(timestamp),
	}, nil
}

func (st *SessionTracker) EndSession() error {
	if st.currentSessionID == nil {
		return nil
	}

	timestamp := float64(time.Now().Unix())

	var filesModified, linesAdded, linesDeleted int
	err := st.db.QueryRow(`
		SELECT COUNT(DISTINCT file_path), 
		       COALESCE(SUM(lines_added), 0), 
		       COALESCE(SUM(lines_deleted), 0)
		FROM file_changes
		WHERE session_id = ?
	`, *st.currentSessionID).Scan(&filesModified, &linesAdded, &linesDeleted)

	if err != nil {
		return err
	}

	_, err = st.db.Exec(`
		UPDATE sessions
		SET end_time = ?,
		    duration_seconds = ? - start_time,
		    files_modified = ?,
		    lines_added = ?,
		    lines_deleted = ?,
		    status = 'completed'
		WHERE session_id = ?
	`, timestamp, timestamp, filesModified, linesAdded, linesDeleted, *st.currentSessionID)

	if err == nil {
		fmt.Printf("✅ Session ended: %d files, +%d/-%d lines\n",
			filesModified, linesAdded, linesDeleted)
		st.currentSessionID = nil
	}

	return err
}

func (st *SessionTracker) getFileHash(filePath string) string {
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		return ""
	}
	return fmt.Sprintf("%x", md5.Sum(content))
}

func (st *SessionTracker) Close() error {
	return st.db.Close()
}

func timeAgo(timestamp float64) string {
	diff := float64(time.Now().Unix()) - timestamp

	if diff < 60 {
		return fmt.Sprintf("%ds ago", int(diff))
	} else if diff < 3600 {
		return fmt.Sprintf("%dm ago", int(diff/60))
	} else if diff < 86400 {
		return fmt.Sprintf("%dh ago", int(diff/3600))
	}
	return fmt.Sprintf("%dd ago", int(diff/86400))
}

func main() {
	fmt.Println("🎯 Session Tracker Demo (Go)\n")

	tracker, err := NewSessionTracker("forge_sessions.db")
	if err != nil {
		panic(err)
	}
	defer tracker.Close()

	sessionID, _ := tracker.StartSession("/home/user/project", "My Project")
	fmt.Println()

	tracker.LogFileChange("src/main.go", "modified", 25, 10)
	tracker.LogFileChange("src/utils.go", "created", 50, 0)

	tracker.SaveCheckpoint("src/main.go", 42, 150, 500,
		[]string{"src/main.go", "src/utils.go"},
		"Working on authentication feature")
	fmt.Println()

	checkpoint, _ := tracker.GetLastCheckpoint()
	if checkpoint != nil {
		fmt.Println("🔖 Last Checkpoint:")
		fmt.Printf("  File: %s\n", checkpoint.FilePath)
		fmt.Printf("  Line: %d\n", checkpoint.LineNumber)
		fmt.Printf("  Notes: %s\n", checkpoint.Notes)
		fmt.Printf("  Saved: %s\n\n", checkpoint.TimeAgo)
	}

	tracker.EndSession()
}

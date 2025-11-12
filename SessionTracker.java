// Session Tracker - Java Version
// Tracks coding sessions, progress, and provides analytics

import java.sql.*;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.io.File;

public class SessionTracker {
    private Connection conn;
    private String currentSessionId;

    public SessionTracker(String dbPath) throws SQLException {
        conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath);
        initDatabase();
    }

    private void initDatabase() throws SQLException {
        String[] queries = {
            "CREATE TABLE IF NOT EXISTS sessions (" +
            "session_id TEXT PRIMARY KEY, " +
            "start_time REAL, " +
            "end_time REAL, " +
            "project_path TEXT, " +
            "project_name TEXT, " +
            "duration_seconds INTEGER, " +
            "files_modified INTEGER, " +
            "lines_added INTEGER, " +
            "lines_deleted INTEGER, " +
            "status TEXT DEFAULT 'active')",

            "CREATE TABLE IF NOT EXISTS file_changes (" +
            "change_id INTEGER PRIMARY KEY AUTOINCREMENT, " +
            "session_id TEXT, " +
            "file_path TEXT, " +
            "timestamp REAL, " +
            "change_type TEXT, " +
            "lines_added INTEGER, " +
            "lines_deleted INTEGER, " +
            "file_hash TEXT)",

            "CREATE TABLE IF NOT EXISTS checkpoints (" +
            "checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT, " +
            "session_id TEXT, " +
            "timestamp REAL, " +
            "file_path TEXT, " +
            "line_number INTEGER, " +
            "cursor_position INTEGER, " +
            "scroll_position INTEGER, " +
            "open_files TEXT, " +
            "notes TEXT)"
        };

        Statement stmt = conn.createStatement();
        for (String query : queries) {
            stmt.execute(query);
        }
        stmt.close();
    }

    public String startSession(String projectPath, String projectName) throws SQLException {
        double timestamp = System.currentTimeMillis() / 1000.0;
        String hash = getMD5(projectPath).substring(0, 8);
        String sessionId = "session_" + (long)timestamp + "_" + hash;

        if (projectName == null || projectName.isEmpty()) {
            projectName = new File(projectPath).getName();
        }

        PreparedStatement pstmt = conn.prepareStatement(
            "INSERT INTO sessions (session_id, start_time, project_path, project_name, status) " +
            "VALUES (?, ?, ?, ?, 'active')"
        );
        pstmt.setString(1, sessionId);
        pstmt.setDouble(2, timestamp);
        pstmt.setString(3, projectPath);
        pstmt.setString(4, projectName);
        pstmt.executeUpdate();
        pstmt.close();

        currentSessionId = sessionId;
        System.out.println("✅ Session started: " + sessionId);
        return sessionId;
    }

    public void logFileChange(String filePath, String changeType, int linesAdded, int linesDeleted) 
            throws SQLException {
        if (currentSessionId == null) return;

        double timestamp = System.currentTimeMillis() / 1000.0;
        String fileHash = getMD5(filePath);

        PreparedStatement pstmt = conn.prepareStatement(
            "INSERT INTO file_changes " +
            "(session_id, file_path, timestamp, change_type, lines_added, lines_deleted, file_hash) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        );
        pstmt.setString(1, currentSessionId);
        pstmt.setString(2, filePath);
        pstmt.setDouble(3, timestamp);
        pstmt.setString(4, changeType);
        pstmt.setInt(5, linesAdded);
        pstmt.setInt(6, linesDeleted);
        pstmt.setString(7, fileHash);
        pstmt.executeUpdate();
        pstmt.close();

        System.out.println("📝 " + changeType + ": " + new File(filePath).getName() + 
                         " (+" + linesAdded + "/-" + linesDeleted + ")");
    }

    public void saveCheckpoint(String filePath, int lineNumber, int cursorPosition,
                              int scrollPosition, List<String> openFiles, String notes) 
            throws SQLException {
        if (currentSessionId == null) return;

        double timestamp = System.currentTimeMillis() / 1000.0;
        
        // Convert list to JSON-like string
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < openFiles.size(); i++) {
            sb.append("\"").append(openFiles.get(i)).append("\"");
            if (i < openFiles.size() - 1) sb.append(",");
        }
        sb.append("]");

        PreparedStatement pstmt = conn.prepareStatement(
            "INSERT INTO checkpoints " +
            "(session_id, timestamp, file_path, line_number, cursor_position, " +
            "scroll_position, open_files, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        );
        pstmt.setString(1, currentSessionId);
        pstmt.setDouble(2, timestamp);
        pstmt.setString(3, filePath);
        pstmt.setInt(4, lineNumber);
        pstmt.setInt(5, cursorPosition);
        pstmt.setInt(6, scrollPosition);
        pstmt.setString(7, sb.toString());
        pstmt.setString(8, notes);
        pstmt.executeUpdate();
        pstmt.close();

        System.out.println("✅ Checkpoint saved: " + filePath + ":" + lineNumber);
    }

    public void endSession() throws SQLException {
        if (currentSessionId == null) return;

        double timestamp = System.currentTimeMillis() / 1000.0;

        // Get stats
        PreparedStatement pstmt = conn.prepareStatement(
            "SELECT COUNT(DISTINCT file_path), SUM(lines_added), SUM(lines_deleted) " +
            "FROM file_changes WHERE session_id = ?"
        );
        pstmt.setString(1, currentSessionId);
        ResultSet rs = pstmt.executeQuery();

        int files = 0, added = 0, deleted = 0;
        if (rs.next()) {
            files = rs.getInt(1);
            added = rs.getInt(2);
            deleted = rs.getInt(3);
        }
        rs.close();
        pstmt.close();

        // Update session
        pstmt = conn.prepareStatement(
            "UPDATE sessions SET end_time = ?, duration_seconds = ? - start_time, " +
            "files_modified = ?, lines_added = ?, lines_deleted = ?, status = 'completed' " +
            "WHERE session_id = ?"
        );
        pstmt.setDouble(1, timestamp);
        pstmt.setDouble(2, timestamp);
        pstmt.setInt(3, files);
        pstmt.setInt(4, added);
        pstmt.setInt(5, deleted);
        pstmt.setString(6, currentSessionId);
        pstmt.executeUpdate();
        pstmt.close();

        System.out.println("✅ Session ended: " + files + " files, +" + added + "/-" + deleted + " lines");
        currentSessionId = null;
    }

    private String getMD5(String input) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(input.getBytes());
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 8; i++) {
                sb.append(String.format("%02x", digest[i]));
            }
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }

    public void close() throws SQLException {
        if (conn != null) conn.close();
    }

    public static void main(String[] args) {
        try {
            System.out.println("🎯 Session Tracker Demo (Java)\n");

            SessionTracker tracker = new SessionTracker("forge_sessions.db");
            
            String sessionId = tracker.startSession("/home/user/project", "My Project");
            System.out.println();
            
            tracker.logFileChange("src/Main.java", "modified", 25, 10);
            tracker.logFileChange("src/Utils.java", "created", 50, 0);
            
            List<String> openFiles = new ArrayList<>();
            openFiles.add("src/Main.java");
            openFiles.add("src/Utils.java");
            tracker.saveCheckpoint("src/Main.java", 42, 150, 500, openFiles, 
                                  "Working on authentication feature");
            System.out.println();
            
            tracker.endSession();
            tracker.close();

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}

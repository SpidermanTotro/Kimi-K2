// Session Tracker - C# Version
// Tracks coding sessions, progress, and provides analytics

using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

public class SessionTracker
{
    private SQLiteConnection conn;
    private string currentSessionId;

    public SessionTracker(string dbPath = "forge_sessions.db")
    {
        conn = new SQLiteConnection($"Data Source={dbPath};Version=3;");
        conn.Open();
        InitDatabase();
    }

    private void InitDatabase()
    {
        string[] queries = {
            @"CREATE TABLE IF NOT EXISTS sessions (
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

            @"CREATE TABLE IF NOT EXISTS file_changes (
                change_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                file_path TEXT,
                timestamp REAL,
                change_type TEXT,
                lines_added INTEGER,
                lines_deleted INTEGER,
                file_hash TEXT
            )",

            @"CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp REAL,
                file_path TEXT,
                line_number INTEGER,
                cursor_position INTEGER,
                scroll_position INTEGER,
                open_files TEXT,
                notes TEXT
            )"
        };

        using (var cmd = conn.CreateCommand())
        {
            foreach (var query in queries)
            {
                cmd.CommandText = query;
                cmd.ExecuteNonQuery();
            }
        }
    }

    public string StartSession(string projectPath, string projectName = null)
    {
        double timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        string hash = GetMD5(projectPath).Substring(0, 8);
        string sessionId = $"session_{(long)timestamp}_{hash}";

        if (string.IsNullOrEmpty(projectName))
        {
            projectName = Path.GetFileName(projectPath);
        }

        using (var cmd = conn.CreateCommand())
        {
            cmd.CommandText = @"INSERT INTO sessions (session_id, start_time, project_path, project_name, status)
                               VALUES (@id, @time, @path, @name, 'active')";
            cmd.Parameters.AddWithValue("@id", sessionId);
            cmd.Parameters.AddWithValue("@time", timestamp);
            cmd.Parameters.AddWithValue("@path", projectPath);
            cmd.Parameters.AddWithValue("@name", projectName);
            cmd.ExecuteNonQuery();
        }

        currentSessionId = sessionId;
        Console.WriteLine($"✅ Session started: {sessionId}");
        return sessionId;
    }

    public void LogFileChange(string filePath, string changeType, int linesAdded = 0, int linesDeleted = 0)
    {
        if (string.IsNullOrEmpty(currentSessionId)) return;

        double timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        string fileHash = GetMD5(filePath);

        using (var cmd = conn.CreateCommand())
        {
            cmd.CommandText = @"INSERT INTO file_changes 
                (session_id, file_path, timestamp, change_type, lines_added, lines_deleted, file_hash)
                VALUES (@sid, @path, @time, @type, @added, @deleted, @hash)";
            cmd.Parameters.AddWithValue("@sid", currentSessionId);
            cmd.Parameters.AddWithValue("@path", filePath);
            cmd.Parameters.AddWithValue("@time", timestamp);
            cmd.Parameters.AddWithValue("@type", changeType);
            cmd.Parameters.AddWithValue("@added", linesAdded);
            cmd.Parameters.AddWithValue("@deleted", linesDeleted);
            cmd.Parameters.AddWithValue("@hash", fileHash);
            cmd.ExecuteNonQuery();
        }

        Console.WriteLine($"📝 {changeType}: {Path.GetFileName(filePath)} (+{linesAdded}/-{linesDeleted})");
    }

    public void SaveCheckpoint(string filePath, int lineNumber, int cursorPosition,
                              int scrollPosition, List<string> openFiles, string notes = "")
    {
        if (string.IsNullOrEmpty(currentSessionId)) return;

        double timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        string openFilesJson = JsonSerializer.Serialize(openFiles);

        using (var cmd = conn.CreateCommand())
        {
            cmd.CommandText = @"INSERT INTO checkpoints 
                (session_id, timestamp, file_path, line_number, cursor_position, 
                 scroll_position, open_files, notes)
                VALUES (@sid, @time, @path, @line, @cursor, @scroll, @files, @notes)";
            cmd.Parameters.AddWithValue("@sid", currentSessionId);
            cmd.Parameters.AddWithValue("@time", timestamp);
            cmd.Parameters.AddWithValue("@path", filePath);
            cmd.Parameters.AddWithValue("@line", lineNumber);
            cmd.Parameters.AddWithValue("@cursor", cursorPosition);
            cmd.Parameters.AddWithValue("@scroll", scrollPosition);
            cmd.Parameters.AddWithValue("@files", openFilesJson);
            cmd.Parameters.AddWithValue("@notes", notes);
            cmd.ExecuteNonQuery();
        }

        Console.WriteLine($"✅ Checkpoint saved: {filePath}:{lineNumber}");
    }

    public void EndSession()
    {
        if (string.IsNullOrEmpty(currentSessionId)) return;

        double timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

        // Get stats
        int files = 0, added = 0, deleted = 0;
        using (var cmd = conn.CreateCommand())
        {
            cmd.CommandText = @"SELECT COUNT(DISTINCT file_path), SUM(lines_added), SUM(lines_deleted)
                               FROM file_changes WHERE session_id = @sid";
            cmd.Parameters.AddWithValue("@sid", currentSessionId);
            
            using (var reader = cmd.ExecuteReader())
            {
                if (reader.Read())
                {
                    files = reader.GetInt32(0);
                    added = reader.IsDBNull(1) ? 0 : reader.GetInt32(1);
                    deleted = reader.IsDBNull(2) ? 0 : reader.GetInt32(2);
                }
            }
        }

        // Update session
        using (var cmd = conn.CreateCommand())
        {
            cmd.CommandText = @"UPDATE sessions SET 
                end_time = @time,
                duration_seconds = @time - start_time,
                files_modified = @files,
                lines_added = @added,
                lines_deleted = @deleted,
                status = 'completed'
                WHERE session_id = @sid";
            cmd.Parameters.AddWithValue("@time", timestamp);
            cmd.Parameters.AddWithValue("@files", files);
            cmd.Parameters.AddWithValue("@added", added);
            cmd.Parameters.AddWithValue("@deleted", deleted);
            cmd.Parameters.AddWithValue("@sid", currentSessionId);
            cmd.ExecuteNonQuery();
        }

        Console.WriteLine($"✅ Session ended: {files} files, +{added}/-{deleted} lines");
        currentSessionId = null;
    }

    private string GetMD5(string input)
    {
        using (var md5 = MD5.Create())
        {
            byte[] hash = md5.ComputeHash(Encoding.UTF8.GetBytes(input));
            var sb = new StringBuilder();
            for (int i = 0; i < 8; i++)
            {
                sb.Append(hash[i].ToString("x2"));
            }
            return sb.ToString();
        }
    }

    public void Close()
    {
        conn?.Close();
    }

    static void Main()
    {
        Console.WriteLine("🎯 Session Tracker Demo (C#)\n");

        var tracker = new SessionTracker();
        
        string sessionId = tracker.StartSession("/home/user/project", "My Project");
        Console.WriteLine();
        
        tracker.LogFileChange("src/Program.cs", "modified", 25, 10);
        tracker.LogFileChange("src/Utils.cs", "created", 50, 0);
        
        var openFiles = new List<string> { "src/Program.cs", "src/Utils.cs" };
        tracker.SaveCheckpoint("src/Program.cs", 42, 150, 500, openFiles,
                              "Working on authentication feature");
        Console.WriteLine();
        
        tracker.EndSession();
        tracker.Close();
    }
}

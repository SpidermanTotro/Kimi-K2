// Session Tracker - C++ Version
// Tracks coding sessions, progress, and provides analytics

#include <sqlite3.h>
#include <iostream>
#include <string>
#include <vector>
#include <ctime>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <openssl/md5.h>

class SessionTracker {
private:
    sqlite3* db;
    std::string currentSessionId;

    std::string getMD5(const std::string& input) {
        unsigned char digest[MD5_DIGEST_LENGTH];
        MD5((unsigned char*)input.c_str(), input.length(), digest);
        
        std::stringstream ss;
        for(int i = 0; i < 8; i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') << (int)digest[i];
        }
        return ss.str();
    }

    double getCurrentTimestamp() {
        return (double)std::time(nullptr);
    }

    std::string timeAgo(double timestamp) {
        double diff = getCurrentTimestamp() - timestamp;
        
        if (diff < 60) return std::to_string((int)diff) + "s ago";
        if (diff < 3600) return std::to_string((int)(diff/60)) + "m ago";
        if (diff < 86400) return std::to_string((int)(diff/3600)) + "h ago";
        return std::to_string((int)(diff/86400)) + "d ago";
    }

public:
    SessionTracker(const std::string& dbPath = "forge_sessions.db") {
        int rc = sqlite3_open(dbPath.c_str(), &db);
        if (rc) {
            std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
            return;
        }
        initDatabase();
    }

    ~SessionTracker() {
        sqlite3_close(db);
    }

    void initDatabase() {
        const char* sql[] = {
            "CREATE TABLE IF NOT EXISTS sessions ("
            "session_id TEXT PRIMARY KEY,"
            "start_time REAL,"
            "end_time REAL,"
            "project_path TEXT,"
            "project_name TEXT,"
            "duration_seconds INTEGER,"
            "files_modified INTEGER,"
            "lines_added INTEGER,"
            "lines_deleted INTEGER,"
            "status TEXT DEFAULT 'active'"
            ")",
            
            "CREATE TABLE IF NOT EXISTS file_changes ("
            "change_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "session_id TEXT,"
            "file_path TEXT,"
            "timestamp REAL,"
            "change_type TEXT,"
            "lines_added INTEGER,"
            "lines_deleted INTEGER,"
            "file_hash TEXT"
            ")",
            
            "CREATE TABLE IF NOT EXISTS checkpoints ("
            "checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "session_id TEXT,"
            "timestamp REAL,"
            "file_path TEXT,"
            "line_number INTEGER,"
            "cursor_position INTEGER,"
            "scroll_position INTEGER,"
            "open_files TEXT,"
            "notes TEXT"
            ")"
        };

        char* errMsg = nullptr;
        for (const char* query : sql) {
            int rc = sqlite3_exec(db, query, nullptr, nullptr, &errMsg);
            if (rc != SQLITE_OK) {
                std::cerr << "SQL error: " << errMsg << std::endl;
                sqlite3_free(errMsg);
            }
        }
    }

    std::string startSession(const std::string& projectPath, const std::string& projectName = "") {
        double timestamp = getCurrentTimestamp();
        std::string hash = getMD5(projectPath);
        std::string sessionId = "session_" + std::to_string((long)timestamp) + "_" + hash;

        std::string name = projectName.empty() ? projectPath.substr(projectPath.find_last_of("/\\") + 1) : projectName;

        std::string sql = "INSERT INTO sessions (session_id, start_time, project_path, project_name, status) "
                         "VALUES (?, ?, ?, ?, 'active')";
        
        sqlite3_stmt* stmt;
        sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
        sqlite3_bind_text(stmt, 1, sessionId.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_double(stmt, 2, timestamp);
        sqlite3_bind_text(stmt, 3, projectPath.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 4, name.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_step(stmt);
        sqlite3_finalize(stmt);

        currentSessionId = sessionId;
        std::cout << "✅ Session started: " << sessionId << std::endl;
        return sessionId;
    }

    void logFileChange(const std::string& filePath, const std::string& changeType, 
                       int linesAdded = 0, int linesDeleted = 0) {
        if (currentSessionId.empty()) return;

        double timestamp = getCurrentTimestamp();
        std::string fileHash = getMD5(filePath);

        std::string sql = "INSERT INTO file_changes "
                         "(session_id, file_path, timestamp, change_type, lines_added, lines_deleted, file_hash) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?)";
        
        sqlite3_stmt* stmt;
        sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
        sqlite3_bind_text(stmt, 1, currentSessionId.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 2, filePath.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_double(stmt, 3, timestamp);
        sqlite3_bind_text(stmt, 4, changeType.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_int(stmt, 5, linesAdded);
        sqlite3_bind_int(stmt, 6, linesDeleted);
        sqlite3_bind_text(stmt, 7, fileHash.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_step(stmt);
        sqlite3_finalize(stmt);

        std::cout << "📝 " << changeType << ": " << filePath << " (+" << linesAdded << "/-" << linesDeleted << ")" << std::endl;
    }

    void saveCheckpoint(const std::string& filePath, int lineNumber, int cursorPosition,
                       int scrollPosition, const std::vector<std::string>& openFiles, 
                       const std::string& notes = "") {
        if (currentSessionId.empty()) return;

        double timestamp = getCurrentTimestamp();
        
        // Convert vector to JSON-like string
        std::string openFilesStr = "[";
        for (size_t i = 0; i < openFiles.size(); i++) {
            openFilesStr += "\"" + openFiles[i] + "\"";
            if (i < openFiles.size() - 1) openFilesStr += ",";
        }
        openFilesStr += "]";

        std::string sql = "INSERT INTO checkpoints "
                         "(session_id, timestamp, file_path, line_number, cursor_position, "
                         "scroll_position, open_files, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        
        sqlite3_stmt* stmt;
        sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
        sqlite3_bind_text(stmt, 1, currentSessionId.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_double(stmt, 2, timestamp);
        sqlite3_bind_text(stmt, 3, filePath.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_int(stmt, 4, lineNumber);
        sqlite3_bind_int(stmt, 5, cursorPosition);
        sqlite3_bind_int(stmt, 6, scrollPosition);
        sqlite3_bind_text(stmt, 7, openFilesStr.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 8, notes.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_step(stmt);
        sqlite3_finalize(stmt);

        std::cout << "✅ Checkpoint saved: " << filePath << ":" << lineNumber << std::endl;
    }

    void endSession() {
        if (currentSessionId.empty()) return;

        double timestamp = getCurrentTimestamp();

        // Get stats
        std::string sql = "SELECT COUNT(DISTINCT file_path), SUM(lines_added), SUM(lines_deleted) "
                         "FROM file_changes WHERE session_id = ?";
        
        sqlite3_stmt* stmt;
        sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
        sqlite3_bind_text(stmt, 1, currentSessionId.c_str(), -1, SQLITE_TRANSIENT);
        
        int files = 0, added = 0, deleted = 0;
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            files = sqlite3_column_int(stmt, 0);
            added = sqlite3_column_int(stmt, 1);
            deleted = sqlite3_column_int(stmt, 2);
        }
        sqlite3_finalize(stmt);

        // Update session
        sql = "UPDATE sessions SET end_time = ?, duration_seconds = ? - start_time, "
              "files_modified = ?, lines_added = ?, lines_deleted = ?, status = 'completed' "
              "WHERE session_id = ?";
        
        sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr);
        sqlite3_bind_double(stmt, 1, timestamp);
        sqlite3_bind_double(stmt, 2, timestamp);
        sqlite3_bind_int(stmt, 3, files);
        sqlite3_bind_int(stmt, 4, added);
        sqlite3_bind_int(stmt, 5, deleted);
        sqlite3_bind_text(stmt, 6, currentSessionId.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_step(stmt);
        sqlite3_finalize(stmt);

        std::cout << "✅ Session ended: " << files << " files, +" << added << "/-" << deleted << " lines" << std::endl;
        currentSessionId.clear();
    }
};

int main() {
    std::cout << "🎯 Session Tracker Demo (C++)\n" << std::endl;

    SessionTracker tracker;
    
    std::string sessionId = tracker.startSession("/home/user/project", "My Project");
    std::cout << std::endl;
    
    tracker.logFileChange("src/main.cpp", "modified", 25, 10);
    tracker.logFileChange("src/utils.cpp", "created", 50, 0);
    
    std::vector<std::string> openFiles = {"src/main.cpp", "src/utils.cpp"};
    tracker.saveCheckpoint("src/main.cpp", 42, 150, 500, openFiles, 
                          "Working on authentication feature");
    std::cout << std::endl;
    
    tracker.endSession();
    
    return 0;
}

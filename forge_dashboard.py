#!/usr/bin/env python3
"""
THE FORGE Analytics Dashboard - Complete Session Tracking & Analytics
Shows status bars, changelogs, recommendations, and real-time progress
This is a SEPARATE feature that will be linked to THE FORGE and KIMI-2 later
"""

from session_tracker import SessionTracker
import os
import sys
from datetime import datetime, timedelta

class ForgeDashboard:
    """Complete analytics dashboard for THE FORGE"""
    
    def __init__(self):
        self.tracker = SessionTracker()
        self.width = 80
    
    def draw_status_bar(self, label, value, max_value, width=40):
        """Draw a status bar"""
        if max_value == 0:
            percentage = 0
        else:
            percentage = min(100, int((value / max_value) * 100))
        
        filled = int((percentage / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        
        return f"{label:20} [{bar}] {percentage}% ({value}/{max_value})"
    
    def print_header(self, title):
        """Print a section header"""
        print("\n" + "=" * self.width)
        print(f"{title:^{self.width}}")
        print("=" * self.width)
    
    def print_separator(self):
        """Print a separator line"""
        print("-" * self.width)
    
    def show_current_session_status(self):
        """Show current session status bar"""
        self.print_header("📊 CURRENT SESSION STATUS")
        
        if not self.tracker.current_session_id:
            print("\n⚠️  No active session. Start a session to track your work!")
            print("\nStart coding with:")
            print("  ./start_forge.sh")
            return
        
        dashboard = self.tracker.get_session_dashboard()
        
        print(f"\n🎯 Session: {dashboard['session_id']}")
        print(f"📁 Project: {dashboard['project_name']}")
        print(f"⏰ Started: {dashboard['start_time']}")
        print(f"⏱️  Duration: {dashboard['duration']}")
        print(f"📝 Status: {dashboard['status'].upper()}")
        
        print("\n📈 Progress Metrics:")
        self.print_separator()
        
        # Status bars
        print(self.draw_status_bar("Files Modified", dashboard['files_modified'], 20))
        print(self.draw_status_bar("Lines Added", dashboard['lines_added'], 500))
        print(self.draw_status_bar("Lines Deleted", dashboard['lines_deleted'], 200))
        
        # Productivity score (based on activity)
        activity_score = min(100, (dashboard['files_modified'] * 10 + 
                                   dashboard['lines_added'] // 10))
        print(self.draw_status_bar("Productivity", activity_score, 100))
        
        print("\n📋 Recent Activity:")
        self.print_separator()
        for i, activity in enumerate(dashboard['activities'][:10], 1):
            print(f"{i:2}. [{activity['time']}] {activity['description']}")
        
        print("\n📂 Recent File Changes:")
        self.print_separator()
        for i, change in enumerate(dashboard['changes'][:10], 1):
            print(f"{i:2}. {change['file']:30} {change['type']:10} "
                  f"(+{change['lines_added']}/-{change['lines_deleted']}) "
                  f"- {change['time']}")
    
    def show_changelog(self, days=7):
        """Show changelog for recent sessions"""
        self.print_header(f"📝 CHANGELOG - LAST {days} DAYS")
        
        changelog = self.tracker.get_changelog(days)
        
        if not changelog:
            print("\n⚠️  No coding sessions found in the last 7 days.")
            return
        
        print(f"\nTotal sessions: {len(changelog)}")
        self.print_separator()
        
        current_date = None
        for entry in changelog:
            if entry['date'] != current_date:
                current_date = entry['date']
                print(f"\n📅 {current_date}")
                print("  " + "-" * (self.width - 2))
            
            print(f"  [{entry['time']}] {entry['project']:30} "
                  f"({entry['duration']:8}) "
                  f"{entry['files']:2} files, "
                  f"+{entry['added']:4}/-{entry['deleted']:4} lines")
    
    def show_daily_stats(self, days=7):
        """Show daily statistics"""
        self.print_header(f"📊 DAILY STATISTICS - LAST {days} DAYS")
        
        stats = self.tracker.get_daily_stats(days)
        
        print("\n🎯 Summary:")
        self.print_separator()
        print(f"  Total Sessions:     {stats['summary']['total_sessions']}")
        print(f"  Total Duration:     {stats['summary']['total_duration']}")
        print(f"  Total Files:        {stats['summary']['total_files']}")
        print(f"  Total Lines Added:  {stats['summary']['total_lines_added']}")
        print(f"  Total Lines Deleted:{stats['summary']['total_lines_deleted']}")
        print(f"  Avg Session:        {stats['summary']['avg_session_duration']}")
        
        print("\n📈 Daily Breakdown:")
        self.print_separator()
        print(f"{'Date':12} {'Sessions':10} {'Duration':12} {'Lines Changed':15}")
        self.print_separator()
        
        for day in stats['daily']:
            print(f"{day['date']:12} {day['sessions']:10} "
                  f"{day['duration']:12} {day['lines_changed']:15}")
    
    def show_recommendations(self):
        """Show smart recommendations"""
        self.print_header("💡 SMART RECOMMENDATIONS")
        
        recs = self.tracker.get_recommendations()
        
        if not recs:
            print("\n✅ No pending recommendations. You're doing great!")
            return
        
        print(f"\nYou have {len(recs)} recommendations:")
        self.print_separator()
        
        for i, rec in enumerate(recs, 1):
            priority_icon = "🔴" if rec['priority'] >= 3 else "🟡" if rec['priority'] == 2 else "🟢"
            print(f"\n{i}. {priority_icon} {rec['title']}")
            print(f"   Type: {rec['type']}")
            print(f"   {rec['description']}")
            print(f"   Suggested: {rec['time_ago']}")
    
    def show_resume_point(self):
        """Show where to resume work"""
        self.print_header("🔖 RESUME WORK")
        
        checkpoint = self.tracker.get_last_checkpoint()
        
        if not checkpoint:
            print("\n⚠️  No checkpoint found. Start working to create checkpoints!")
            return
        
        print("\n📍 Last Checkpoint (Resume from here):")
        self.print_separator()
        print(f"  File:            {checkpoint['file_path']}")
        print(f"  Line Number:     {checkpoint['line_number']}")
        print(f"  Cursor Position: {checkpoint['cursor_position']}")
        print(f"  Scroll Position: {checkpoint['scroll_position']}")
        print(f"  Saved:           {checkpoint['time_ago']}")
        
        if checkpoint['notes']:
            print(f"\n📝 Notes:")
            print(f"  {checkpoint['notes']}")
        
        if checkpoint['open_files']:
            print(f"\n📂 Open Files:")
            for i, file in enumerate(checkpoint['open_files'], 1):
                print(f"  {i}. {file}")
        
        print("\n✨ Tips:")
        print("  • THE FORGE will automatically restore your position")
        print("  • All your open files will be reopened")
        print("  • Your cursor will be at the exact same spot")
    
    def show_full_dashboard(self):
        """Show complete dashboard"""
        print("\n" + "╔" + "═" * (self.width - 2) + "╗")
        print(f"║{'🔥 THE FORGE ANALYTICS DASHBOARD 🔥':^{self.width - 2}}║")
        print("╚" + "═" * (self.width - 2) + "╝")
        
        # Show all sections
        self.show_current_session_status()
        self.show_resume_point()
        self.show_recommendations()
        self.show_changelog(7)
        self.show_daily_stats(7)
        
        # Integration info
        self.print_header("🔗 INTEGRATION STATUS")
        print("\n📦 This is a SEPARATE feature that will be integrated with:")
        print("  ✅ THE FORGE - Free GitHub Codespaces alternative")
        print("  ✅ KIMI-2 - Advanced AI assistant")
        print("\n🎯 Current Status: STANDALONE (Ready for integration)")
        print("💰 Cost: $0 (No payments required!)")
        print("\n🚀 Features:")
        print("  ✅ Session tracking across ALL programming languages")
        print("  ✅ Real-time progress monitoring")
        print("  ✅ Smart recommendations")
        print("  ✅ Resume from exact position")
        print("  ✅ Complete analytics and changelogs")
        print("\n💡 Coming Soon:")
        print("  🔜 Full integration with THE FORGE")
        print("  🔜 Link to KIMI-2 AI")
        print("  🔜 Sync across devices")
        print("  🔜 Team collaboration features")


def main():
    dashboard = ForgeDashboard()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            dashboard.show_current_session_status()
        elif command == "resume":
            dashboard.show_resume_point()
        elif command == "changelog":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            dashboard.show_changelog(days)
        elif command == "stats":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            dashboard.show_daily_stats(days)
        elif command == "recommendations" or command == "recs":
            dashboard.show_recommendations()
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python3 forge_dashboard.py [command] [options]")
            print("\nCommands:")
            print("  status          - Show current session status")
            print("  resume          - Show resume point")
            print("  changelog [N]   - Show changelog (default: 7 days)")
            print("  stats [N]       - Show statistics (default: 7 days)")
            print("  recommendations - Show recommendations")
            print("  (no command)    - Show full dashboard")
    else:
        dashboard.show_full_dashboard()


if __name__ == "__main__":
    main()

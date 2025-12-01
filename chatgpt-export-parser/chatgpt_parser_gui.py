#!/usr/bin/env python3
"""
ChatGPT Export Parser - GUI Version
Simple graphical interface for parsing ChatGPT exports
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from chatgpt_parser import ChatGPTExportParser

class ChatGPTParserGUI:
    """GUI application for ChatGPT Export Parser"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT Export Parser")
        self.root.geometry("800x600")
        
        self.parser = None
        self.export_file = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="🔍 ChatGPT Export Parser",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Extract all text and conversations from ChatGPT exports",
            font=("Arial", 10)
        )
        subtitle_label.pack()
        
        # File selection
        file_frame = ttk.LabelFrame(self.root, text="Select Export File", padding="10")
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        file_entry.pack(side=tk.LEFT, padx=5)
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT)
        
        parse_btn = ttk.Button(file_frame, text="Parse", command=self.parse_file)
        parse_btn.pack(side=tk.LEFT, padx=5)
        
        # Export options
        export_frame = ttk.LabelFrame(self.root, text="Export Options", padding="10")
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(export_frame, text="Export to Markdown", command=self.export_markdown).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export to JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export to Text", command=self.export_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export All", command=self.export_all).pack(side=tk.LEFT, padx=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=10, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def browse_file(self):
        """Browse for export file"""
        filename = filedialog.askopenfilename(
            title="Select ChatGPT Export File",
            filetypes=[
                ("All Supported", "*.zip *.json *.html *.htm"),
                ("ZIP files", "*.zip"),
                ("JSON files", "*.json"),
                ("HTML files", "*.html *.htm"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.export_file = filename
    
    def parse_file(self):
        """Parse the selected file"""
        if not self.export_file:
            messagebox.showerror("Error", "Please select an export file first")
            return
        
        self.status_var.set("Parsing...")
        self.stats_text.delete(1.0, tk.END)
        
        # Parse in thread to avoid freezing GUI
        thread = threading.Thread(target=self._parse_thread)
        thread.start()
    
    def _parse_thread(self):
        """Parse file in separate thread"""
        try:
            self.parser = ChatGPTExportParser(self.export_file)
            result = self.parser.parse()
            stats = self.parser.get_statistics()
            
            # Update GUI in main thread
            self.root.after(0, self._update_stats, result, stats)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to parse: {e}"))
            self.root.after(0, lambda: self.status_var.set("Error"))
    
    def _update_stats(self, result, stats):
        """Update statistics display"""
        self.stats_text.delete(1.0, tk.END)
        
        output = f"""📊 PARSING RESULTS

Total Conversations: {result['total_conversations']}
Total Messages: {result['total_messages']}
Average Messages per Conversation: {stats['average_messages_per_conversation']:.1f}

Messages by Role:
"""
        
        for role, count in stats['messages_by_role'].items():
            if count > 0:
                output += f"  • {role.capitalize()}: {count}\n"
        
        output += f"""
Content Statistics:
  • Total Characters: {stats['total_characters']:,}
  • Total Words: {stats['total_words']:,}

Export Date: {result.get('export_date', 'Unknown')}
"""
        
        self.stats_text.insert(1.0, output)
        self.status_var.set("Parsing complete!")
    
    def export_markdown(self):
        """Export to Markdown"""
        if not self.parser:
            messagebox.showerror("Error", "Please parse a file first")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Markdown File",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.parser.export_to_markdown(filename)
                messagebox.showinfo("Success", f"Exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_json(self):
        """Export to JSON"""
        if not self.parser:
            messagebox.showerror("Error", "Please parse a file first")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save JSON File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.parser.export_to_json(filename)
                messagebox.showinfo("Success", f"Exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_text(self):
        """Export to text"""
        if not self.parser:
            messagebox.showerror("Error", "Please parse a file first")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Text File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.parser.export_to_text(filename)
                messagebox.showinfo("Success", f"Exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_all(self):
        """Export to all formats"""
        if not self.parser:
            messagebox.showerror("Error", "Please parse a file first")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Files (prefix)",
            defaultextension="",
            filetypes=[("All files", "*.*")]
        )
        
        if filename:
            try:
                base = Path(filename).stem
                directory = Path(filename).parent
                
                md_file = directory / f"{base}.md"
                json_file = directory / f"{base}.json"
                txt_file = directory / f"{base}.txt"
                
                self.parser.export_to_markdown(str(md_file))
                self.parser.export_to_json(str(json_file))
                self.parser.export_to_text(str(txt_file))
                
                messagebox.showinfo("Success", f"Exported to:\n{md_file}\n{json_file}\n{txt_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ChatGPTParserGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
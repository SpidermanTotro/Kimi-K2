#!/usr/bin/env python3
"""
THE FORGE AI - Book Writing System GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from book_writer import BookWritingSystem
from pathlib import Path

class BookWriterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("THE FORGE AI - Book Writing System")
        self.root.geometry("1200x800")
        
        self.system = BookWritingSystem()
        
        self.create_widgets()
        self.refresh_projects()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="📚 THE FORGE AI - Book Writing System",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="New Project", command=self.new_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add Chapter", command=self.add_chapter).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export", command=self.export_manuscript).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_projects).pack(side=tk.LEFT, padx=5)
        
        # Projects list
        list_frame = ttk.LabelFrame(main_frame, text="Projects", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.projects_text = scrolledtext.ScrolledText(list_frame, height=20, wrap=tk.WORD)
        self.projects_text.pack(fill=tk.BOTH, expand=True)
    
    def refresh_projects(self):
        self.projects_text.delete(1.0, tk.END)
        
        if not self.system.projects:
            self.projects_text.insert(1.0, "No projects yet. Create one to get started!")
            return
        
        for pid, project in self.system.projects.items():
            progress = (project['current_words'] / project['target_words']) * 100
            
            text = f"""
📖 {project['title']}
   ID: {pid}
   Genre: {project['genre']}
   Progress: {project['current_words']:,} / {project['target_words']:,} words ({progress:.1f}%)
   Chapters: {len(project['chapters'])}
   Status: {project['status']}
{'─' * 80}
"""
            self.projects_text.insert(tk.END, text)
    
    def new_project(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Book Project")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Book Title:").pack(pady=5)
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Genre:").pack(pady=5)
        genre_entry = ttk.Entry(dialog, width=40)
        genre_entry.insert(0, "Fiction")
        genre_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Target Words:").pack(pady=5)
        words_entry = ttk.Entry(dialog, width=40)
        words_entry.insert(0, "50000")
        words_entry.pack(pady=5)
        
        def create():
            title = title_entry.get()
            genre = genre_entry.get()
            words = int(words_entry.get())
            
            self.system.create_project(title, genre, words)
            self.refresh_projects()
            dialog.destroy()
            messagebox.showinfo("Success", f"Created project: {title}")
        
        ttk.Button(dialog, text="Create", command=create).pack(pady=20)
    
    def add_chapter(self):
        if not self.system.projects:
            messagebox.showerror("Error", "No projects found. Create one first.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Chapter")
        dialog.geometry("600x400")
        
        ttk.Label(dialog, text="Project ID:").pack(pady=5)
        project_combo = ttk.Combobox(dialog, values=list(self.system.projects.keys()), width=40)
        project_combo.pack(pady=5)
        if self.system.projects:
            project_combo.current(0)
        
        ttk.Label(dialog, text="Chapter Title:").pack(pady=5)
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Content:").pack(pady=5)
        content_text = scrolledtext.ScrolledText(dialog, height=10, width=60)
        content_text.pack(pady=5)
        
        def add():
            project_id = project_combo.get()
            title = title_entry.get()
            content = content_text.get(1.0, tk.END)
            
            self.system.add_chapter(project_id, title, content)
            self.refresh_projects()
            dialog.destroy()
            messagebox.showinfo("Success", f"Added chapter: {title}")
        
        ttk.Button(dialog, text="Add Chapter", command=add).pack(pady=10)
    
    def export_manuscript(self):
        if not self.system.projects:
            messagebox.showerror("Error", "No projects found.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Export Manuscript")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Project ID:").pack(pady=5)
        project_combo = ttk.Combobox(dialog, values=list(self.system.projects.keys()), width=40)
        project_combo.pack(pady=5)
        if self.system.projects:
            project_combo.current(0)
        
        ttk.Label(dialog, text="Format:").pack(pady=5)
        format_combo = ttk.Combobox(dialog, values=['txt', 'md'], width=40)
        format_combo.current(0)
        format_combo.pack(pady=5)
        
        def export():
            project_id = project_combo.get()
            format = format_combo.get()
            
            output = self.system.export_manuscript(project_id, format)
            dialog.destroy()
            messagebox.showinfo("Success", f"Exported to:\n{output}")
        
        ttk.Button(dialog, text="Export", command=export).pack(pady=20)

def main():
    root = tk.Tk()
    app = BookWriterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()

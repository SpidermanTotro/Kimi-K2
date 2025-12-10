#!/usr/bin/env python3
"""
AI Ripper GUI - Visual Interface for AI Model Extraction
========================================================
Cross-platform graphical interface built with Tkinter
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from ai_ripper_core import AIRipper, EndpointConfig, RippingProgress, request_ethical_consent
from typing import Dict, List
import json


class AIRipperGUI:
    """Main GUI application for AI Ripper"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Ripper - Model Extraction & Analysis Tool")
        self.root.geometry("1200x800")
        
        # Initialize ripper
        self.ripper = AIRipper()
        self.ripper.set_progress_callback(self.update_progress)
        
        # State
        self.endpoints: Dict[str, EndpointConfig] = {}
        self.is_ripping = False
        self.consent_given = False
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.setup_main_tab()
        self.setup_visualization_tab()
        self.setup_settings_tab()
        self.setup_logs_tab()
        
    def setup_main_tab(self):
        """Setup main ripping interface tab"""
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Main")
        
        # Top section - Endpoint configuration
        config_frame = ttk.LabelFrame(main_frame, text="Endpoint Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # URL input
        ttk.Label(config_frame, text="Endpoint URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(config_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)
        self.url_entry.insert(0, "http://localhost:8000")
        
        # API Key input
        ttk.Label(config_frame, text="API Key (optional):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(config_frame, width=50, show="*")
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Endpoint name
        ttk.Label(config_frame, text="Endpoint Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.endpoint_name_entry = ttk.Entry(config_frame, width=50)
        self.endpoint_name_entry.grid(row=2, column=1, padx=5, pady=5)
        self.endpoint_name_entry.insert(0, "endpoint_1")
        
        # Add endpoint button
        ttk.Button(config_frame, text="Add Endpoint", command=self.add_endpoint).grid(row=2, column=2, padx=5, pady=5)
        
        # Middle section - Endpoints list
        list_frame = ttk.LabelFrame(main_frame, text="Configured Endpoints", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Endpoints listbox
        self.endpoints_listbox = tk.Listbox(list_frame, height=6)
        self.endpoints_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.endpoints_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.endpoints_listbox.config(yscrollcommand=scrollbar.set)
        
        # Remove endpoint button
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_endpoint).pack(side=tk.LEFT, padx=5)
        
        # Export format selection
        export_frame = ttk.LabelFrame(main_frame, text="Export Options", padding=10)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(export_frame, text="Export Format:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.export_format = tk.StringVar(value="JSON")
        formats = ["JSON", "Python", "GGUF", "ONNX"]
        for i, fmt in enumerate(formats):
            ttk.Radiobutton(export_frame, text=fmt, variable=self.export_format, value=fmt).grid(row=0, column=i+1, padx=5)
        
        # Control section
        control_frame = ttk.LabelFrame(main_frame, text="Control", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Ripping", command=self.start_ripping, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="⏸ Stop", command=self.stop_ripping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="📊 Compare Endpoints", command=self.compare_endpoints).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 Export Selected", command=self.export_model).pack(side=tk.LEFT, padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready", foreground="green")
        self.status_label.pack(fill=tk.X)
        
    def setup_visualization_tab(self):
        """Setup visualization tab"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualization")
        
        # Create matplotlib figure
        self.viz_figure = Figure(figsize=(10, 6))
        
        # Response time plot
        self.ax1 = self.viz_figure.add_subplot(2, 2, 1)
        self.ax1.set_title("Response Times")
        self.ax1.set_xlabel("Request #")
        self.ax1.set_ylabel("Time (s)")
        
        # Capabilities comparison
        self.ax2 = self.viz_figure.add_subplot(2, 2, 2)
        self.ax2.set_title("Capabilities Comparison")
        
        # Token attention heatmap (placeholder)
        self.ax3 = self.viz_figure.add_subplot(2, 2, 3)
        self.ax3.set_title("Token Attention Heatmap")
        
        # Behavior classification
        self.ax4 = self.viz_figure.add_subplot(2, 2, 4)
        self.ax4.set_title("Behavior Classification")
        
        self.viz_figure.tight_layout()
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.viz_figure, viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(viz_frame, text="🔄 Refresh Visualizations", command=self.update_visualizations).pack(pady=5)
        
    def setup_settings_tab(self):
        """Setup settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Advanced settings
        advanced_frame = ttk.LabelFrame(settings_frame, text="Advanced Configuration", padding=10)
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Timeout
        ttk.Label(advanced_frame, text="Request Timeout (seconds):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.IntVar(value=30)
        ttk.Spinbox(advanced_frame, from_=5, to=300, textvariable=self.timeout_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Max retries
        ttk.Label(advanced_frame, text="Max Retries:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.retries_var = tk.IntVar(value=3)
        ttk.Spinbox(advanced_frame, from_=1, to=10, textvariable=self.retries_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Scan depth
        ttk.Label(advanced_frame, text="Scan Depth:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.scan_depth_var = tk.IntVar(value=3)
        ttk.Spinbox(advanced_frame, from_=1, to=10, textvariable=self.scan_depth_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Memory management
        memory_frame = ttk.LabelFrame(settings_frame, text="Memory Management", padding=10)
        memory_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.adaptive_memory_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(memory_frame, text="Enable Adaptive Memory Management", variable=self.adaptive_memory_var).pack(anchor=tk.W)
        
        ttk.Label(memory_frame, text="Max Memory Usage (MB):").pack(anchor=tk.W, pady=(10, 0))
        self.max_memory_var = tk.IntVar(value=2048)
        ttk.Spinbox(memory_frame, from_=512, to=16384, textvariable=self.max_memory_var, width=10).pack(anchor=tk.W, padx=20)
        
        # Security
        security_frame = ttk.LabelFrame(settings_frame, text="Security & Ethics", padding=10)
        security_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.require_consent_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(security_frame, text="Require Ethical Consent Before Ripping", variable=self.require_consent_var).pack(anchor=tk.W)
        
        self.verify_ssl_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(security_frame, text="Verify SSL Certificates", variable=self.verify_ssl_var).pack(anchor=tk.W)
        
        # Save settings button
        ttk.Button(settings_frame, text="💾 Save Settings", command=self.save_settings).pack(pady=10)
        
    def setup_logs_tab(self):
        """Setup logs viewer tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Log viewer
        log_viewer_frame = ttk.LabelFrame(logs_frame, text="Detailed Logs", padding=10)
        log_viewer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_viewer_frame, wrap=tk.WORD, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        btn_frame = ttk.Frame(logs_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="🗑 Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Save Logs", command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
    def add_endpoint(self):
        """Add an endpoint to the list"""
        url = self.url_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        name = self.endpoint_name_entry.get().strip()
        
        if not url or not name:
            messagebox.showerror("Error", "Please provide both URL and endpoint name")
            return
        
        if name in self.endpoints:
            messagebox.showerror("Error", f"Endpoint '{name}' already exists")
            return
        
        config = EndpointConfig(
            url=url,
            api_key=api_key if api_key else None,
            timeout=self.timeout_var.get(),
            max_retries=self.retries_var.get(),
            scan_depth=self.scan_depth_var.get()
        )
        
        self.endpoints[name] = config
        self.ripper.add_endpoint(name, config)
        self.endpoints_listbox.insert(tk.END, f"{name} - {url}")
        
        self.log(f"✅ Added endpoint: {name}")
        
        # Clear inputs
        self.url_entry.delete(0, tk.END)
        self.api_key_entry.delete(0, tk.END)
        
    def remove_endpoint(self):
        """Remove selected endpoint"""
        selection = self.endpoints_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an endpoint to remove")
            return
        
        index = selection[0]
        endpoint_text = self.endpoints_listbox.get(index)
        name = endpoint_text.split(" - ")[0]
        
        self.endpoints_listbox.delete(index)
        del self.endpoints[name]
        self.ripper.remove_endpoint(name)
        
        self.log(f"🗑 Removed endpoint: {name}")
        
    def start_ripping(self):
        """Start the ripping process"""
        if not self.endpoints:
            messagebox.showwarning("Warning", "Please add at least one endpoint first")
            return
        
        # Check consent
        if self.require_consent_var.get() and not self.consent_given:
            if not self.show_consent_dialog():
                return
        
        self.is_ripping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Ripping in progress...", foreground="blue")
        
        self.log("🚀 Starting ripping process...")
        
        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(target=self._rip_thread)
        thread.daemon = True
        thread.start()
        
    def _rip_thread(self):
        """Thread function for ripping"""
        try:
            endpoint_names = list(self.endpoints.keys())
            results = self.ripper.rip_multiple_endpoints(endpoint_names, self.scan_depth_var.get())
            
            # Log results
            for name, success in results.items():
                if success:
                    self.log(f"✅ Successfully ripped: {name}")
                else:
                    self.log(f"❌ Failed to rip: {name}")
            
            self.root.after(0, self._ripping_complete)
            
        except Exception as e:
            self.log(f"❌ Error during ripping: {str(e)}")
            self.root.after(0, self._ripping_complete)
    
    def _ripping_complete(self):
        """Called when ripping is complete"""
        self.is_ripping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ripping completed", foreground="green")
        self.update_visualizations()
        
    def stop_ripping(self):
        """Stop the ripping process"""
        self.ripper.stop_ripping()
        self.log("⏸ Ripping stopped by user")
        self.status_label.config(text="Stopped", foreground="orange")
        
    def compare_endpoints(self):
        """Compare all configured endpoints"""
        if not self.ripper.extracted_models:
            messagebox.showinfo("Info", "No endpoints have been ripped yet")
            return
        
        comparison = self.ripper.compare_endpoints(list(self.ripper.extracted_models.keys()))
        
        # Show comparison in a new window
        compare_window = tk.Toplevel(self.root)
        compare_window.title("Endpoint Comparison")
        compare_window.geometry("800x600")
        
        text = scrolledtext.ScrolledText(compare_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text.insert(tk.END, "ENDPOINT COMPARISON\n")
        text.insert(tk.END, "=" * 80 + "\n\n")
        
        for endpoint_data in comparison['endpoints']:
            text.insert(tk.END, f"Endpoint: {endpoint_data['name']}\n")
            text.insert(tk.END, f"  Model: {endpoint_data['model_name']}\n")
            text.insert(tk.END, f"  URL: {endpoint_data['url']}\n")
            text.insert(tk.END, f"  Capabilities: {', '.join(endpoint_data['capabilities'])}\n")
            text.insert(tk.END, "\n")
        
        text.insert(tk.END, "\nMETRICS\n")
        text.insert(tk.END, "-" * 80 + "\n\n")
        text.insert(tk.END, json.dumps(comparison['metrics'], indent=2))
        
        text.config(state=tk.DISABLED)
        
    def export_model(self):
        """Export selected endpoint model"""
        selection = self.endpoints_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an endpoint to export")
            return
        
        index = selection[0]
        endpoint_text = self.endpoints_listbox.get(index)
        name = endpoint_text.split(" - ")[0]
        
        if name not in self.ripper.extracted_models:
            messagebox.showerror("Error", f"Endpoint '{name}' has not been ripped yet")
            return
        
        # Get export format
        export_format = self.export_format.get()
        
        # File extension mapping
        ext_map = {
            "JSON": ".json",
            "Python": ".py",
            "GGUF": ".gguf",
            "ONNX": ".onnx"
        }
        
        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=ext_map[export_format],
            filetypes=[(f"{export_format} files", f"*{ext_map[export_format]}"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        # Export based on format
        success = False
        if export_format == "JSON":
            success = self.ripper.export_to_json(name, filepath)
        elif export_format == "Python":
            success = self.ripper.export_to_python(name, filepath)
        elif export_format == "GGUF":
            success = self.ripper.export_to_gguf(name, filepath)
        elif export_format == "ONNX":
            success = self.ripper.export_to_onnx(name, filepath)
        
        if success:
            messagebox.showinfo("Success", f"Model exported to {filepath}")
            self.log(f"💾 Exported {name} to {filepath}")
        else:
            messagebox.showerror("Error", "Failed to export model")
            
    def update_progress(self, progress: RippingProgress):
        """Update progress bar and status"""
        self.root.after(0, lambda: self._update_progress_ui(progress))
        
    def _update_progress_ui(self, progress: RippingProgress):
        """Update progress UI (called from main thread)"""
        self.progress_var.set(progress.progress_percentage)
        self.status_label.config(text=f"{progress.current_task} ({progress.progress_percentage:.1f}%)")
        
        # Log errors and warnings
        for error in progress.errors:
            self.log(f"❌ ERROR: {error}")
        progress.errors.clear()
        
        for warning in progress.warnings:
            self.log(f"⚠️  WARNING: {warning}")
        progress.warnings.clear()
        
    def update_visualizations(self):
        """Update all visualizations"""
        # Clear all axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        # Plot 1: Response times
        self.ax1.set_title("Response Times")
        self.ax1.set_xlabel("Request #")
        self.ax1.set_ylabel("Time (s)")
        
        for name, times in self.ripper.response_times.items():
            if times:
                self.ax1.plot(range(len(times)), times, marker='o', label=name)
        
        if self.ripper.response_times:
            self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)
        
        # Plot 2: Capabilities comparison
        self.ax2.set_title("Capabilities Comparison")
        
        if self.ripper.extracted_models:
            names = []
            cap_counts = []
            
            for name, metadata in self.ripper.extracted_models.items():
                names.append(name)
                cap_counts.append(len(metadata.capabilities))
            
            self.ax2.bar(names, cap_counts, color='skyblue')
            self.ax2.set_ylabel("Number of Capabilities")
            self.ax2.tick_params(axis='x', rotation=45)
        
        # Plot 3: Token attention heatmap (placeholder with sample data)
        self.ax3.set_title("Token Attention Heatmap (Sample)")
        import numpy as np
        if self.ripper.extracted_models:
            data = np.random.rand(10, 10)
            im = self.ax3.imshow(data, cmap='hot', aspect='auto')
            self.ax3.set_xlabel("Token Position")
            self.ax3.set_ylabel("Attention Head")
        
        # Plot 4: Behavior classification (pie chart)
        self.ax4.set_title("Behavior Classification")
        
        if self.ripper.extracted_models:
            capabilities = []
            for metadata in self.ripper.extracted_models.values():
                capabilities.extend(metadata.capabilities)
            
            if capabilities:
                from collections import Counter
                cap_counts = Counter(capabilities)
                self.ax4.pie(cap_counts.values(), labels=cap_counts.keys(), autopct='%1.1f%%')
        
        self.viz_figure.tight_layout()
        self.canvas.draw()
        
        self.log("📊 Visualizations updated")
        
    def show_consent_dialog(self):
        """Show ethical consent dialog"""
        consent_window = tk.Toplevel(self.root)
        consent_window.title("Ethical Usage Agreement")
        consent_window.geometry("600x400")
        consent_window.transient(self.root)
        consent_window.grab_set()
        
        # Consent text
        text = scrolledtext.ScrolledText(consent_window, wrap=tk.WORD, height=15)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        consent_text = """ETHICAL USAGE AGREEMENT

This tool is designed for legitimate research and analysis purposes only.

By proceeding, you agree to:

1. Only scan endpoints you own or have explicit permission to access
2. Respect API rate limits and terms of service
3. Not use extracted data for malicious purposes
4. Comply with all applicable laws and regulations
5. Not attempt to extract proprietary information without authorization
6. Use this tool responsibly and ethically

IMPORTANT: Unauthorized access to computer systems may be illegal under 
laws such as the Computer Fraud and Abuse Act (CFAA) in the United States 
and similar legislation in other countries.

This tool is provided for educational and research purposes. The authors 
and contributors are not responsible for any misuse.

Do you agree to these terms?"""
        
        text.insert(tk.END, consent_text)
        text.config(state=tk.DISABLED)
        
        result = [False]
        
        def accept():
            result[0] = True
            self.consent_given = True
            consent_window.destroy()
        
        def decline():
            result[0] = False
            consent_window.destroy()
        
        # Buttons
        btn_frame = ttk.Frame(consent_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="✅ I Agree", command=accept).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Decline", command=decline).pack(side=tk.LEFT, padx=5)
        
        consent_window.wait_window()
        
        return result[0]
        
    def save_settings(self):
        """Save settings to file"""
        settings = {
            'timeout': self.timeout_var.get(),
            'max_retries': self.retries_var.get(),
            'scan_depth': self.scan_depth_var.get(),
            'adaptive_memory': self.adaptive_memory_var.get(),
            'max_memory': self.max_memory_var.get(),
            'require_consent': self.require_consent_var.get(),
            'verify_ssl': self.verify_ssl_var.get()
        }
        
        try:
            with open('ai_ripper_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Success", "Settings saved successfully")
            self.log("💾 Settings saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def log(self, message: str):
        """Add message to log"""
        timestamp = tk.datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def clear_logs(self):
        """Clear the log viewer"""
        self.log_text.delete(1.0, tk.END)
        
    def save_logs(self):
        """Save logs to file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {str(e)}")


def main():
    """Main entry point"""
    import datetime
    tk.datetime = datetime  # Add datetime to tk namespace for log function
    
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')
    
    app = AIRipperGUI(root)
    
    # Add welcome log
    app.log("🚀 AI Ripper initialized")
    app.log("📖 Add endpoints to begin extraction")
    
    root.mainloop()


if __name__ == "__main__":
    main()

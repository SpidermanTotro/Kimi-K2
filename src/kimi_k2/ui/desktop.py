"""Desktop UI for Kimi-K2 Framework using Tkinter."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Optional
import logging

from kimi_k2 import Framework, Config


logger = logging.getLogger(__name__)


class FrameworkUI:
    """Main desktop UI for the framework."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the desktop UI.
        
        Args:
            config: Framework configuration
        """
        self.config = config or Config.default()
        self.framework = Framework(self.config)
        
        self.root = tk.Tk()
        self.root.title("Kimi-K2 Unified Framework")
        self.root.geometry("1000x700")
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Config", command=self._load_config)
        file_menu.add_command(label="Save Config", command=self._save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Tutorial", command=self._show_tutorial)
        help_menu.add_command(label="About", command=self._show_about)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Animation tab
        self.animation_frame = ttk.Frame(notebook)
        notebook.add(self.animation_frame, text="Animation Suite")
        self._setup_animation_tab()
        
        # Commands tab
        self.commands_frame = ttk.Frame(notebook)
        notebook.add(self.commands_frame, text="Commands")
        self._setup_commands_tab()
        
        # Models tab
        self.models_frame = ttk.Frame(notebook)
        notebook.add(self.models_frame, text="AI Models")
        self._setup_models_tab()
        
        # Collaboration tab
        self.collab_frame = ttk.Frame(notebook)
        notebook.add(self.collab_frame, text="Collaboration")
        self._setup_collaboration_tab()
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def _setup_animation_tab(self) -> None:
        """Setup animation suite tab."""
        # Project controls
        control_frame = ttk.LabelFrame(self.animation_frame, text="Project Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W)
        self.anim_project_name = ttk.Entry(control_frame, width=30)
        self.anim_project_name.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="FPS:").grid(row=1, column=0, sticky=tk.W)
        self.anim_fps = ttk.Spinbox(control_frame, from_=15, to=60, width=28)
        self.anim_fps.set(30)
        self.anim_fps.grid(row=1, column=1, padx=5)
        
        ttk.Label(control_frame, text="Quality:").grid(row=2, column=0, sticky=tk.W)
        self.anim_quality = ttk.Combobox(control_frame, values=['draft', 'tv', 'cinema'], width=27)
        self.anim_quality.set('tv')
        self.anim_quality.grid(row=2, column=1, padx=5)
        
        ttk.Button(control_frame, text="Create Project", command=self._create_animation_project).grid(
            row=3, column=0, columnspan=2, pady=10
        )
        
        # Output area
        output_frame = ttk.LabelFrame(self.animation_frame, text="Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.anim_output = scrolledtext.ScrolledText(output_frame, height=15)
        self.anim_output.pack(fill=tk.BOTH, expand=True)
        
    def _setup_commands_tab(self) -> None:
        """Setup commands tab."""
        # Command input
        input_frame = ttk.LabelFrame(self.commands_frame, text="Command Input", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.cmd_input = ttk.Entry(input_frame)
        self.cmd_input.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.cmd_input.bind('<Return>', lambda e: self._execute_command())
        
        ttk.Button(input_frame, text="Execute", command=self._execute_command).pack(side=tk.LEFT, padx=5)
        
        # Output area
        output_frame = ttk.LabelFrame(self.commands_frame, text="Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.cmd_output = scrolledtext.ScrolledText(output_frame, height=20)
        self.cmd_output.pack(fill=tk.BOTH, expand=True)
        
    def _setup_models_tab(self) -> None:
        """Setup AI models tab."""
        # Model selection
        control_frame = ttk.LabelFrame(self.models_frame, text="Model Selection", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Model:").grid(row=0, column=0, sticky=tk.W)
        self.model_select = ttk.Combobox(control_frame, values=['lightweight', 'heavy'], width=27)
        self.model_select.set('lightweight')
        self.model_select.grid(row=0, column=1, padx=5)
        
        ttk.Button(control_frame, text="Load Model", command=self._load_model).grid(
            row=0, column=2, padx=5
        )
        
        # Generation controls
        gen_frame = ttk.LabelFrame(self.models_frame, text="Text Generation", padding=10)
        gen_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(gen_frame, text="Prompt:").pack(anchor=tk.W)
        self.model_prompt = ttk.Entry(gen_frame)
        self.model_prompt.pack(fill=tk.X, pady=5)
        
        ttk.Button(gen_frame, text="Generate", command=self._generate_text).pack()
        
        # Output area
        output_frame = ttk.LabelFrame(self.models_frame, text="Generated Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.model_output = scrolledtext.ScrolledText(output_frame, height=15)
        self.model_output.pack(fill=tk.BOTH, expand=True)
        
    def _setup_collaboration_tab(self) -> None:
        """Setup collaboration tab."""
        info_label = ttk.Label(
            self.collab_frame,
            text="Collaboration features will be enabled in a future version.\n\n"
                 "Enable in config to use multi-user features.",
            justify=tk.CENTER
        )
        info_label.pack(expand=True)
        
    def _create_animation_project(self) -> None:
        """Create a new animation project."""
        project_name = self.anim_project_name.get()
        if not project_name:
            messagebox.showwarning("Warning", "Please enter a project name")
            return
            
        try:
            if not self.framework._initialized:
                self.framework.initialize()
                
            animation_suite = self.framework.get_module('animation')
            project = animation_suite.create_project(
                name=project_name,
                fps=int(self.anim_fps.get()),
                quality=self.anim_quality.get()
            )
            
            self.anim_output.insert(tk.END, f"✓ Created project: {project_name}\n")
            self.anim_output.insert(tk.END, f"  FPS: {project.fps}, Quality: {project.quality.value}\n\n")
            self.status_bar.config(text=f"Created project: {project_name}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _execute_command(self) -> None:
        """Execute a command."""
        command = self.cmd_input.get()
        if not command:
            return
            
        try:
            if not self.framework._initialized:
                self.framework.initialize()
                
            cmd_interface = self.framework.get_module('commands')
            result = cmd_interface.execute_command(command)
            
            self.cmd_output.insert(tk.END, f"$ {command}\n")
            if result['success']:
                self.cmd_output.insert(tk.END, f"{result['result']}\n\n")
            else:
                self.cmd_output.insert(tk.END, f"Error: {result['error']}\n\n")
                
            self.cmd_input.delete(0, tk.END)
            self.status_bar.config(text="Command executed")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _load_model(self) -> None:
        """Load a model."""
        model_name = self.model_select.get()
        
        try:
            if not self.framework._initialized:
                self.framework.initialize()
                
            model_manager = self.framework.get_module('models')
            model_manager.load_model(model_name)
            
            messagebox.showinfo("Success", f"Model '{model_name}' loaded successfully")
            self.status_bar.config(text=f"Model loaded: {model_name}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _generate_text(self) -> None:
        """Generate text using AI model."""
        prompt = self.model_prompt.get()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt")
            return
            
        try:
            if not self.framework._initialized:
                self.framework.initialize()
                
            model_manager = self.framework.get_module('models')
            result = model_manager.generate(prompt)
            
            self.model_output.insert(tk.END, f"Prompt: {prompt}\n")
            self.model_output.insert(tk.END, f"Response: {result}\n\n")
            self.status_bar.config(text="Text generated")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _load_config(self) -> None:
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config = Config.load_from_file(filename)
                messagebox.showinfo("Success", "Configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")
                
    def _save_config(self) -> None:
        """Save configuration to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config.save_to_file(filename)
                messagebox.showinfo("Success", "Configuration saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {e}")
                
    def _show_tutorial(self) -> None:
        """Show tutorial dialog."""
        tutorial_text = """
        Kimi-K2 Framework Tutorial
        
        1. Animation Suite:
           - Create projects with custom FPS and quality settings
           - Use timeline editor for precise control
           - Apply AI optimizations for better results
           
        2. Commands:
           - Execute Linux-style commands
           - Generate scripts using AI
           - Automate workflows
           
        3. AI Models:
           - Choose between lightweight and heavy models
           - Generate text with customizable parameters
           - Manage model memory efficiently
           
        4. Collaboration:
           - Share projects with team members
           - Real-time synchronization
           - Multi-user editing support
        """
        messagebox.showinfo("Tutorial", tutorial_text)
        
    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = """
        Kimi-K2 Unified Framework v1.0.0
        
        A comprehensive AI framework consolidating:
        - Animation tools
        - Command interfaces
        - GPT models
        - Collaboration features
        
        © 2025 Kimi Team
        """
        messagebox.showinfo("About", about_text)
        
    def run(self) -> None:
        """Run the UI main loop."""
        self.root.mainloop()
        
    def shutdown(self) -> None:
        """Shutdown the framework."""
        if self.framework._initialized:
            self.framework.shutdown()


def main():
    """Main entry point for desktop UI."""
    ui = FrameworkUI()
    try:
        ui.run()
    finally:
        ui.shutdown()


if __name__ == '__main__':
    main()

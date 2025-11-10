"""
Linux-style Command System

Provides a virtual file system with Linux-like commands for file management.
Supports aliasing and scripting capabilities.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable
import json


class VirtualFileSystem:
    """Virtual file system for command operations"""
    
    def __init__(self, root_path: str = "/tmp/kimi_vfs"):
        """Initialize virtual file system
        
        Args:
            root_path: Root directory for the virtual file system
        """
        self.root_path = Path(root_path)
        self.current_dir = self.root_path
        self._ensure_root()
    
    def _ensure_root(self):
        """Ensure root directory exists"""
        self.root_path.mkdir(parents=True, exist_ok=True)
        self.current_dir = self.root_path
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to current directory
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved absolute path
        """
        if not path:
            return self.current_dir
        
        p = Path(path)
        if p.is_absolute():
            # Make it relative to root
            return self.root_path / p.relative_to("/")
        return self.current_dir / p
    
    def get_current_dir(self) -> str:
        """Get current directory relative to root"""
        try:
            rel_path = str(self.current_dir.relative_to(self.root_path))
            if rel_path == ".":
                return "/"
            return "/" + rel_path
        except ValueError:
            return "/"


class CommandSystem:
    """Linux-style command system with aliasing and scripting support"""
    
    def __init__(self, vfs: Optional[VirtualFileSystem] = None):
        """Initialize command system
        
        Args:
            vfs: Virtual file system instance (creates new one if None)
        """
        self.vfs = vfs or VirtualFileSystem()
        self.aliases: Dict[str, str] = {}
        self.commands: Dict[str, Callable] = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "pwd": self.cmd_pwd,
            "mkdir": self.cmd_mkdir,
            "rm": self.cmd_rm,
            "cat": self.cmd_cat,
            "echo": self.cmd_echo,
            "touch": self.cmd_touch,
            "cp": self.cmd_cp,
            "mv": self.cmd_mv,
            "alias": self.cmd_alias,
            "help": self.cmd_help,
        }
    
    def execute(self, command_line: str) -> str:
        """Execute a command
        
        Args:
            command_line: Command string to execute
            
        Returns:
            Command output
        """
        if not command_line.strip():
            return ""
        
        parts = command_line.strip().split()
        cmd = parts[0]
        args = parts[1:]
        
        # Check for alias
        if cmd in self.aliases:
            # Replace alias with actual command
            alias_cmd = self.aliases[cmd]
            command_line = alias_cmd + " " + " ".join(args)
            return self.execute(command_line)
        
        if cmd in self.commands:
            try:
                return self.commands[cmd](args)
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return f"Command not found: {cmd}"
    
    def cmd_ls(self, args: List[str]) -> str:
        """List directory contents"""
        path = args[0] if args else "."
        target = self.vfs._resolve_path(path)
        
        if not target.exists():
            return f"ls: cannot access '{path}': No such file or directory"
        
        if target.is_file():
            return target.name
        
        items = []
        for item in sorted(target.iterdir()):
            name = item.name
            if item.is_dir():
                name += "/"
            items.append(name)
        
        return "\n".join(items) if items else ""
    
    def cmd_cd(self, args: List[str]) -> str:
        """Change directory"""
        if not args:
            self.vfs.current_dir = self.vfs.root_path
            return ""
        
        target = self.vfs._resolve_path(args[0])
        
        if not target.exists():
            return f"cd: {args[0]}: No such file or directory"
        
        if not target.is_dir():
            return f"cd: {args[0]}: Not a directory"
        
        self.vfs.current_dir = target
        return ""
    
    def cmd_pwd(self, args: List[str]) -> str:
        """Print working directory"""
        return self.vfs.get_current_dir()
    
    def cmd_mkdir(self, args: List[str]) -> str:
        """Create directory"""
        if not args:
            return "mkdir: missing operand"
        
        for path in args:
            target = self.vfs._resolve_path(path)
            try:
                target.mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                return f"mkdir: cannot create directory '{path}': File exists"
        
        return ""
    
    def cmd_rm(self, args: List[str]) -> str:
        """Remove files or directories"""
        if not args:
            return "rm: missing operand"
        
        recursive = "-r" in args or "-rf" in args
        force = "-f" in args or "-rf" in args
        
        paths = [a for a in args if not a.startswith("-")]
        
        for path in paths:
            target = self.vfs._resolve_path(path)
            
            if not target.exists():
                if not force:
                    return f"rm: cannot remove '{path}': No such file or directory"
                continue
            
            try:
                if target.is_dir():
                    if not recursive:
                        return f"rm: cannot remove '{path}': Is a directory"
                    shutil.rmtree(target)
                else:
                    target.unlink()
            except Exception as e:
                if not force:
                    return f"rm: cannot remove '{path}': {str(e)}"
        
        return ""
    
    def cmd_cat(self, args: List[str]) -> str:
        """Display file contents"""
        if not args:
            return "cat: missing operand"
        
        contents = []
        for path in args:
            target = self.vfs._resolve_path(path)
            
            if not target.exists():
                return f"cat: {path}: No such file or directory"
            
            if target.is_dir():
                return f"cat: {path}: Is a directory"
            
            try:
                contents.append(target.read_text())
            except Exception as e:
                return f"cat: {path}: {str(e)}"
        
        return "\n".join(contents)
    
    def cmd_echo(self, args: List[str]) -> str:
        """Echo arguments"""
        if not args:
            return ""
        
        text = " ".join(args)
        
        # Check for redirect
        if ">" in text:
            parts = text.split(">", 1)
            content = parts[0].strip()
            filepath = parts[1].strip()
            
            target = self.vfs._resolve_path(filepath)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content + "\n")
            return ""
        
        return text
    
    def cmd_touch(self, args: List[str]) -> str:
        """Create empty file"""
        if not args:
            return "touch: missing operand"
        
        for path in args:
            target = self.vfs._resolve_path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.touch()
        
        return ""
    
    def cmd_cp(self, args: List[str]) -> str:
        """Copy files or directories"""
        if len(args) < 2:
            return "cp: missing file operand"
        
        recursive = "-r" in args
        actual_args = [a for a in args if not a.startswith("-")]
        
        if len(actual_args) < 2:
            return "cp: missing destination file operand"
        
        source = self.vfs._resolve_path(actual_args[0])
        dest = self.vfs._resolve_path(actual_args[1])
        
        if not source.exists():
            return f"cp: cannot stat '{actual_args[0]}': No such file or directory"
        
        try:
            if source.is_dir():
                if not recursive:
                    return f"cp: -r not specified; omitting directory '{actual_args[0]}'"
                shutil.copytree(source, dest)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        except Exception as e:
            return f"cp: {str(e)}"
        
        return ""
    
    def cmd_mv(self, args: List[str]) -> str:
        """Move/rename files or directories"""
        if len(args) < 2:
            return "mv: missing file operand"
        
        source = self.vfs._resolve_path(args[0])
        dest = self.vfs._resolve_path(args[1])
        
        if not source.exists():
            return f"mv: cannot stat '{args[0]}': No such file or directory"
        
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source, dest)
        except Exception as e:
            return f"mv: {str(e)}"
        
        return ""
    
    def cmd_alias(self, args: List[str]) -> str:
        """Create command alias"""
        if not args:
            # List all aliases
            if not self.aliases:
                return ""
            return "\n".join([f"{k}='{v}'" for k, v in self.aliases.items()])
        
        alias_def = " ".join(args)
        if "=" not in alias_def:
            # Show specific alias
            if alias_def in self.aliases:
                return f"{alias_def}='{self.aliases[alias_def]}'"
            return f"alias: {alias_def}: not found"
        
        # Create alias
        parts = alias_def.split("=", 1)
        name = parts[0].strip()
        command = parts[1].strip().strip("'\"")
        
        self.aliases[name] = command
        return ""
    
    def cmd_help(self, args: List[str]) -> str:
        """Display help information"""
        help_text = """Available commands:
  ls [path]              - List directory contents
  cd [path]              - Change directory
  pwd                    - Print working directory
  mkdir <path>...        - Create directories
  rm [-rf] <path>...     - Remove files/directories
  cat <file>...          - Display file contents
  echo <text> [> file]   - Echo text (optionally to file)
  touch <file>...        - Create empty files
  cp [-r] <src> <dest>   - Copy files/directories
  mv <src> <dest>        - Move/rename files/directories
  alias [name=command]   - Create or list aliases
  help                   - Show this help message
"""
        return help_text.strip()
    
    def execute_script(self, script_path: str) -> List[str]:
        """Execute commands from a script file
        
        Args:
            script_path: Path to script file
            
        Returns:
            List of outputs from each command
        """
        target = self.vfs._resolve_path(script_path)
        
        if not target.exists():
            return [f"Script not found: {script_path}"]
        
        script_content = target.read_text()
        outputs = []
        
        for line in script_content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                output = self.execute(line)
                if output:
                    outputs.append(output)
        
        return outputs


__all__ = ["CommandSystem", "VirtualFileSystem"]

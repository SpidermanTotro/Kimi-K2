"""Linux-style Command System with scripting capabilities"""

import os
from typing import Dict, List, Any, Optional, Callable
import shlex


class CommandSystem:
    """
    Linux-style command interface supporting commands like ls, mkdir, cd, etc.,
    with scripting capabilities.
    """

    def __init__(self, virtual_fs: bool = True):
        """
        Initialize the command system.

        Args:
            virtual_fs: If True, use a virtual filesystem. If False, use real filesystem.
        """
        self.virtual_fs = virtual_fs
        self.cwd = "/"
        self.filesystem = {"/": {"type": "dir", "contents": {}}}
        self.command_history = []
        self.variables = {}
        
        # Register built-in commands
        self.commands: Dict[str, Callable] = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "pwd": self._cmd_pwd,
            "mkdir": self._cmd_mkdir,
            "rm": self._cmd_rm,
            "touch": self._cmd_touch,
            "cat": self._cmd_cat,
            "echo": self._cmd_echo,
            "set": self._cmd_set,
            "get": self._cmd_get,
            "help": self._cmd_help,
        }

    def execute(self, command: str) -> Dict[str, Any]:
        """
        Execute a command or script.

        Args:
            command: Command string to execute

        Returns:
            Dictionary with execution results
        """
        if not command.strip():
            return {"status": "success", "output": ""}

        # Add to history
        self.command_history.append(command)

        # Parse command
        try:
            parts = shlex.split(command)
        except ValueError as e:
            return {"status": "error", "error": f"Parse error: {e}"}

        if not parts:
            return {"status": "success", "output": ""}

        cmd_name = parts[0]
        args = parts[1:]

        # Execute command
        if cmd_name in self.commands:
            try:
                result = self.commands[cmd_name](args)
                return {"status": "success", "output": result}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        else:
            return {"status": "error", "error": f"Command not found: {cmd_name}"}

    def execute_script(self, script: str) -> List[Dict[str, Any]]:
        """
        Execute a multi-line script.

        Args:
            script: Multi-line script string

        Returns:
            List of results for each command
        """
        results = []
        lines = script.strip().split("\n")

        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            result = self.execute(line)
            results.append(result)

            # Stop on error if desired
            if result["status"] == "error":
                break

        return results

    def _normalize_path(self, path: str) -> str:
        """Normalize a path relative to current directory."""
        if path.startswith("/"):
            return path
        
        if self.cwd == "/":
            return "/" + path
        else:
            return self.cwd + "/" + path

    def _get_path_parts(self, path: str) -> List[str]:
        """Split path into parts."""
        return [p for p in path.split("/") if p]

    def _navigate_to_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Navigate to a path in the virtual filesystem."""
        if path == "/":
            return self.filesystem["/"]

        parts = self._get_path_parts(path)
        current = self.filesystem["/"]

        for part in parts:
            if current["type"] != "dir":
                return None
            if part not in current["contents"]:
                return None
            current = current["contents"][part]

        return current

    def _cmd_ls(self, args: List[str]) -> str:
        """List directory contents."""
        path = args[0] if args else self.cwd
        path = self._normalize_path(path)

        node = self._navigate_to_path(path)
        if node is None:
            raise FileNotFoundError(f"Path not found: {path}")
        if node["type"] != "dir":
            raise NotADirectoryError(f"Not a directory: {path}")

        items = sorted(node["contents"].keys())
        return "\n".join(items) if items else ""

    def _cmd_cd(self, args: List[str]) -> str:
        """Change directory."""
        if not args:
            self.cwd = "/"
            return ""

        path = self._normalize_path(args[0])
        node = self._navigate_to_path(path)

        if node is None:
            raise FileNotFoundError(f"Directory not found: {path}")
        if node["type"] != "dir":
            raise NotADirectoryError(f"Not a directory: {path}")

        self.cwd = path
        return ""

    def _cmd_pwd(self, args: List[str]) -> str:
        """Print working directory."""
        return self.cwd

    def _cmd_mkdir(self, args: List[str]) -> str:
        """Create a directory."""
        if not args:
            raise ValueError("mkdir: missing operand")

        for arg in args:
            path = self._normalize_path(arg)
            parts = self._get_path_parts(path)

            if not parts:
                continue

            # Navigate to parent
            parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
            parent = self._navigate_to_path(parent_path)

            if parent is None:
                raise FileNotFoundError(f"Parent directory not found: {parent_path}")
            if parent["type"] != "dir":
                raise NotADirectoryError(f"Parent is not a directory: {parent_path}")

            # Create directory
            dir_name = parts[-1]
            if dir_name in parent["contents"]:
                raise FileExistsError(f"Directory already exists: {path}")

            parent["contents"][dir_name] = {"type": "dir", "contents": {}}

        return ""

    def _cmd_rm(self, args: List[str]) -> str:
        """Remove files or directories."""
        if not args:
            raise ValueError("rm: missing operand")

        for arg in args:
            path = self._normalize_path(arg)
            parts = self._get_path_parts(path)

            if not parts:
                raise ValueError("Cannot remove root directory")

            # Navigate to parent
            parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
            parent = self._navigate_to_path(parent_path)

            if parent is None or parent["type"] != "dir":
                raise FileNotFoundError(f"Parent directory not found: {parent_path}")

            # Remove item
            item_name = parts[-1]
            if item_name not in parent["contents"]:
                raise FileNotFoundError(f"File not found: {path}")

            del parent["contents"][item_name]

        return ""

    def _cmd_touch(self, args: List[str]) -> str:
        """Create empty files."""
        if not args:
            raise ValueError("touch: missing operand")

        for arg in args:
            path = self._normalize_path(arg)
            parts = self._get_path_parts(path)

            if not parts:
                continue

            # Navigate to parent
            parent_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
            parent = self._navigate_to_path(parent_path)

            if parent is None or parent["type"] != "dir":
                raise FileNotFoundError(f"Parent directory not found: {parent_path}")

            # Create or update file
            file_name = parts[-1]
            if file_name not in parent["contents"]:
                parent["contents"][file_name] = {"type": "file", "content": ""}

        return ""

    def _cmd_cat(self, args: List[str]) -> str:
        """Display file contents."""
        if not args:
            raise ValueError("cat: missing operand")

        outputs = []
        for arg in args:
            path = self._normalize_path(arg)
            node = self._navigate_to_path(path)

            if node is None:
                raise FileNotFoundError(f"File not found: {path}")
            if node["type"] != "file":
                raise IsADirectoryError(f"Is a directory: {path}")

            outputs.append(node.get("content", ""))

        return "\n".join(outputs)

    def _cmd_echo(self, args: List[str]) -> str:
        """Echo arguments."""
        return " ".join(args)

    def _cmd_set(self, args: List[str]) -> str:
        """Set a variable."""
        if len(args) < 2:
            raise ValueError("set: requires variable name and value")

        var_name = args[0]
        var_value = " ".join(args[1:])
        self.variables[var_name] = var_value
        return ""

    def _cmd_get(self, args: List[str]) -> str:
        """Get a variable value."""
        if not args:
            # List all variables
            return "\n".join(f"{k}={v}" for k, v in self.variables.items())

        var_name = args[0]
        if var_name not in self.variables:
            raise KeyError(f"Variable not found: {var_name}")

        return self.variables[var_name]

    def _cmd_help(self, args: List[str]) -> str:
        """Display help information."""
        if args:
            cmd = args[0]
            help_text = {
                "ls": "List directory contents",
                "cd": "Change directory",
                "pwd": "Print working directory",
                "mkdir": "Create directories",
                "rm": "Remove files or directories",
                "touch": "Create empty files",
                "cat": "Display file contents",
                "echo": "Echo arguments",
                "set": "Set a variable",
                "get": "Get a variable value",
                "help": "Display help information",
            }
            return help_text.get(cmd, f"No help available for: {cmd}")
        else:
            return "Available commands: " + ", ".join(sorted(self.commands.keys()))

    def get_history(self) -> List[str]:
        """Get command history."""
        return self.command_history.copy()

    def register_command(self, name: str, handler: Callable) -> None:
        """
        Register a custom command.

        Args:
            name: Command name
            handler: Function to handle the command (takes List[str] args, returns str)
        """
        self.commands[name] = handler

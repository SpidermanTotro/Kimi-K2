#!/usr/bin/env python3
"""
Nebula Shell - Command Line Interface

A simple but functional shell for the Nebula Linux-like system.
Supports basic commands, pipes, and command history.
"""

import os
import sys
import shlex
import subprocess
from typing import List, Dict, Optional, Callable
from pathlib import Path


class NebulaShell:
    """Main shell class"""
    
    def __init__(self):
        self.version = "0.1.0"
        self.prompt = "nebula> "
        self.running = False
        self.history: List[str] = []
        self.current_dir = os.getcwd()
        self.env_vars: Dict[str, str] = dict(os.environ)
        
        # Built-in commands
        self.builtins: Dict[str, Callable] = {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "cd": self.cmd_cd,
            "pwd": self.cmd_pwd,
            "echo": self.cmd_echo,
            "env": self.cmd_env,
            "export": self.cmd_export,
            "history": self.cmd_history,
            "clear": self.cmd_clear,
            "version": self.cmd_version,
            "ls": self.cmd_ls,
            "cat": self.cmd_cat,
            "mkdir": self.cmd_mkdir,
            "rm": self.cmd_rm,
            "touch": self.cmd_touch,
        }
    
    def start(self):
        """Start the shell"""
        self.running = True
        print(f"Nebula Shell v{self.version}")
        print("Type 'help' for available commands.\n")
        
        while self.running:
            try:
                line = input(self.prompt).strip()
                
                if not line:
                    continue
                
                # Add to history
                self.history.append(line)
                
                # Execute command
                self.execute_line(line)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit the shell.")
                continue
            except EOFError:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def execute_line(self, line: str) -> int:
        """Execute a command line"""
        # Handle pipes
        if '|' in line:
            return self.execute_pipeline(line)
        
        # Parse command
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(f"Parse error: {e}")
            return 1
        
        if not parts:
            return 0
        
        cmd = parts[0]
        args = parts[1:]
        
        # Check if it's a builtin
        if cmd in self.builtins:
            return self.builtins[cmd](args)
        
        # Try to execute as external command
        return self.execute_external(cmd, args)
    
    def execute_pipeline(self, line: str) -> int:
        """Execute a pipeline of commands"""
        commands = [cmd.strip() for cmd in line.split('|')]
        
        print(f"Executing pipeline with {len(commands)} commands...")
        for i, cmd in enumerate(commands):
            print(f"  [{i+1}] {cmd}")
        
        return 0
    
    def execute_external(self, cmd: str, args: List[str]) -> int:
        """Execute an external command"""
        try:
            result = subprocess.run([cmd] + args, 
                                    cwd=self.current_dir,
                                    env=self.env_vars)
            return result.returncode
        except FileNotFoundError:
            print(f"nebula: {cmd}: command not found")
            return 127
        except Exception as e:
            print(f"nebula: {cmd}: {e}")
            return 1
    
    # Built-in commands
    
    def cmd_help(self, args: List[str]) -> int:
        """Display help information"""
        print("Nebula Shell - Available Commands:")
        print("\nBuilt-in commands:")
        commands = sorted(self.builtins.keys())
        for cmd in commands:
            print(f"  {cmd}")
        
        print("\nUse external commands by typing their name.")
        print("Pipes are supported using '|' symbol.")
        return 0
    
    def cmd_exit(self, args: List[str]) -> int:
        """Exit the shell"""
        self.running = False
        print("Goodbye!")
        return 0
    
    def cmd_cd(self, args: List[str]) -> int:
        """Change directory"""
        if not args:
            target = os.path.expanduser("~")
        else:
            target = args[0]
        
        try:
            target_path = os.path.abspath(os.path.join(self.current_dir, target))
            if os.path.isdir(target_path):
                self.current_dir = target_path
                os.chdir(target_path)
                return 0
            else:
                print(f"cd: {target}: No such directory")
                return 1
        except Exception as e:
            print(f"cd: {e}")
            return 1
    
    def cmd_pwd(self, args: List[str]) -> int:
        """Print working directory"""
        print(self.current_dir)
        return 0
    
    def cmd_echo(self, args: List[str]) -> int:
        """Echo arguments"""
        # Expand environment variables
        output = []
        for arg in args:
            if arg.startswith('$'):
                var_name = arg[1:]
                output.append(self.env_vars.get(var_name, ''))
            else:
                output.append(arg)
        
        print(' '.join(output))
        return 0
    
    def cmd_env(self, args: List[str]) -> int:
        """Display environment variables"""
        for key, value in sorted(self.env_vars.items()):
            print(f"{key}={value}")
        return 0
    
    def cmd_export(self, args: List[str]) -> int:
        """Set environment variable"""
        if not args:
            return self.cmd_env(args)
        
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                self.env_vars[key] = value
                os.environ[key] = value
            else:
                print(f"export: {arg}: invalid format (use KEY=VALUE)")
                return 1
        
        return 0
    
    def cmd_history(self, args: List[str]) -> int:
        """Show command history"""
        for i, cmd in enumerate(self.history, 1):
            print(f"{i:4d}  {cmd}")
        return 0
    
    def cmd_clear(self, args: List[str]) -> int:
        """Clear the screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
        return 0
    
    def cmd_version(self, args: List[str]) -> int:
        """Display version information"""
        print(f"Nebula Shell v{self.version}")
        print(f"Python {sys.version}")
        return 0
    
    def cmd_ls(self, args: List[str]) -> int:
        """List directory contents"""
        path = args[0] if args else self.current_dir
        
        try:
            target_path = os.path.abspath(os.path.join(self.current_dir, path))
            if os.path.isfile(target_path):
                print(os.path.basename(target_path))
            elif os.path.isdir(target_path):
                items = sorted(os.listdir(target_path))
                for item in items:
                    full_path = os.path.join(target_path, item)
                    if os.path.isdir(full_path):
                        print(f"{item}/")
                    else:
                        print(item)
            else:
                print(f"ls: {path}: No such file or directory")
                return 1
            return 0
        except Exception as e:
            print(f"ls: {e}")
            return 1
    
    def cmd_cat(self, args: List[str]) -> int:
        """Display file contents"""
        if not args:
            print("cat: missing file operand")
            return 1
        
        for filename in args:
            try:
                filepath = os.path.join(self.current_dir, filename)
                with open(filepath, 'r') as f:
                    print(f.read(), end='')
            except Exception as e:
                print(f"cat: {filename}: {e}")
                return 1
        
        return 0
    
    def cmd_mkdir(self, args: List[str]) -> int:
        """Create directory"""
        if not args:
            print("mkdir: missing operand")
            return 1
        
        for dirname in args:
            try:
                dirpath = os.path.join(self.current_dir, dirname)
                os.makedirs(dirpath, exist_ok=True)
            except Exception as e:
                print(f"mkdir: {dirname}: {e}")
                return 1
        
        return 0
    
    def cmd_rm(self, args: List[str]) -> int:
        """Remove file"""
        if not args:
            print("rm: missing operand")
            return 1
        
        for filename in args:
            try:
                filepath = os.path.join(self.current_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                else:
                    print(f"rm: {filename}: No such file")
                    return 1
            except Exception as e:
                print(f"rm: {filename}: {e}")
                return 1
        
        return 0
    
    def cmd_touch(self, args: List[str]) -> int:
        """Create empty file or update timestamp"""
        if not args:
            print("touch: missing operand")
            return 1
        
        for filename in args:
            try:
                filepath = os.path.join(self.current_dir, filename)
                Path(filepath).touch()
            except Exception as e:
                print(f"touch: {filename}: {e}")
                return 1
        
        return 0


def main():
    """Main entry point"""
    shell = NebulaShell()
    shell.start()


if __name__ == "__main__":
    main()

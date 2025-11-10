"""Tests for Command System"""

import pytest
from kimi_k2.commands import CommandSystem


class TestCommandSystem:
    """Test suite for CommandSystem class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cmd = CommandSystem(virtual_fs=True)

    def test_initialization(self):
        """Test command system initialization."""
        assert self.cmd is not None
        assert self.cmd.cwd == "/"
        assert "/" in self.cmd.filesystem

    def test_pwd(self):
        """Test pwd command."""
        result = self.cmd.execute("pwd")
        assert result["status"] == "success"
        assert result["output"] == "/"

    def test_mkdir(self):
        """Test mkdir command."""
        result = self.cmd.execute("mkdir test_dir")
        assert result["status"] == "success"
        
        result = self.cmd.execute("ls")
        assert "test_dir" in result["output"]

    def test_mkdir_nested(self):
        """Test creating nested directories."""
        self.cmd.execute("mkdir parent")
        result = self.cmd.execute("mkdir parent/child")
        assert result["status"] == "success"

    def test_cd(self):
        """Test cd command."""
        self.cmd.execute("mkdir test_dir")
        result = self.cmd.execute("cd test_dir")
        assert result["status"] == "success"
        
        result = self.cmd.execute("pwd")
        assert result["output"] == "/test_dir"

    def test_cd_parent(self):
        """Test changing to parent directory."""
        self.cmd.execute("mkdir test_dir")
        self.cmd.execute("cd test_dir")
        self.cmd.execute("cd /")
        
        result = self.cmd.execute("pwd")
        assert result["output"] == "/"

    def test_ls_empty(self):
        """Test ls on empty directory."""
        result = self.cmd.execute("ls")
        assert result["status"] == "success"
        assert result["output"] == ""

    def test_ls_with_files(self):
        """Test ls with files."""
        self.cmd.execute("mkdir dir1")
        self.cmd.execute("mkdir dir2")
        self.cmd.execute("touch file1")
        
        result = self.cmd.execute("ls")
        assert "dir1" in result["output"]
        assert "dir2" in result["output"]
        assert "file1" in result["output"]

    def test_touch(self):
        """Test touch command."""
        result = self.cmd.execute("touch testfile")
        assert result["status"] == "success"
        
        result = self.cmd.execute("ls")
        assert "testfile" in result["output"]

    def test_rm_file(self):
        """Test removing a file."""
        self.cmd.execute("touch testfile")
        result = self.cmd.execute("rm testfile")
        assert result["status"] == "success"
        
        result = self.cmd.execute("ls")
        assert "testfile" not in result["output"]

    def test_rm_directory(self):
        """Test removing a directory."""
        self.cmd.execute("mkdir testdir")
        result = self.cmd.execute("rm testdir")
        assert result["status"] == "success"
        
        result = self.cmd.execute("ls")
        assert "testdir" not in result["output"]

    def test_echo(self):
        """Test echo command."""
        result = self.cmd.execute("echo Hello World")
        assert result["status"] == "success"
        assert result["output"] == "Hello World"

    def test_set_get_variable(self):
        """Test setting and getting variables."""
        result = self.cmd.execute("set myvar test_value")
        assert result["status"] == "success"
        
        result = self.cmd.execute("get myvar")
        assert result["status"] == "success"
        assert result["output"] == "test_value"

    def test_get_all_variables(self):
        """Test getting all variables."""
        self.cmd.execute("set var1 value1")
        self.cmd.execute("set var2 value2")
        
        result = self.cmd.execute("get")
        assert "var1=value1" in result["output"]
        assert "var2=value2" in result["output"]

    def test_help(self):
        """Test help command."""
        result = self.cmd.execute("help")
        assert result["status"] == "success"
        assert "ls" in result["output"]
        assert "cd" in result["output"]

    def test_help_specific_command(self):
        """Test help for specific command."""
        result = self.cmd.execute("help ls")
        assert result["status"] == "success"
        assert "List directory" in result["output"]

    def test_execute_script(self):
        """Test executing multi-line script."""
        script = """
        mkdir test_dir
        cd test_dir
        touch file1
        touch file2
        """
        results = self.cmd.execute_script(script)
        
        # All commands should succeed
        for result in results:
            assert result["status"] == "success"
        
        # Check final state
        result = self.cmd.execute("pwd")
        assert "/test_dir" in result["output"]

    def test_execute_script_with_comments(self):
        """Test script execution with comments."""
        script = """
        # This is a comment
        mkdir test_dir
        # Another comment
        cd test_dir
        """
        results = self.cmd.execute_script(script)
        
        # Only non-comment commands should be in results
        assert len(results) == 2

    def test_command_history(self):
        """Test command history tracking."""
        self.cmd.execute("pwd")
        self.cmd.execute("ls")
        self.cmd.execute("echo test")
        
        history = self.cmd.get_history()
        assert len(history) == 3
        assert "pwd" in history
        assert "ls" in history
        assert "echo test" in history

    def test_invalid_command(self):
        """Test executing invalid command."""
        result = self.cmd.execute("nonexistent_command")
        assert result["status"] == "error"
        assert "not found" in result["error"]

    def test_register_custom_command(self):
        """Test registering custom command."""
        def custom_handler(args):
            return "custom output"
        
        self.cmd.register_command("custom", custom_handler)
        result = self.cmd.execute("custom")
        assert result["status"] == "success"
        assert result["output"] == "custom output"

    def test_error_handling(self):
        """Test error handling for invalid operations."""
        # Try to cd into non-existent directory
        result = self.cmd.execute("cd nonexistent")
        assert result["status"] == "error"
        
        # Try to remove non-existent file
        result = self.cmd.execute("rm nonexistent")
        assert result["status"] == "error"

    def test_cat_command(self):
        """Test cat command (file reading is limited in virtual fs)."""
        # In the virtual fs, we can test basic cat functionality
        result = self.cmd.execute("cat")
        assert result["status"] == "error"  # Missing operand

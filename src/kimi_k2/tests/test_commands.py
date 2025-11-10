"""Tests for command interface functionality."""

import pytest
from pathlib import Path

from kimi_k2.commands.interface import CommandInterface, Command
from kimi_k2.core.config import CommandsConfig


class TestCommandInterface:
    """Test command interface functionality."""
    
    @pytest.fixture
    def cmd_interface(self, tmp_path):
        """Create command interface for testing."""
        config = CommandsConfig(script_dir=str(tmp_path / "scripts"))
        return CommandInterface(config)
        
    def test_interface_initialization(self, cmd_interface):
        """Test command interface initialization."""
        assert cmd_interface is not None
        assert cmd_interface.script_dir.exists()
        
    def test_builtin_commands_registered(self, cmd_interface):
        """Test builtin commands are registered."""
        assert 'ls' in cmd_interface.commands
        assert 'help' in cmd_interface.commands
        assert 'gen-script' in cmd_interface.commands
        
    def test_register_custom_command(self, cmd_interface):
        """Test registering custom command."""
        def custom_handler(args):
            return "custom result"
            
        cmd_interface.register_command(
            name="custom",
            description="Custom command",
            handler=custom_handler
        )
        
        assert 'custom' in cmd_interface.commands
        
    def test_execute_command(self, cmd_interface):
        """Test executing a command."""
        result = cmd_interface.execute_command("help")
        
        assert result['success'] is True
        assert 'Available Commands' in result['result']
        
    def test_execute_unknown_command(self, cmd_interface):
        """Test executing unknown command."""
        result = cmd_interface.execute_command("unknown_cmd")
        
        assert result['success'] is False
        assert 'Unknown command' in result['error']
        
    def test_execute_empty_command(self, cmd_interface):
        """Test executing empty command."""
        result = cmd_interface.execute_command("")
        
        assert result['success'] is False
        assert 'Empty command' in result['error']
        
    def test_command_history(self, cmd_interface):
        """Test command history tracking."""
        cmd_interface.execute_command("help")
        cmd_interface.execute_command("ls")
        
        assert len(cmd_interface.command_history) == 2
        assert cmd_interface.command_history[0] == "help"
        assert cmd_interface.command_history[1] == "ls"


class TestScriptGenerator:
    """Test script generator functionality."""
    
    @pytest.fixture
    def cmd_interface(self, tmp_path):
        """Create command interface for testing."""
        config = CommandsConfig(script_dir=str(tmp_path / "scripts"))
        return CommandInterface(config)
    
    def test_generate_bash_script(self, cmd_interface):
        """Test generating bash script."""
        generator = cmd_interface.script_generator
        script = generator.generate_script("List files", "bash")
        
        assert "#!/bin/bash" in script
        assert "List files" in script
        
    def test_generate_python_script(self, cmd_interface):
        """Test generating python script."""
        generator = cmd_interface.script_generator
        script = generator.generate_script("Process data", "python")
        
        assert "#!/usr/bin/env python3" in script
        assert "Process data" in script
        
    def test_gen_script_command(self, cmd_interface, tmp_path):
        """Test gen-script command."""
        result = cmd_interface.execute_command("gen-script test automation script")
        
        assert result['success'] is True
        assert 'Generated script' in result['result']


class TestBuiltinCommands:
    """Test builtin command functionality."""
    
    @pytest.fixture
    def cmd_interface(self, tmp_path):
        """Create command interface for testing."""
        config = CommandsConfig(script_dir=str(tmp_path / "scripts"))
        return CommandInterface(config)
    
    def test_help_command(self, cmd_interface):
        """Test help command shows all commands."""
        result = cmd_interface.execute_command("help")
        
        assert result['success'] is True
        assert 'ls' in result['result']
        assert 'help' in result['result']
        
    def test_ls_command_current_dir(self, cmd_interface):
        """Test ls command on current directory."""
        result = cmd_interface.execute_command("ls")
        
        assert result['success'] is True
        
    def test_ls_command_with_path(self, cmd_interface, tmp_path):
        """Test ls command with path argument."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.touch()
        
        result = cmd_interface.execute_command(f"ls {tmp_path}")
        
        assert result['success'] is True
        assert 'test.txt' in result['result']
        
    def test_ls_command_nonexistent_path(self, cmd_interface):
        """Test ls command with non-existent path."""
        result = cmd_interface.execute_command("ls /nonexistent/path")
        
        assert result['success'] is True
        assert 'not found' in result['result']


class TestDangerousCommands:
    """Test handling of dangerous commands."""
    
    def test_dangerous_command_not_allowed(self, tmp_path):
        """Test dangerous commands are blocked when not allowed."""
        config = CommandsConfig(
            script_dir=str(tmp_path / "scripts"),
            allow_dangerous=False
        )
        cmd_interface = CommandInterface(config)
        
        def dangerous_handler(args):
            return "dangerous"
            
        cmd_interface.register_command(
            name="danger",
            description="Dangerous command",
            handler=dangerous_handler,
            dangerous=True
        )
        
        assert 'danger' not in cmd_interface.commands
        
    def test_dangerous_command_allowed(self, tmp_path):
        """Test dangerous commands are allowed when configured."""
        config = CommandsConfig(
            script_dir=str(tmp_path / "scripts"),
            allow_dangerous=True
        )
        cmd_interface = CommandInterface(config)
        
        def dangerous_handler(args):
            return "dangerous"
            
        cmd_interface.register_command(
            name="danger",
            description="Dangerous command",
            handler=dangerous_handler,
            dangerous=True
        )
        
        assert 'danger' in cmd_interface.commands

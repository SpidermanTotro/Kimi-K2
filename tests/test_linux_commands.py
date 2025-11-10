"""
Unit tests for Linux Command System
"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kimi_k2.linux_commands import CommandSystem, VirtualFileSystem


class TestVirtualFileSystem:
    """Test VirtualFileSystem functionality"""
    
    @pytest.fixture
    def vfs(self):
        """Create a temporary VFS for testing"""
        temp_dir = tempfile.mkdtemp()
        vfs = VirtualFileSystem(temp_dir)
        yield vfs
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_vfs_initialization(self, vfs):
        """Test VFS initializes correctly"""
        assert vfs.root_path.exists()
        assert vfs.current_dir == vfs.root_path
    
    def test_resolve_path_absolute(self, vfs):
        """Test absolute path resolution"""
        path = vfs._resolve_path("/test/path")
        assert "test" in str(path)
        assert "path" in str(path)
    
    def test_resolve_path_relative(self, vfs):
        """Test relative path resolution"""
        path = vfs._resolve_path("test/file.txt")
        assert path.parent == vfs.current_dir / "test"
    
    def test_get_current_dir(self, vfs):
        """Test getting current directory"""
        assert vfs.get_current_dir() == "/"


class TestCommandSystem:
    """Test CommandSystem functionality"""
    
    @pytest.fixture
    def cmd_sys(self):
        """Create a temporary command system for testing"""
        temp_dir = tempfile.mkdtemp()
        vfs = VirtualFileSystem(temp_dir)
        cmd_sys = CommandSystem(vfs)
        yield cmd_sys
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_pwd(self, cmd_sys):
        """Test pwd command"""
        result = cmd_sys.execute("pwd")
        assert result == "/"
    
    def test_mkdir(self, cmd_sys):
        """Test mkdir command"""
        result = cmd_sys.execute("mkdir test_dir")
        assert result == ""
        
        # Verify directory was created
        result = cmd_sys.execute("ls")
        assert "test_dir/" in result
    
    def test_cd(self, cmd_sys):
        """Test cd command"""
        cmd_sys.execute("mkdir test_dir")
        result = cmd_sys.execute("cd test_dir")
        assert result == ""
        
        # Verify we're in the new directory
        result = cmd_sys.execute("pwd")
        assert "test_dir" in result
    
    def test_touch(self, cmd_sys):
        """Test touch command"""
        result = cmd_sys.execute("touch test_file.txt")
        assert result == ""
        
        # Verify file was created
        result = cmd_sys.execute("ls")
        assert "test_file.txt" in result
    
    def test_echo_simple(self, cmd_sys):
        """Test echo command"""
        result = cmd_sys.execute("echo Hello World")
        assert result == "Hello World"
    
    def test_echo_redirect(self, cmd_sys):
        """Test echo with redirect"""
        result = cmd_sys.execute("echo Hello World > test.txt")
        assert result == ""
        
        # Verify file was created and contains content
        result = cmd_sys.execute("cat test.txt")
        assert "Hello World" in result
    
    def test_cat(self, cmd_sys):
        """Test cat command"""
        cmd_sys.execute("echo Test Content > file.txt")
        result = cmd_sys.execute("cat file.txt")
        assert "Test Content" in result
    
    def test_cp(self, cmd_sys):
        """Test cp command"""
        cmd_sys.execute("echo Original > source.txt")
        result = cmd_sys.execute("cp source.txt dest.txt")
        assert result == ""
        
        # Verify both files exist
        result = cmd_sys.execute("ls")
        assert "source.txt" in result
        assert "dest.txt" in result
        
        # Verify content was copied
        result = cmd_sys.execute("cat dest.txt")
        assert "Original" in result
    
    def test_mv(self, cmd_sys):
        """Test mv command"""
        cmd_sys.execute("echo Content > old.txt")
        result = cmd_sys.execute("mv old.txt new.txt")
        assert result == ""
        
        # Verify old file doesn't exist
        result = cmd_sys.execute("ls")
        assert "old.txt" not in result
        assert "new.txt" in result
    
    def test_rm_file(self, cmd_sys):
        """Test rm command on file"""
        cmd_sys.execute("touch test.txt")
        result = cmd_sys.execute("rm test.txt")
        assert result == ""
        
        # Verify file was removed
        result = cmd_sys.execute("ls")
        assert "test.txt" not in result
    
    def test_rm_directory(self, cmd_sys):
        """Test rm command on directory"""
        cmd_sys.execute("mkdir test_dir")
        result = cmd_sys.execute("rm -rf test_dir")
        assert result == ""
        
        # Verify directory was removed
        result = cmd_sys.execute("ls")
        assert "test_dir" not in result
    
    def test_alias(self, cmd_sys):
        """Test alias command"""
        # Create alias
        result = cmd_sys.execute("alias ll='ls -la'")
        assert result == ""
        
        # List aliases
        result = cmd_sys.execute("alias")
        assert "ll" in result
    
    def test_alias_execution(self, cmd_sys):
        """Test executing an alias"""
        cmd_sys.execute("alias ll='ls'")
        cmd_sys.execute("touch test.txt")
        
        # Execute alias
        result = cmd_sys.execute("ll")
        assert "test.txt" in result
    
    def test_help(self, cmd_sys):
        """Test help command"""
        result = cmd_sys.execute("help")
        assert "ls" in result
        assert "cd" in result
        assert "mkdir" in result
    
    def test_invalid_command(self, cmd_sys):
        """Test invalid command"""
        result = cmd_sys.execute("invalid_cmd")
        assert "not found" in result
    
    def test_execute_script(self, cmd_sys):
        """Test script execution"""
        # Create a script
        script_path = cmd_sys.vfs._resolve_path("test_script.sh")
        script_content = """mkdir script_test
cd script_test
touch file1.txt
touch file2.txt
cd ..
"""
        script_path.write_text(script_content)
        
        # Execute script
        outputs = cmd_sys.execute_script("test_script.sh")
        
        # Verify script executed - directory should exist with files
        result = cmd_sys.execute("ls script_test")
        assert "file1.txt" in result
        assert "file2.txt" in result
    
    def test_nested_directories(self, cmd_sys):
        """Test nested directory operations"""
        cmd_sys.execute("mkdir -p a/b/c")
        cmd_sys.execute("cd a/b/c")
        
        result = cmd_sys.execute("pwd")
        assert "a/b/c" in result
    
    def test_ls_directory(self, cmd_sys):
        """Test ls on specific directory"""
        cmd_sys.execute("mkdir test")
        cmd_sys.execute("touch test/file.txt")
        
        result = cmd_sys.execute("ls test")
        assert "file.txt" in result


class TestCommandSystemEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def cmd_sys(self):
        """Create a temporary command system for testing"""
        temp_dir = tempfile.mkdtemp()
        vfs = VirtualFileSystem(temp_dir)
        cmd_sys = CommandSystem(vfs)
        yield cmd_sys
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_cd_nonexistent(self, cmd_sys):
        """Test cd to non-existent directory"""
        result = cmd_sys.execute("cd nonexistent")
        assert "No such file or directory" in result
    
    def test_cat_nonexistent(self, cmd_sys):
        """Test cat on non-existent file"""
        result = cmd_sys.execute("cat nonexistent.txt")
        assert "No such file or directory" in result
    
    def test_mkdir_existing(self, cmd_sys):
        """Test mkdir on existing directory"""
        cmd_sys.execute("mkdir test")
        result = cmd_sys.execute("mkdir test")
        assert "exists" in result.lower()
    
    def test_rm_nonexistent(self, cmd_sys):
        """Test rm on non-existent file"""
        result = cmd_sys.execute("rm nonexistent.txt")
        assert "No such file or directory" in result
    
    def test_rm_directory_without_recursive(self, cmd_sys):
        """Test rm on directory without -r flag"""
        cmd_sys.execute("mkdir test")
        result = cmd_sys.execute("rm test")
        assert "Is a directory" in result
    
    def test_empty_command(self, cmd_sys):
        """Test empty command"""
        result = cmd_sys.execute("")
        assert result == ""
    
    def test_cp_nonexistent_source(self, cmd_sys):
        """Test cp with non-existent source"""
        result = cmd_sys.execute("cp nonexistent.txt dest.txt")
        assert "No such file or directory" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

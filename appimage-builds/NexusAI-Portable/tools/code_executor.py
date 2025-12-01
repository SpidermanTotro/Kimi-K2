"""
NEXUS AI - Code Executor
Safely execute Python code with timeout and sandboxing
"""

import sys
import io
import contextlib
from typing import Dict, Any, Optional
import traceback
import ast
import signal
from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)

class CodeExecutor:
    """
    Safely execute Python code with timeout and sandboxing
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize code executor
        
        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
        
        # Allowed built-ins (security)
        self.allowed_builtins = {
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'divmod', 'enumerate', 'filter', 'float', 'format', 'hex',
            'int', 'isinstance', 'len', 'list', 'map', 'max', 'min',
            'oct', 'ord', 'pow', 'print', 'range', 'reversed', 'round',
            'set', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip',
        }
        
        # Allowed modules
        self.allowed_modules = {
            'math', 'random', 'datetime', 'json', 'collections',
            'itertools', 'functools', 're', 'statistics', 'decimal',
            'fractions', 'string', 'textwrap', 'unicodedata'
        }
        
        logger.info(f"Initialized CodeExecutor with {timeout}s timeout")
    
    def _timeout_handler(self, signum, frame):
        """Handle execution timeout"""
        raise TimeoutError("Code execution timed out")
    
    def is_safe_code(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Check if code is safe to execute
        
        Args:
            code: Python code to check
        
        Returns:
            Tuple of (is_safe, error_message)
        """
        try:
            tree = ast.parse(code)
            
            # Check for dangerous operations
            for node in ast.walk(tree):
                # Block imports of dangerous modules
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.allowed_modules:
                            return False, f"Module '{alias.name}' not allowed"
                
                if isinstance(node, ast.ImportFrom):
                    if node.module not in self.allowed_modules:
                        return False, f"Module '{node.module}' not allowed"
                
                # Block dangerous functions
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'compile', '__import__', 'open']:
                            return False, f"Function '{node.func.id}' not allowed"
                
                # Block attribute access to dangerous attributes
                if isinstance(node, ast.Attribute):
                    dangerous_attrs = ['__class__', '__bases__', '__subclasses__', '__globals__']
                    if node.attr in dangerous_attrs:
                        return False, f"Attribute '{node.attr}' not allowed"
            
            return True, None
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
    
    def execute(
        self,
        code: str,
        globals_dict: Optional[Dict] = None,
        return_variable: str = "result"
    ) -> Dict[str, Any]:
        """
        Execute Python code safely and return results
        
        Args:
            code: Python code to execute
            globals_dict: Global variables to provide
            return_variable: Variable name to return (if exists)
        
        Returns:
            Dict with keys: success, output, error, return_value
        """
        if not config.ENABLE_CODE_EXECUTION:
            return {
                "success": False,
                "output": "",
                "error": "Code execution is disabled",
                "return_value": None
            }
        
        # Safety check
        is_safe, error = self.is_safe_code(code)
        if not is_safe:
            logger.warning(f"Unsafe code blocked: {error}")
            return {
                "success": False,
                "output": "",
                "error": f"Security violation: {error}",
                "return_value": None
            }
        
        # Prepare execution environment
        if globals_dict is None:
            globals_dict = {}
        
        # Add allowed builtins
        safe_builtins = {
            k: __builtins__[k] 
            for k in self.allowed_builtins 
            if k in __builtins__
        }
        globals_dict['__builtins__'] = safe_builtins
        
        # Capture output
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            # Set timeout (Unix only)
            if sys.platform != "win32":
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.timeout)
            
            # Execute code with captured output
            with contextlib.redirect_stdout(output_buffer), \
                 contextlib.redirect_stderr(error_buffer):
                
                exec(code, globals_dict)
            
            # Cancel timeout
            if sys.platform != "win32":
                signal.alarm(0)
            
            result = {
                "success": True,
                "output": output_buffer.getvalue(),
                "error": error_buffer.getvalue(),
                "return_value": globals_dict.get(return_variable, None)
            }
            
            logger.info("Code executed successfully")
            return result
            
        except TimeoutError:
            logger.error(f"Code execution timed out after {self.timeout}s")
            return {
                "success": False,
                "output": output_buffer.getvalue(),
                "error": f"Execution timed out after {self.timeout} seconds",
                "return_value": None
            }
        
        except Exception as e:
            logger.error(f"Code execution error: {str(e)}")
            return {
                "success": False,
                "output": output_buffer.getvalue(),
                "error": f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                "return_value": None
            }
        
        finally:
            # Always cancel timeout
            if sys.platform != "win32":
                signal.alarm(0)
    
    def execute_and_get_result(self, code: str) -> Any:
        """
        Execute code and return the 'result' variable if it exists
        
        Args:
            code: Python code to execute
        
        Returns:
            Value of 'result' variable
        
        Raises:
            RuntimeError: If execution fails
        """
        result = self.execute(code)
        if result["success"]:
            return result.get("return_value")
        else:
            raise RuntimeError(result["error"])
    
    def test_code(self, code: str, test_cases: list) -> Dict[str, Any]:
        """
        Test code with multiple test cases
        
        Args:
            code: Python code to test
            test_cases: List of test case dicts with 'input' and 'expected'
        
        Returns:
            Dict with test results
        """
        results = {
            "total": len(test_cases),
            "passed": 0,
            "failed": 0,
            "test_results": []
        }
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get("input", {})
            expected = test_case.get("expected")
            
            # Create test code
            test_code = f"{code}\n\nresult = {test_input}"
            
            # Execute
            exec_result = self.execute(test_code)
            
            # Check result
            passed = exec_result["success"] and exec_result["return_value"] == expected
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["test_results"].append({
                "test_number": i + 1,
                "input": test_input,
                "expected": expected,
                "actual": exec_result.get("return_value"),
                "passed": passed,
                "error": exec_result.get("error") if not exec_result["success"] else None
            })
        
        return results

__all__ = ['CodeExecutor']
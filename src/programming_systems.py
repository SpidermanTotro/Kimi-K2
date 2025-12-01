"""
THE FORGE AI - Programming Systems Module
Implements comprehensive programming tools and interfaces
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, List, Any

class ProgrammingSystem:
    """Complete programming development environment"""
    
    def __init__(self):
        self.active_projects = {}
        self.templates = self.load_templates()
        self.libraries = self.load_libraries()
    
    def load_templates(self) -> Dict[str, str]:
        """Load programming templates"""
        return {
            "python_basic": '''#!/usr/bin/env python3
# Python Basic Template

def main():
    print("Hello from THE FORGE AI!")
    
    # Your code here
    
if __name__ == "__main__":
    main()
''',
            "javascript_basic": '''// JavaScript Basic Template
console.log("Hello from THE FORGE AI!");

// Your code here
''',
            "web_app": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE FORGE AI Web App</title>
</head>
<body>
    <h1>Welcome to THE FORGE AI</h1>
    <script>
        console.log("Web app loaded!");
    </script>
</body>
</html>
''',
            "api_server": '''from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "THE FORGE AI API Server"})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
''',
            "database_model": '''from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(String(50))
    updated_at = Column(String(50))

# Your models here
''',
            "mobile_app": '''import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const App = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>THE FORGE AI Mobile App</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
});

export default App;
'''
        }
    
    def load_libraries(self) -> Dict[str, List[str]]:
        """Load popular libraries by language"""
        return {
            "python": ["numpy", "pandas", "requests", "flask", "django", "tensorflow", "pytorch", "scikit-learn"],
            "javascript": ["react", "vue", "angular", "express", "lodash", "moment", "axios", "jquery"],
            "web": ["bootstrap", "tailwind", "webpack", "vite", "parcel", "sass", "less"],
            "mobile": ["react-native", "flutter", "swift", "kotlin", "cordova", "ionic"],
            "database": ["sqlalchemy", "mongoose", "sequelize", "prisma", "typeorm", "hibernate"]
        }
    
    def create_project(self, name: str, language: str, template_type: str = "basic") -> Dict[str, Any]:
        """Create a new programming project"""
        try:
            project_dir = f"/workspace/projects/{name}"
            os.makedirs(project_dir, exist_ok=True)
            
            # Get template
            template_key = f"{language}_{template_type}"
            if template_key in self.templates:
                template_content = self.templates[template_key]
                
                # Create main file based on language
                if language == "python":
                    main_file = "main.py"
                elif language == "javascript":
                    main_file = "main.js"
                elif language == "web":
                    main_file = "index.html"
                elif language == "api_server":
                    main_file = "app.py"
                elif language == "database":
                    main_file = "models.py"
                elif language == "mobile":
                    main_file = "App.js"
                else:
                    main_file = "main.txt"
                
                with open(f"{project_dir}/{main_file}", 'w') as f:
                    f.write(template_content)
                
                # Create project structure
                self.create_project_structure(project_dir, language)
                
                self.active_projects[name] = {
                    "path": project_dir,
                    "language": language,
                    "template": template_type,
                    "files": os.listdir(project_dir)
                }
                
                return {
                    "success": True,
                    "project": name,
                    "path": project_dir,
                    "language": language,
                    "files": self.active_projects[name]["files"]
                }
            else:
                return {"success": False, "error": f"Template {template_key} not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_project_structure(self, project_dir: str, language: str):
        """Create appropriate project structure"""
        if language in ["python", "api_server", "database"]:
            os.makedirs(f"{project_dir}/src", exist_ok=True)
            os.makedirs(f"{project_dir}/tests", exist_ok=True)
            os.makedirs(f"{project_dir}/docs", exist_ok=True)
            
            # Create requirements.txt
            with open(f"{project_dir}/requirements.txt", 'w') as f:
                f.write("flask\nnumpy\nrequests\n")
            
            # Create __init__.py files
            open(f"{project_dir}/src/__init__.py", 'w').close()
            open(f"{project_dir}/tests/__init__.py", 'w').close()
            
        elif language in ["javascript", "web"]:
            os.makedirs(f"{project_dir}/src", exist_ok=True)
            os.makedirs(f"{project_dir}/public", exist_ok=True)
            os.makedirs(f"{project_dir}/dist", exist_ok=True)
            
            # Create package.json
            package_json = {
                "name": "forge-ai-project",
                "version": "1.0.0",
                "description": "Project created by THE FORGE AI",
                "main": "main.js",
                "scripts": {
                    "start": "node main.js",
                    "dev": "nodemon main.js",
                    "test": "jest"
                },
                "dependencies": {},
                "devDependencies": {}
            }
            
            with open(f"{project_dir}/package.json", 'w') as f:
                json.dump(package_json, f, indent=2)
        
        elif language == "mobile":
            os.makedirs(f"{project_dir}/components", exist_ok=True)
            os.makedirs(f"{project_dir}/screens", exist_ok=True)
            os.makedirs(f"{project_dir}/utils", exist_ok=True)
    
    def run_code(self, project_name: str, code: str = None) -> Dict[str, Any]:
        """Execute code in the specified project"""
        try:
            if project_name not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.active_projects[project_name]
            language = project["language"]
            
            if code:
                # Run provided code
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                try:
                    result = subprocess.run(['python', temp_file], capture_output=True, text=True, timeout=10)
                    os.unlink(temp_file)
                    
                    return {
                        "success": True,
                        "output": result.stdout,
                        "error": result.stderr,
                        "return_code": result.returncode
                    }
                except subprocess.TimeoutExpired:
                    os.unlink(temp_file)
                    return {"success": False, "error": "Code execution timeout"}
            else:
                # Run main project file
                project_dir = project["path"]
                
                if language == "python":
                    main_file = f"{project_dir}/main.py"
                    if os.path.exists(main_file):
                        result = subprocess.run(['python', main_file], capture_output=True, text=True, timeout=10)
                        return {
                            "success": True,
                            "output": result.stdout,
                            "error": result.stderr,
                            "return_code": result.returncode
                        }
                
                elif language == "javascript":
                    main_file = f"{project_dir}/main.js"
                    if os.path.exists(main_file):
                        result = subprocess.run(['node', main_file], capture_output=True, text=True, timeout=10)
                        return {
                            "success": True,
                            "output": result.stdout,
                            "error": result.stderr,
                            "return_code": result.returncode
                        }
                
                return {"success": False, "error": "Main file not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def debug_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Debug and analyze code"""
        try:
            # Basic syntax checking
            if language == "python":
                try:
                    compile(code, '<string>', 'exec')
                    return {"success": True, "message": "Syntax is valid", "issues": []}
                except SyntaxError as e:
                    return {
                        "success": False,
                        "message": "Syntax error detected",
                        "issues": [{
                            "type": "SyntaxError",
                            "line": e.lineno,
                            "message": str(e),
                            "suggestion": "Check syntax around line " + str(e.lineno)
                        }]
                    }
            
            elif language == "javascript":
                # Basic JavaScript checks
                issues = []
                if 'console.log' in code and 'console.error' not in code:
                    issues.append({
                        "type": "Warning",
                        "message": "Consider adding error handling",
                        "suggestion": "Add try-catch blocks or console.error for debugging"
                    })
                
                return {
                    "success": True,
                    "message": "Basic analysis complete",
                    "issues": issues
                }
            
            return {"success": True, "message": "Code analysis complete", "issues": []}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def install_libraries(self, project_name: str, libraries: List[str]) -> Dict[str, Any]:
        """Install libraries for project"""
        try:
            if project_name not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.active_projects[project_name]
            language = project["language"]
            project_dir = project["path"]
            
            installed = []
            failed = []
            
            if language == "python":
                for lib in libraries:
                    try:
                        result = subprocess.run(['pip', 'install', lib], capture_output=True, text=True)
                        if result.returncode == 0:
                            installed.append(lib)
                        else:
                            failed.append({"library": lib, "error": result.stderr})
                    except Exception as e:
                        failed.append({"library": lib, "error": str(e)})
            
            elif language == "javascript":
                for lib in libraries:
                    try:
                        result = subprocess.run(['npm', 'install', lib], cwd=project_dir, capture_output=True, text=True)
                        if result.returncode == 0:
                            installed.append(lib)
                        else:
                            failed.append({"library": lib, "error": result.stderr})
                    except Exception as e:
                        failed.append({"library": lib, "error": str(e)})
            
            return {
                "success": len(failed) == 0,
                "installed": installed,
                "failed": failed
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_code_completion(self, code: str, cursor_position: int = 0) -> Dict[str, Any]:
        """Get code completion suggestions"""
        try:
            # Simple keyword-based completion
            python_keywords = [
                "print", "def", "class", "import", "from", "if", "else", "elif",
                "for", "while", "try", "except", "with", "as", "return", "yield"
            ]
            
            javascript_keywords = [
                "console", "function", "const", "let", "var", "if", "else", "for",
                "while", "try", "catch", "return", "class", "import", "export"
            ]
            
            suggestions = []
            
            if "def" in code or "print" in code:
                suggestions.extend(python_keywords)
            if "function" in code or "console" in code:
                suggestions.extend(javascript_keywords)
            
            return {
                "success": True,
                "suggestions": list(set(suggestions))[:10],  # Limit to 10 suggestions
                "context": "Basic keyword completion"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_api_endpoint(self, project_name: str, endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """Create API endpoint for project"""
        try:
            if project_name not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.active_projects[project_name]
            language = project["language"]
            project_dir = project["path"]
            
            if language in ["python", "api_server"]:
                endpoint_code = f'''
@app.route('/api/{endpoint}', methods=['{method}'])
def {endpoint}_handler():
    """
    {method} endpoint for {endpoint}
    Created by THE FORGE AI
    """
    if request.method == '{method}':
        return jsonify({{
            "message": "This is the {endpoint} endpoint",
            "status": "success",
            "data": {{}}
        }})
    else:
        return jsonify({{"error": "Method not allowed"}}), 405
'''
                
                # Append to main app file
                app_file = f"{project_dir}/app.py"
                if os.path.exists(app_file):
                    with open(app_file, 'a') as f:
                        f.write(endpoint_code)
                
                return {
                    "success": True,
                    "endpoint": f"/api/{endpoint}",
                    "method": method,
                    "message": f"API endpoint {endpoint} created successfully"
                }
            
            return {"success": False, "error": "API creation not supported for this language"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """Get detailed project status"""
        try:
            if project_name not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.active_projects[project_name]
            project_dir = project["path"]
            
            # Get project files
            files = []
            for root, dirs, file_list in os.walk(project_dir):
                for file in file_list:
                    rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                    files.append(rel_path)
            
            # Get project stats
            total_files = len(files)
            py_files = len([f for f in files if f.endswith('.py')])
            js_files = len([f for f in files if f.endswith('.js')])
            html_files = len([f for f in files if f.endswith('.html')])
            
            return {
                "success": True,
                "project": project_name,
                "language": project["language"],
                "total_files": total_files,
                "python_files": py_files,
                "javascript_files": js_files,
                "html_files": html_files,
                "files": files,
                "created_at": project.get("created_at", "Unknown"),
                "last_modified": project.get("last_modified", "Unknown")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize the programming system
programming_system = ProgrammingSystem()
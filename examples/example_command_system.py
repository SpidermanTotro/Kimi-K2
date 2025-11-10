"""
Example: Using the Command System

This example demonstrates the Linux-style command system with
scripting capabilities.
"""

from kimi_k2.commands import CommandSystem


def main():
    """Run the command system example."""
    print("=== Command System Example ===\n")
    
    # Create the command system
    cmd = CommandSystem(virtual_fs=True)
    
    print("1. Basic file system commands...\n")
    
    # Print working directory
    result = cmd.execute("pwd")
    print(f"   pwd: {result['output']}")
    
    # Create directories
    cmd.execute("mkdir projects")
    cmd.execute("mkdir documents")
    cmd.execute("mkdir downloads")
    
    result = cmd.execute("ls")
    print(f"   ls: {result['output']}\n")
    
    # Change directory
    cmd.execute("cd projects")
    result = cmd.execute("pwd")
    print(f"   After cd projects, pwd: {result['output']}\n")
    
    # Create nested directories
    cmd.execute("mkdir python")
    cmd.execute("mkdir python/scripts")
    cmd.execute("cd python/scripts")
    
    result = cmd.execute("pwd")
    print(f"   After nested cd, pwd: {result['output']}\n")
    
    # Create files
    print("2. Creating and managing files...\n")
    cmd.execute("touch main.py")
    cmd.execute("touch utils.py")
    cmd.execute("touch config.yaml")
    
    result = cmd.execute("ls")
    print(f"   Files in current directory:\n{result['output']}\n")
    
    # Echo command
    result = cmd.execute("echo Hello, Kimi K2!")
    print(f"   echo: {result['output']}\n")
    
    # Variables
    print("3. Using variables...\n")
    cmd.execute("set project_name MyAwesomeProject")
    cmd.execute("set version 1.0.0")
    cmd.execute("set author Kimi")
    
    result = cmd.execute("get project_name")
    print(f"   project_name: {result['output']}")
    
    result = cmd.execute("get")
    print(f"   All variables:\n{result['output']}\n")
    
    # Script execution
    print("4. Executing a script...\n")
    script = """
    # Setup script
    cd /
    mkdir workspace
    cd workspace
    mkdir src
    mkdir tests
    mkdir docs
    touch README.md
    touch setup.py
    """
    
    print("   Running setup script...")
    results = cmd.execute_script(script)
    
    successful = sum(1 for r in results if r["status"] == "success")
    print(f"   Executed {len(results)} commands, {successful} successful\n")
    
    result = cmd.execute("pwd")
    print(f"   Current directory: {result['output']}")
    
    result = cmd.execute("ls")
    print(f"   Contents:\n{result['output']}\n")
    
    # Custom command
    print("5. Registering custom command...\n")
    
    def greet_handler(args):
        name = args[0] if args else "World"
        return f"Hello, {name}! Welcome to Kimi K2!"
    
    cmd.register_command("greet", greet_handler)
    
    result = cmd.execute("greet")
    print(f"   greet: {result['output']}")
    
    result = cmd.execute("greet Alice")
    print(f"   greet Alice: {result['output']}\n")
    
    # Command history
    print("6. Command history...\n")
    history = cmd.get_history()
    print(f"   Total commands executed: {len(history)}")
    print(f"   Last 5 commands:")
    for i, cmd_str in enumerate(history[-5:], 1):
        print(f"      {i}. {cmd_str}")
    
    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()

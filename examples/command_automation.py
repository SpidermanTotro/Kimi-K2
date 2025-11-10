"""Example: Command automation and script generation."""

from kimi_k2 import Framework, Config


def main():
    """Demonstrate command automation."""
    config = Config.default()
    framework = Framework(config)
    framework.initialize()
    
    try:
        cmd_interface = framework.get_module('commands')
        
        print("=" * 60)
        print("Command Automation Demo")
        print("=" * 60)
        
        # Execute help command
        print("\n1. Listing available commands:")
        result = cmd_interface.execute_command("help")
        if result['success']:
            print(result['result'])
        
        # Generate a backup script
        print("\n2. Generating backup script:")
        script = cmd_interface.script_generator.generate_script(
            "Create daily backup of database",
            "bash"
        )
        print(script)
        
        # Generate a Python script
        print("\n3. Generating Python data processing script:")
        script = cmd_interface.script_generator.generate_script(
            "Process CSV files and generate reports",
            "python"
        )
        print(script)
        
        # Show command history
        print("\n4. Command history:")
        for i, cmd in enumerate(cmd_interface.command_history, 1):
            print(f"  {i}. {cmd}")
        
        # Register a custom command
        print("\n5. Registering custom command:")
        
        def greet_handler(args):
            name = args[0] if args else "World"
            return f"Hello, {name}!"
        
        cmd_interface.register_command(
            name="greet",
            description="Greet a user",
            handler=greet_handler,
            category="custom"
        )
        
        result = cmd_interface.execute_command("greet Alice")
        print(f"Custom command result: {result['result']}")
        
        print("\n" + "=" * 60)
        print("Automation demo complete!")
        
    finally:
        framework.shutdown()


if __name__ == '__main__':
    main()

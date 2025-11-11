#!/usr/bin/env python3
"""
Interactive Setup Wizard for Kimi K2

This wizard guides users through the initial setup and configuration
of the Kimi K2 system.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class SetupWizard:
    """Interactive setup wizard for Kimi K2."""
    
    def __init__(self):
        """Initialize the setup wizard."""
        self.config = {}
        self.steps_completed = []
        
    def run(self):
        """Run the interactive setup wizard."""
        print("\n" + "="*70)
        print("Welcome to the Kimi K2 Setup Wizard!")
        print("="*70 + "\n")
        
        print("This wizard will help you set up Kimi K2 for your environment.")
        print("You can exit at any time by pressing Ctrl+C.\n")
        
        try:
            # Step 1: Choose deployment type
            self.choose_deployment_type()
            
            # Step 2: Configure storage
            self.configure_storage()
            
            # Step 3: Set up plugins
            self.setup_plugins()
            
            # Step 4: Configure memory management
            self.configure_memory()
            
            # Step 5: Set up monitoring (optional)
            self.setup_monitoring()
            
            # Step 6: Review and save configuration
            self.review_and_save()
            
            # Step 7: Final steps
            self.show_next_steps()
            
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
            sys.exit(0)
    
    def choose_deployment_type(self):
        """Choose deployment type."""
        print("\n" + "-"*70)
        print("Step 1: Choose Deployment Type")
        print("-"*70)
        
        print("\nAvailable deployment options:")
        print("1. Local development (single machine)")
        print("2. Production (multi-GPU cluster)")
        print("3. Cloud deployment (managed service)")
        
        choice = self.get_choice("Select deployment type", ["1", "2", "3"])
        
        deployment_types = {
            "1": "local",
            "2": "production",
            "3": "cloud"
        }
        
        self.config['deployment_type'] = deployment_types[choice]
        self.steps_completed.append("deployment_type")
        
        print(f"\n✓ Deployment type set to: {deployment_types[choice]}")
    
    def configure_storage(self):
        """Configure storage backend."""
        print("\n" + "-"*70)
        print("Step 2: Configure Storage")
        print("-"*70)
        
        print("\nChoose a storage backend for memory and data:")
        print("1. File-based (simple, for development)")
        print("2. PostgreSQL (recommended for production)")
        print("3. Redis (high-performance, in-memory)")
        
        choice = self.get_choice("Select storage backend", ["1", "2", "3"])
        
        backends = {
            "1": "file",
            "2": "postgresql",
            "3": "redis"
        }
        
        self.config['storage_backend'] = backends[choice]
        
        # Get storage path for file-based
        if choice == "1":
            default_path = "./data"
            path = input(f"\nStorage path (default: {default_path}): ").strip()
            self.config['storage_path'] = path if path else default_path
        
        self.steps_completed.append("storage")
        print(f"\n✓ Storage configured: {backends[choice]}")
    
    def setup_plugins(self):
        """Set up plugins."""
        print("\n" + "-"*70)
        print("Step 3: Plugin Setup")
        print("-"*70)
        
        print("\nWould you like to enable plugins?")
        enable = self.get_yes_no("Enable plugins")
        
        self.config['plugins_enabled'] = enable
        
        if enable:
            print("\nAvailable plugin types:")
            print("- Tool plugins: Extend tool-calling capabilities")
            print("- API plugins: Integrate external services")
            print("- Data plugins: Add data sources and processors")
            
            self.config['plugin_types'] = []
            
            if self.get_yes_no("Enable tool plugins"):
                self.config['plugin_types'].append('tool')
            if self.get_yes_no("Enable API plugins"):
                self.config['plugin_types'].append('api')
            if self.get_yes_no("Enable data plugins"):
                self.config['plugin_types'].append('data')
        
        self.steps_completed.append("plugins")
        print("\n✓ Plugin configuration completed")
    
    def configure_memory(self):
        """Configure memory management."""
        print("\n" + "-"*70)
        print("Step 4: Memory Management")
        print("-"*70)
        
        print("\nMemory management allows Kimi K2 to maintain context across conversations.")
        
        enable = self.get_yes_no("Enable memory management")
        self.config['memory_enabled'] = enable
        
        if enable:
            print("\nConfigure memory settings:")
            
            default_history = "1000"
            max_history = input(f"Max conversation history (default: {default_history}): ").strip()
            self.config['max_history'] = int(max_history) if max_history else int(default_history)
            
            self.config['enable_personalization'] = self.get_yes_no("Enable personalization")
        
        self.steps_completed.append("memory")
        print("\n✓ Memory management configured")
    
    def setup_monitoring(self):
        """Set up monitoring (optional)."""
        print("\n" + "-"*70)
        print("Step 5: Monitoring Setup (Optional)")
        print("-"*70)
        
        print("\nMonitoring helps track performance and usage metrics.")
        
        enable = self.get_yes_no("Enable monitoring")
        self.config['monitoring_enabled'] = enable
        
        if enable:
            print("\nAvailable monitoring tools:")
            print("1. Prometheus + Grafana")
            print("2. Custom logging only")
            
            choice = self.get_choice("Select monitoring tool", ["1", "2"])
            
            self.config['monitoring_tool'] = "prometheus" if choice == "1" else "logging"
        
        self.steps_completed.append("monitoring")
        print("\n✓ Monitoring setup completed")
    
    def review_and_save(self):
        """Review configuration and save."""
        print("\n" + "-"*70)
        print("Step 6: Review Configuration")
        print("-"*70)
        
        print("\nYour configuration:")
        print(json.dumps(self.config, indent=2))
        
        if not self.get_yes_no("\nSave this configuration"):
            print("Configuration not saved. Exiting.")
            sys.exit(0)
        
        # Save configuration
        config_path = Path("config/kimi_k2_config.json")
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"\n✓ Configuration saved to: {config_path}")
    
    def show_next_steps(self):
        """Show next steps after setup."""
        print("\n" + "="*70)
        print("Setup Complete!")
        print("="*70)
        
        print("\nNext steps:")
        print("1. Review the configuration in config/kimi_k2_config.json")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Download the model: See README.md for instructions")
        print("4. Start the server: See docs/deploy_guidance.md")
        
        if self.config.get('monitoring_enabled'):
            print("5. Start monitoring: docker-compose -f benchmarks/dashboards/docker-compose.yml up -d")
        
        print("\nFor more information, see:")
        print("- Documentation: docs/")
        print("- Examples: examples/")
        print("- Support: support@moonshot.cn")
        
        print("\nThank you for using Kimi K2!")
    
    def get_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """Get user choice from a list of options.
        
        Args:
            prompt: Prompt to display
            valid_choices: List of valid choice strings
            
        Returns:
            User's choice
        """
        while True:
            choice = input(f"\n{prompt} [{'/'.join(valid_choices)}]: ").strip()
            if choice in valid_choices:
                return choice
            print(f"Invalid choice. Please select from: {', '.join(valid_choices)}")
    
    def get_yes_no(self, prompt: str) -> bool:
        """Get yes/no response from user.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            True for yes, False for no
        """
        while True:
            response = input(f"{prompt}? [y/n]: ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please answer 'y' or 'n'")


def main():
    """Run the setup wizard."""
    wizard = SetupWizard()
    wizard.run()


if __name__ == "__main__":
    main()

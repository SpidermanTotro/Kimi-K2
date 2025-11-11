"""
Example: Plugin System Usage

This example demonstrates how to extend the dual-operator AI system
with custom plugins for tools and workflows.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dual_operator_ai.core import (
    UserProfile,
    DualOperatorEngine,
    FusionStrategy
)
from dual_operator_ai.modules.plugin_system import (
    Plugin,
    PluginManager,
    ToolPlugin,
    WorkflowPlugin
)


# Define a custom tool plugin
class CalculatorTool(ToolPlugin):
    """A simple calculator tool plugin."""
    
    @property
    def name(self):
        return "calculator"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self, config):
        """Initialize the calculator."""
        self.history = []
    
    def get_tool_definition(self):
        """Get the tool definition for LLM."""
        return {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform basic arithmetic calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"],
                            "description": "The operation to perform"
                        },
                        "a": {
                            "type": "number",
                            "description": "First number"
                        },
                        "b": {
                            "type": "number",
                            "description": "Second number"
                        }
                    },
                    "required": ["operation", "a", "b"]
                }
            }
        }
    
    def execute(self, operation, a, b):
        """Execute the calculation."""
        result = None
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b != 0:
                result = a / b
            else:
                return {"error": "Division by zero"}
        
        self.history.append({
            "operation": operation,
            "a": a,
            "b": b,
            "result": result
        })
        
        return {"result": result, "operation": f"{a} {operation} {b} = {result}"}


# Define a workflow plugin
class DecisionWorkflow(WorkflowPlugin):
    """A workflow for collaborative decision-making."""
    
    @property
    def name(self):
        return "decision_workflow"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self, config):
        """Initialize the workflow."""
        self.engine = config.get('engine')
        
        # Define workflow steps
        self.add_step(self.gather_input)
        self.add_step(self.analyze_options)
        self.add_step(self.make_decision)
        self.add_step(self.document_decision)
    
    def gather_input(self, topic, **kwargs):
        """Step 1: Gather input from both users."""
        print(f"Step 1: Gathering input on '{topic}'")
        return {"topic": topic, "status": "inputs_gathered"}
    
    def analyze_options(self, previous_result=None, **kwargs):
        """Step 2: Analyze options."""
        topic = previous_result.get('topic', 'unknown') if previous_result else 'unknown'
        print(f"Step 2: Analyzing options for {topic}")
        return {"analysis": "Options analyzed", "previous": previous_result}
    
    def make_decision(self, previous_result=None, **kwargs):
        """Step 3: Make collaborative decision."""
        print(f"Step 3: Making collaborative decision")
        return {"decision": "Decision made", "previous": previous_result}
    
    def document_decision(self, previous_result=None, **kwargs):
        """Step 4: Document the decision."""
        print(f"Step 4: Documenting decision")
        return {
            "status": "complete",
            "decision_documented": True,
            "workflow_result": previous_result
        }


def main():
    """Run the plugin system example."""
    
    print("=" * 60)
    print("Dual Operator AI - Plugin System Example")
    print("=" * 60)
    print()
    
    # Create user profiles
    user1 = UserProfile(user_id="user1", name="User 1")
    user2 = UserProfile(user_id="user2", name="User 2")
    
    # Create engine
    engine = DualOperatorEngine(
        user1_profile=user1,
        user2_profile=user2,
        fusion_strategy=FusionStrategy.ADAPTIVE
    )
    
    # Create plugin manager
    print("Initializing Plugin Manager...")
    manager = PluginManager()
    
    # Register calculator tool plugin
    print("\n1. Registering Calculator Tool Plugin")
    print("-" * 60)
    
    calc_plugin = CalculatorTool()
    manager.register_plugin(calc_plugin)
    
    print(f"✓ Registered: {calc_plugin.name} v{calc_plugin.version}")
    
    # Get tool definition
    tool_def = calc_plugin.get_tool_definition()
    print(f"  Tool name: {tool_def['function']['name']}")
    print(f"  Description: {tool_def['function']['description']}")
    
    # Execute the plugin
    print("\n  Testing calculator:")
    result1 = manager.execute_plugin("calculator", operation="add", a=10, b=5)
    print(f"    10 + 5 = {result1['result']}")
    
    result2 = manager.execute_plugin("calculator", operation="multiply", a=7, b=8)
    print(f"    7 × 8 = {result2['result']}")
    
    # Register workflow plugin
    print("\n2. Registering Decision Workflow Plugin")
    print("-" * 60)
    
    workflow_plugin = DecisionWorkflow()
    manager.register_plugin(workflow_plugin, config={'engine': engine})
    
    print(f"✓ Registered: {workflow_plugin.name} v{workflow_plugin.version}")
    print(f"  Workflow steps: {len(workflow_plugin.steps)}")
    
    # Execute workflow
    print("\n  Executing decision workflow:")
    workflow_result = manager.execute_plugin(
        "decision_workflow",
        topic="Choose project architecture"
    )
    print(f"  ✓ Workflow completed: {workflow_result['status']}")
    
    # List all plugins
    print("\n3. Plugin Registry")
    print("-" * 60)
    
    plugins = manager.list_plugins()
    print(f"Total plugins registered: {len(plugins)}")
    
    for plugin_info in plugins:
        print(f"  • {plugin_info['name']} v{plugin_info['version']} ({plugin_info['type']})")
    
    # Demonstrate hooks
    print("\n4. Hook System")
    print("-" * 60)
    
    def on_decision_made(decision):
        print(f"  [Hook] Decision made: {decision}")
        return "acknowledged"
    
    manager.register_hook("decision_made", on_decision_made)
    print("✓ Registered hook: 'decision_made'")
    
    # Trigger hook
    print("\n  Triggering hook...")
    results = manager.trigger_hook("decision_made", "Use microservices architecture")
    print(f"  Hook results: {results}")
    
    # Custom plugin example
    print("\n5. Custom Plugin Example")
    print("-" * 60)
    
    class NotificationPlugin(Plugin):
        """Custom notification plugin."""
        
        @property
        def name(self):
            return "notifier"
        
        @property
        def version(self):
            return "1.0.0"
        
        def initialize(self, config):
            self.notifications = []
        
        def execute(self, message, priority="normal"):
            notification = {
                "message": message,
                "priority": priority,
                "sent": True
            }
            self.notifications.append(notification)
            return notification
    
    # Register custom plugin
    notifier = NotificationPlugin()
    manager.register_plugin(notifier)
    
    print(f"✓ Registered custom plugin: {notifier.name}")
    
    # Use custom plugin
    notification = manager.execute_plugin(
        "notifier",
        message="Decision finalized",
        priority="high"
    )
    print(f"  Notification sent: {notification['message']} (priority: {notification['priority']})")
    
    # Summary
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    
    print("\nKey Features Demonstrated:")
    print("  1. ✓ Tool plugins with LLM-compatible definitions")
    print("  2. ✓ Workflow plugins for multi-step processes")
    print("  3. ✓ Plugin registration and management")
    print("  4. ✓ Hook system for event-driven architecture")
    print("  5. ✓ Custom plugin development")
    
    print("\nPlugin System Benefits:")
    print("  • Modular and extensible architecture")
    print("  • Easy integration of new capabilities")
    print("  • Consistent plugin interface")
    print("  • Event-driven hooks for flexibility")
    print("  • Tool definitions ready for LLM integration")


if __name__ == "__main__":
    main()

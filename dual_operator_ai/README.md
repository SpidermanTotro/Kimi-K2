# Dual Operator AI System

A modular framework for combining the functionalities and perspectives of multiple users into a cohesive, dynamic AI system. This system enables two operators (such as a couple, partners, or collaborators) to interact with a single AI entity that adapts to both their preferences and decision-making styles.

## Overview

The Dual Operator AI System is designed to create "one AI entity for two operators" that:

- Handles long-context understanding and multimodal inputs
- Provides personalized responses based on dynamic inputs and preferences of both individuals
- Merges decision-making processes configured by each user's inclinations and strengths
- Integrates seamlessly with existing AI tools, workflows, and pipelines (including Kimi-K2)
- Implements visualization and audit tools for transparency in decision-making

## Features

### Core Capabilities

1. **Multi-User Context Management**
   - Long-context support (up to 100,000+ tokens)
   - Multimodal input handling (text, image, audio, video)
   - Separate and shared context streams
   - Context aggregation and summarization

2. **User Profile Management**
   - Dynamic preference tracking
   - Strength and expertise areas
   - Decision weight customization
   - Communication style adaptation

3. **Decision Fusion Engine**
   - Multiple fusion strategies:
     - Weighted Average: Balance inputs based on user weights
     - Consensus: Require agreement between users
     - Expertise-Based: Defer to expert in relevant domain
     - Adaptive: Learn from historical performance
     - Prioritized: Follow explicit priority ordering
   - Custom fusion function support
   - Complete audit trail

4. **Kimi-K2 Integration**
   - Native support for Kimi-K2 API
   - Tool calling capabilities
   - Streaming response support
   - OpenAI-compatible interface

5. **Plugin System**
   - Modular architecture
   - Custom tool plugins
   - Workflow plugins
   - Hook system for extensibility

6. **Visualization & Audit**
   - Decision transparency dashboards
   - Audit trail tracking
   - HTML/JSON export capabilities
   - User contribution analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/moonshotai/Kimi-K2.git
cd Kimi-K2/dual_operator_ai

# No additional dependencies required for core functionality
# For Kimi-K2 integration, install:
pip install openai
```

## Quick Start

### Basic Usage

```python
from dual_operator_ai.core import (
    UserProfile,
    DualOperatorEngine,
    FusionStrategy
)

# Create user profiles
user1 = UserProfile(
    user_id="alice",
    name="Alice",
    preferences={"detail_level": "high", "technical_depth": "expert"},
    strengths=["technical_writing", "architecture"],
    decision_weight=0.6
)

user2 = UserProfile(
    user_id="bob",
    name="Bob",
    preferences={"detail_level": "medium", "technical_depth": "intermediate"},
    strengths=["project_management", "user_experience"],
    decision_weight=0.4
)

# Create dual-operator engine
engine = DualOperatorEngine(
    user1_profile=user1,
    user2_profile=user2,
    fusion_strategy=FusionStrategy.ADAPTIVE
)

# Process inputs
engine.process_input(
    user_id="alice",
    content="How should we architect this system?",
    modality="text"
)

engine.process_input(
    user_id="bob",
    content="We need to prioritize user experience.",
    modality="text"
)

# Generate response considering both perspectives
response = engine.generate_response(include_both_perspectives=True)
```

### Kimi-K2 Integration

```python
from dual_operator_ai.modules.kimi_adapter import KimiK2Adapter

# Initialize adapter
adapter = KimiK2Adapter(
    api_key="your_api_key",
    base_url="https://api.moonshot.cn/v1"
)

# Get formatted context
messages = engine.get_context_for_llm()

# Generate AI response
response = adapter.generate_response(
    messages=messages,
    max_tokens=2048
)

# Add to shared context
engine.context_manager.add_context(
    user_id=None,
    role="assistant",
    content=response['content'],
    shared=True
)
```

### Collaborative Decision Making

```python
# Make a collaborative decision
decision = engine.make_collaborative_decision(
    decision_context={"domain": "architecture", "urgency": "high"},
    user1_input={"choice": "microservices", "priority": 2},
    user2_input={"choice": "modular_monolith", "priority": 1}
)

print(f"Fused decision: {decision['content']}")
```

### Audit and Visualization

```python
from dual_operator_ai.modules.visualization import DecisionVisualizer

# Get audit trail
audit = engine.get_audit_trail()

# Create visualizer
visualizer = DecisionVisualizer()

# Generate dashboard
dashboard = visualizer.generate_audit_dashboard(audit)

# Export as HTML
visualizer.export_visualization(
    dashboard,
    filepath="dashboard.html",
    format="html"
)
```

## Architecture

### Core Components

```
dual_operator_ai/
├── core/
│   ├── user_profile.py       # User profile management
│   ├── context_manager.py    # Context and conversation management
│   ├── decision_fusion.py    # Decision fusion engine
│   └── dual_operator_engine.py # Main orchestration engine
├── modules/
│   ├── kimi_adapter.py       # Kimi-K2 integration
│   ├── visualization.py      # Audit and visualization
│   └── plugin_system.py      # Plugin framework
├── examples/
│   ├── basic_usage.py        # Basic usage example
│   └── kimi_integration.py   # Kimi-K2 integration example
└── tests/                    # Test suite
```

### Component Responsibilities

- **UserProfile**: Manages individual user preferences, strengths, and decision weights
- **ContextManager**: Handles conversation history with long-context and multimodal support
- **DecisionFusionEngine**: Merges decisions using various strategies
- **DualOperatorEngine**: Orchestrates all components and provides main API
- **KimiK2Adapter**: Integrates with Kimi-K2 model API
- **DecisionVisualizer**: Creates transparency dashboards
- **PluginManager**: Manages extensibility through plugins

## Configuration

### User Profiles

```python
user = UserProfile(
    user_id="unique_id",
    name="Display Name",
    preferences={
        "communication_style": "detailed",  # or "concise", "balanced"
        "technical_level": "expert",        # or "beginner", "intermediate"
        "response_length": "comprehensive"  # or "brief", "moderate"
    },
    strengths=["domain1", "domain2"],
    decision_weight=0.5  # 0.0 to 1.0
)
```

### Fusion Strategies

- **WEIGHTED_AVERAGE**: Combines inputs based on user decision weights
- **CONSENSUS**: Requires agreement; identifies divergent points
- **EXPERTISE_BASED**: Defers to user with relevant expertise
- **ADAPTIVE**: Learns from context and history
- **PRIORITIZED**: Follows explicit priority ordering

### Context Management

```python
engine.context_manager.add_context(
    user_id="alice",
    role="user",           # user, assistant, system, tool
    content="message",
    modality="text",       # text, image, audio, video, structured
    metadata={},
    shared=True            # Share between users
)
```

## Advanced Features

### Custom Fusion Functions

```python
def custom_fusion(decisions, **kwargs):
    # Your custom fusion logic
    return fused_decision

engine.decision_engine.register_custom_fusion("my_strategy", custom_fusion)
result = engine.decision_engine.apply_custom_fusion("my_strategy", decisions)
```

### Plugin Development

```python
from dual_operator_ai.modules.plugin_system import Plugin

class MyPlugin(Plugin):
    @property
    def name(self):
        return "my_plugin"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self, config):
        # Initialize plugin
        pass
    
    def execute(self, *args, **kwargs):
        # Plugin logic
        return result

# Register plugin
from dual_operator_ai.modules.plugin_system import PluginManager
manager = PluginManager()
manager.register_plugin(MyPlugin(), config={})
```

### Tool Plugins

```python
from dual_operator_ai.modules.plugin_system import ToolPlugin

class WeatherTool(ToolPlugin):
    @property
    def name(self):
        return "weather_tool"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self, config):
        self.api_key = config.get('api_key')
    
    def get_tool_definition(self):
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }
        }
    
    def execute(self, city):
        # Fetch weather
        return {"temperature": 72, "condition": "sunny"}
```

## Examples

See the `examples/` directory for complete examples:

- `basic_usage.py`: Core functionality demonstration
- `kimi_integration.py`: Integration with Kimi-K2 API

Run examples:

```bash
cd dual_operator_ai/examples
python basic_usage.py
python kimi_integration.py
```

## API Reference

### DualOperatorEngine

**Constructor**
```python
DualOperatorEngine(
    user1_profile: UserProfile,
    user2_profile: UserProfile,
    fusion_strategy: FusionStrategy = FusionStrategy.ADAPTIVE,
    max_context_length: int = 100000
)
```

**Methods**

- `process_input(user_id, content, modality, metadata)`: Process user input
- `generate_response(target_user_id, include_both_perspectives)`: Generate AI response
- `make_collaborative_decision(decision_context, user1_input, user2_input)`: Fuse decisions
- `get_audit_trail()`: Get complete audit trail
- `export_session(filepath)`: Export session to file
- `get_context_for_llm(user_id, system_prompt)`: Get LLM-ready context

### UserProfile

**Constructor**
```python
UserProfile(
    user_id: str,
    name: str,
    preferences: Dict[str, Any] = {},
    strengths: List[str] = [],
    communication_style: str = "balanced",
    decision_weight: float = 0.5
)
```

**Methods**

- `update_preferences(new_preferences)`: Update preferences
- `add_strength(strength)`: Add expertise area
- `set_decision_weight(weight)`: Update decision weight
- `to_dict()`: Export to dictionary
- `save_to_file(filepath)`: Save to JSON file

### ContextManager

**Constructor**
```python
ContextManager(max_context_length: int = 100000)
```

**Methods**

- `add_context(user_id, role, content, modality, metadata, shared)`: Add context entry
- `get_context_for_user(user_id, include_shared, max_entries)`: Get user context
- `get_combined_context(user_ids, max_entries)`: Get combined context
- `format_for_llm(user_id, include_metadata)`: Format for LLM API

## Testing

Run the test suite:

```bash
cd dual_operator_ai
python -m pytest tests/
```

## Use Cases

1. **Couple's AI Assistant**: Shared AI that understands both partners' preferences
2. **Business Partners**: Collaborative decision-making for business decisions
3. **Parent-Child Learning**: Adaptive education with different expertise levels
4. **Team Collaboration**: Multi-stakeholder project management
5. **Research Partnerships**: Combined expertise in academic research

## Best Practices

1. **Set Decision Weights Thoughtfully**: Adjust weights based on context and expertise
2. **Use Appropriate Fusion Strategies**: Match strategy to decision type
3. **Review Audit Trails**: Regularly check transparency dashboards
4. **Update Profiles Dynamically**: Keep preferences and strengths current
5. **Leverage Expertise**: Use expertise-based fusion for domain-specific decisions

## Troubleshooting

### Context Length Issues
- Increase `max_context_length` if needed
- Context manager automatically prunes old entries
- Use `get_context_summary()` to monitor usage

### Decision Conflicts
- Review fusion strategy choice
- Adjust decision weights if needed
- Use consensus strategy to identify conflicts
- Check audit trail for decision history

### Integration Issues
- Verify API key for Kimi-K2
- Check message format compatibility
- Ensure proper tool definitions
- Review streaming vs. non-streaming modes

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

This project is released under the Modified MIT License, consistent with the Kimi-K2 repository.

## Support

For questions and support:
- GitHub Issues: Report bugs and request features
- Email: support@moonshot.cn
- Documentation: See inline code documentation

## Acknowledgments

Built on top of the Kimi-K2 framework by Moonshot AI, leveraging state-of-the-art agentic intelligence capabilities.

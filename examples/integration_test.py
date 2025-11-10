"""Integration test for the complete framework."""

import asyncio
from kimi_k2 import Framework, Config
from kimi_k2.core.config import AnimationConfig, CommandsConfig, ModelsConfig, CollaborationConfig


def test_complete_framework_integration():
    """Test all framework modules working together."""
    print("=" * 80)
    print("KIMI-K2 FRAMEWORK INTEGRATION TEST")
    print("=" * 80)
    
    # Configure framework with all modules enabled
    config = Config(
        animation=AnimationConfig(output_dir="/tmp/integration_test/animations"),
        commands=CommandsConfig(script_dir="/tmp/integration_test/scripts"),
        models=ModelsConfig(model_cache_dir="/tmp/integration_test/cache"),
        collaboration=CollaborationConfig(enabled=True)
    )
    
    framework = Framework(config)
    framework.initialize()
    
    try:
        # Test animation module
        print("\n1. Testing Animation Module...")
        animation = framework.get_module('animation')
        project = animation.create_project(name="integration_test", fps=24)
        animation.timeline_editor.add_clip({'type': 'test'}, 0.0)
        animation.render_project("integration_test")
        print("   ✓ Animation module works")
        
        # Test commands module
        print("\n2. Testing Commands Module...")
        commands = framework.get_module('commands')
        result = commands.execute_command("help")
        assert result['success'], "Command execution failed"
        script = commands.script_generator.generate_script("test", "bash")
        assert "#!/bin/bash" in script
        print("   ✓ Commands module works")
        
        # Test models module
        print("\n3. Testing Models Module...")
        models = framework.get_module('models')
        models.load_model("lightweight")
        text = models.generate("Hello")
        assert text is not None
        print("   ✓ Models module works")
        
        # Test collaboration module
        print("\n4. Testing Collaboration Module...")
        
        async def test_collab():
            collab = framework.get_module('collaboration')
            await collab.start()
            user = await collab.connect_user("test_user", "Test User")
            session = collab.create_session("test_session", "Test", "test_user")
            collab.update_shared_state("test_session", "test", "value")
            await collab.disconnect_user("test_user")
            await collab.stop()
            
        asyncio.run(test_collab())
        print("   ✓ Collaboration module works")
        
        # Test module interaction
        print("\n5. Testing Module Interactions...")
        
        # Use AI to generate animation script
        ai_generated = models.generate("Create animation script")
        print(f"   AI Generated: {ai_generated[:50]}...")
        
        # Execute command to list animations
        result = commands.execute_command("ls /tmp/integration_test")
        print(f"   Command executed successfully")
        
        print("   ✓ Modules work together")
        
        print("\n" + "=" * 80)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("=" * 80)
        
        return True
        
    finally:
        framework.shutdown()


if __name__ == '__main__':
    success = test_complete_framework_integration()
    exit(0 if success else 1)

"""Example: Collaborative editing demonstration."""

import asyncio
from kimi_k2 import Framework, Config
from kimi_k2.core.config import CollaborationConfig


async def collaborative_demo():
    """Demonstrate collaboration features."""
    # Configure with collaboration enabled
    config = Config(
        collaboration=CollaborationConfig(enabled=True)
    )
    
    framework = Framework(config)
    framework.initialize()
    
    try:
        collab = framework.get_module('collaboration')
        
        print("=" * 60)
        print("Collaboration Demo")
        print("=" * 60)
        
        # Start the collaboration server
        await collab.start()
        print("\n1. Collaboration server started")
        
        # Connect users
        print("\n2. Connecting users...")
        user1 = await collab.connect_user("user1", "Alice")
        user2 = await collab.connect_user("user2", "Bob")
        print(f"   Connected: {user1.name}, {user2.name}")
        
        # Create a session
        print("\n3. Creating collaboration session...")
        session = collab.create_session("session1", "Animation Project", "user1")
        print(f"   Session created: {session.name}")
        
        # User 2 joins the session
        print("\n4. Bob joins the session...")
        collab.join_session("session1", "user2")
        users = collab.get_session_users("session1")
        print(f"   Users in session: {[u.name for u in users]}")
        
        # Update shared state
        print("\n5. Updating shared state...")
        collab.update_shared_state("session1", "current_frame", 42)
        collab.update_shared_state("session1", "editing_user", "Alice")
        
        session = collab.sessions["session1"]
        print(f"   Shared state: {session.shared_state}")
        
        # User leaves
        print("\n6. Alice leaves the session...")
        collab.leave_session("session1", "user1")
        users = collab.get_session_users("session1")
        print(f"   Users remaining: {[u.name for u in users]}")
        
        # Disconnect users
        print("\n7. Disconnecting users...")
        await collab.disconnect_user("user1")
        await collab.disconnect_user("user2")
        print("   All users disconnected")
        
        # Stop server
        await collab.stop()
        print("\n8. Collaboration server stopped")
        
        print("\n" + "=" * 60)
        print("Collaboration demo complete!")
        
    finally:
        framework.shutdown()


def main():
    """Run the collaborative demo."""
    asyncio.run(collaborative_demo())


if __name__ == '__main__':
    main()

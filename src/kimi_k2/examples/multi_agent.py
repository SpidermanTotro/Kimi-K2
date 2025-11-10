"""Example: Multi-agent conversation system using Kimi-K2."""

from typing import List, Dict
from kimi_k2.client import KimiClient


class Agent:
    """Represents an AI agent with a specific role."""

    def __init__(self, name: str, role: str, client: KimiClient):
        """Initialize an agent.

        Args:
            name: Agent's name
            role: Agent's role description
            client: KimiClient instance
        """
        self.name = name
        self.role = role
        self.client = client
        self.conversation_history: List[Dict[str, str]] = []

    def respond(self, message: str, context: str = "") -> str:
        """Generate a response to a message.

        Args:
            message: Input message
            context: Optional context from other agents

        Returns:
            Agent's response
        """
        system_message = f"You are {self.name}, a {self.role}. {context}"

        messages = [{"role": "system", "content": system_message}]

        # Add conversation history
        messages.extend(self.conversation_history[-6:])  # Keep last 3 exchanges

        # Add current message
        messages.append({"role": "user", "content": message})

        response = self.client.chat(messages, temperature=0.7)

        # Update history
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": response})

        return response


def main():
    """Run multi-agent conversation example."""
    # Initialize client
    client = KimiClient(base_url="http://localhost:8000", model_name="kimi-k2")

    print("=== Multi-Agent Conversation System ===\n")

    # Example 1: Product development team
    print("Example 1: Product Development Team")
    print("-" * 50)

    product_manager = Agent(
        "Alice", "product manager focused on user needs and business value", client
    )

    engineer = Agent(
        "Bob", "senior software engineer focused on technical implementation", client
    )

    designer = Agent(
        "Carol", "UX designer focused on user experience and interface design", client
    )

    # Simulate a product discussion
    task = "Design a new feature for a mobile app that helps users track their daily water intake."

    print(f"\nTask: {task}\n")

    # PM starts the discussion
    pm_response = product_manager.respond(
        f"We need to {task}. What are your initial thoughts?"
    )
    print(f"{product_manager.name} (PM): {pm_response}\n")

    # Engineer responds
    eng_response = engineer.respond(
        f"The PM said: {pm_response}. What's your technical perspective?"
    )
    print(f"{engineer.name} (Engineer): {eng_response}\n")

    # Designer responds
    design_response = designer.respond(
        f"The engineer mentioned: {eng_response}. What about the UX design?"
    )
    print(f"{designer.name} (Designer): {design_response}\n")

    # PM synthesizes
    final_response = product_manager.respond(
        f"Based on the engineer's view ({eng_response[:100]}...) and "
        f"the designer's view ({design_response[:100]}...), "
        f"what should be our final approach?"
    )
    print(f"{product_manager.name} (PM - Final): {final_response}\n")

    # Example 2: Debate between agents
    print("\nExample 2: AI Debate")
    print("-" * 50)

    advocate = Agent(
        "Dr. Smith", "advocate who argues in favor of the proposition", client
    )

    opponent = Agent(
        "Dr. Johnson", "opponent who argues against the proposition", client
    )

    moderator = Agent(
        "Moderator", "neutral moderator who facilitates the debate", client
    )

    topic = "Remote work is more productive than office work"

    print(f"\nDebate Topic: {topic}\n")

    # Round 1
    advocate_arg = advocate.respond(
        f"Present your opening argument in favor of: {topic}"
    )
    print(f"{advocate.name} (For): {advocate_arg}\n")

    opponent_arg = opponent.respond(f"Present your opening argument against: {topic}")
    print(f"{opponent.name} (Against): {opponent_arg}\n")

    # Moderator summary
    summary = moderator.respond(
        f"Summarize the key points from both sides:\n"
        f"For: {advocate_arg[:150]}...\n"
        f"Against: {opponent_arg[:150]}..."
    )
    print(f"{moderator.name}: {summary}\n")

    # Example 3: Collaborative storytelling
    print("\nExample 3: Collaborative Storytelling")
    print("-" * 50)

    narrator = Agent(
        "Narrator", "storyteller who sets scenes and describes events", client
    )

    character1 = Agent("Elena", "a brave explorer character in the story", client)

    character2 = Agent("Marcus", "a wise scientist character in the story", client)

    # Story beginning
    scene = narrator.respond(
        "Start a science fiction story about discovering an ancient alien artifact"
    )
    print(f"{narrator.name}: {scene}\n")

    # Characters respond
    elena_action = character1.respond(
        f"You are in this situation: {scene}. What do you do or say? (Stay in character)"
    )
    print(f"{character1.name}: {elena_action}\n")

    marcus_action = character2.respond(
        f"Elena just did this: {elena_action}. What is your response? (Stay in character)"
    )
    print(f"{character2.name}: {marcus_action}\n")

    # Narrator continues
    continuation = narrator.respond(
        f"Continue the story based on these actions: Elena - {elena_action[:100]}..., "
        f"Marcus - {marcus_action[:100]}..."
    )
    print(f"{narrator.name}: {continuation}\n")


if __name__ == "__main__":
    main()

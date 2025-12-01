"""
NEXUS AI - Main CLI Interface
Simple command-line interface for Nexus AI
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import print as rprint

from config.settings import config
from agents.code_agent import CodeAgent
from models.gpt_handler import GPTHandler
from models.reasoning_handler import ReasoningHandler
from models.model_router import ModelRouter
from utils.logger import logger

console = Console()

def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              🚀 NEXUS AI - Intelligence System            ║
    ║                                                           ║
    ║         Multi-Agent AI with Advanced Reasoning            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print("\n[yellow]Available Commands:[/yellow]")
    console.print("  • [green]chat[/green]     - General conversation")
    console.print("  • [green]code[/green]     - Code generation and execution")
    console.print("  • [green]reason[/green]   - Deep reasoning (o1 model)")
    console.print("  • [green]help[/green]     - Show help")
    console.print("  • [green]exit[/green]     - Exit Nexus AI")
    console.print()

def chat_mode():
    """Interactive chat mode"""
    console.print("\n[bold green]Chat Mode[/bold green] - Using GPT-4 Turbo")
    console.print("[dim]Type 'back' to return to main menu[/dim]\n")
    
    handler = GPTHandler()
    conversation = []
    
    while True:
        user_input = Prompt.ask("[bold blue]You[/bold blue]")
        
        if user_input.lower() in ['back', 'exit', 'quit']:
            break
        
        # Add to conversation
        conversation.append({"role": "user", "content": user_input})
        
        # Get response
        console.print("\n[bold cyan]Nexus AI[/bold cyan]: ", end="")
        response = handler.chat(conversation)
        
        if "error" in response:
            console.print(f"[red]Error: {response['error']}[/red]")
        else:
            console.print(Markdown(response["content"]))
            conversation.append({"role": "assistant", "content": response["content"]})
            
            # Show token usage
            usage = response.get("usage", {})
            console.print(f"\n[dim]Tokens: {usage.get('total_tokens', 0)}[/dim]\n")

def code_mode():
    """Interactive code mode"""
    console.print("\n[bold green]Code Mode[/bold green] - Code Agent with Execution")
    console.print("[dim]Type 'back' to return to main menu[/dim]\n")
    
    agent = CodeAgent()
    
    while True:
        user_input = Prompt.ask("[bold blue]Coding Task[/bold blue]")
        
        if user_input.lower() in ['back', 'exit', 'quit']:
            break
        
        # Process with code agent
        console.print("\n[bold cyan]Processing...[/bold cyan]\n")
        result = agent.process(user_input)
        
        # Show explanation
        console.print(Panel(Markdown(result["explanation"]), title="Explanation"))
        
        # Show execution results
        if result["execution_results"]:
            console.print("\n[bold yellow]Execution Results:[/bold yellow]")
            for exec_result in result["execution_results"]:
                console.print(f"\n[cyan]Block {exec_result['block_number']}:[/cyan]")
                
                if exec_result["success"]:
                    console.print("[green]✓ Success[/green]")
                    if exec_result["output"]:
                        console.print(f"Output:\n{exec_result['output']}")
                else:
                    console.print("[red]✗ Failed[/red]")
                    console.print(f"Error:\n{exec_result['error']}")
        
        console.print()

def reason_mode():
    """Interactive reasoning mode"""
    console.print("\n[bold green]Reasoning Mode[/bold green] - Using o1-mini")
    console.print("[dim]Type 'back' to return to main menu[/dim]\n")
    
    handler = ReasoningHandler()
    
    while True:
        user_input = Prompt.ask("[bold blue]Problem to Solve[/bold blue]")
        
        if user_input.lower() in ['back', 'exit', 'quit']:
            break
        
        # Get reasoning response
        console.print("\n[bold cyan]Reasoning...[/bold cyan]\n")
        result = handler.solve_problem(user_input)
        
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
        else:
            console.print(Panel(Markdown(result["answer"]), title="Solution"))
            
            # Show token usage
            usage = result.get("usage", {})
            console.print(f"\n[dim]Tokens: {usage.get('total_tokens', 0)} (Reasoning: {usage.get('reasoning_tokens', 0)})[/dim]\n")

def show_help():
    """Show help information"""
    help_text = """
    # Nexus AI Help
    
    ## Available Modes
    
    ### Chat Mode
    General conversation using GPT-4 Turbo. Best for:
    - General questions
    - Explanations
    - Creative tasks
    - Casual conversation
    
    ### Code Mode
    Code generation and execution using Code Agent. Best for:
    - Writing Python code
    - Debugging code
    - Code optimization
    - Code reviews
    
    ### Reasoning Mode
    Deep reasoning using o1 models. Best for:
    - Complex math problems
    - Logic puzzles
    - Step-by-step problem solving
    - Analytical tasks
    
    ## Tips
    - Be specific in your requests
    - Provide context when needed
    - Use 'back' to return to main menu
    - Use 'exit' to quit Nexus AI
    """
    console.print(Markdown(help_text))

def main():
    """Main CLI loop"""
    
    # Check API key
    if not config.OPENAI_API_KEY:
        console.print("[red]Error: OPENAI_API_KEY not set in environment[/red]")
        console.print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    print_banner()
    
    while True:
        try:
            command = Prompt.ask(
                "\n[bold magenta]Select mode[/bold magenta]",
                choices=["chat", "code", "reason", "help", "exit"],
                default="chat"
            )
            
            if command == "chat":
                chat_mode()
            elif command == "code":
                code_mode()
            elif command == "reason":
                reason_mode()
            elif command == "help":
                show_help()
            elif command == "exit":
                console.print("\n[cyan]Thank you for using Nexus AI! 👋[/cyan]\n")
                break
                
        except KeyboardInterrupt:
            console.print("\n\n[cyan]Goodbye! 👋[/cyan]\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {str(e)}[/red]\n")
            logger.error(f"Main loop error: {str(e)}")

if __name__ == "__main__":
    main()
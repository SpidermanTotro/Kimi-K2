"""Command-line interface for Kimi-K2."""

import click
import json
import sys
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from kimi_k2.client import KimiClient

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Kimi-K2 Command Line Interface.

    Interact with Kimi-K2 models from the command line.
    """
    pass


@cli.command()
@click.option("--url", required=True, help="Base URL of Kimi-K2 service")
@click.option("--model", default="kimi-k2", help="Model name")
@click.option("--api-key", default="dummy", help="API key")
@click.option("--system", help="System message")
@click.option(
    "--temperature", type=float, default=0.6, help="Temperature (default: 0.6)"
)
@click.option("--max-tokens", type=int, default=2048, help="Max tokens")
@click.option("--stream/--no-stream", default=False, help="Stream output")
@click.argument("message", required=False)
def chat(
    url: str,
    model: str,
    api_key: str,
    system: Optional[str],
    temperature: float,
    max_tokens: int,
    stream: bool,
    message: Optional[str],
):
    """Send a chat message to Kimi-K2.

    Examples:
        kimi-cli chat --url http://localhost:8000 "Hello, Kimi!"
        kimi-cli chat --url http://localhost:8000 --system "You are a helpful coding assistant" "Write a Python function"
    """
    client = KimiClient(
        base_url=url,
        api_key=api_key,
        model_name=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Read from stdin if no message provided
    if not message:
        if not sys.stdin.isatty():
            message = sys.stdin.read().strip()
        else:
            console.print("[yellow]No message provided. Use --help for usage.[/yellow]")
            return

    console.print(Panel(f"[cyan]{message}[/cyan]", title="User", border_style="cyan"))

    try:
        if stream:
            console.print(Panel("", title="Assistant", border_style="green"))
            response_text = ""
            for chunk in client.chat(
                messages=(
                    [{"role": "user", "content": message}]
                    if not system
                    else [
                        {"role": "system", "content": system},
                        {"role": "user", "content": message},
                    ]
                ),
                stream=True,
            ):
                console.print(chunk, end="")
                response_text += chunk
            console.print()
        else:
            response = client.simple_chat(message, system_message=system)
            console.print(
                Panel(Markdown(response), title="Assistant", border_style="green")
            )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--url", required=True, help="Base URL of Kimi-K2 service")
@click.option("--model", default="kimi-k2", help="Model name")
@click.option("--api-key", default="dummy", help="API key")
@click.option("--temperature", type=float, default=0.6, help="Temperature")
def interactive(url: str, model: str, api_key: str, temperature: float):
    """Start an interactive chat session.

    Example:
        kimi-cli interactive --url http://localhost:8000
    """
    client = KimiClient(
        base_url=url, api_key=api_key, model_name=model, temperature=temperature
    )

    messages = []
    console.print(
        Panel(
            "[green]Kimi-K2 Interactive Chat[/green]\n"
            "Type your messages and press Enter.\n"
            "Commands: /quit, /clear, /help",
            border_style="blue",
        )
    )

    while True:
        try:
            user_input = console.input("\n[cyan]You:[/cyan] ")

            if user_input.strip() == "/quit":
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif user_input.strip() == "/clear":
                messages = []
                console.print("[yellow]Chat history cleared.[/yellow]")
                continue
            elif user_input.strip() == "/help":
                console.print(
                    "[yellow]Commands:[/yellow]\n"
                    "  /quit  - Exit the chat\n"
                    "  /clear - Clear chat history\n"
                    "  /help  - Show this help"
                )
                continue
            elif not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            response = client.chat(messages)
            messages.append({"role": "assistant", "content": response})

            console.print(f"\n[green]Kimi:[/green] {response}")

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    cli()

"""Main CLI interface for Kimi-K2 Framework."""

import click
import logging
from pathlib import Path
from typing import Optional

from kimi_k2 import Framework, Config
from kimi_k2.core.config import (
    AnimationConfig,
    CommandsConfig,
    ModelsConfig,
    UIConfig,
    CollaborationConfig
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0', prog_name='kimi-k2')
@click.option('--config', type=click.Path(), help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Kimi-K2 Unified AI Framework.
    
    A comprehensive framework for animation, commands, and AI models.
    """
    ctx.ensure_object(dict)
    
    if config:
        ctx.obj['config'] = Config.load_from_file(Path(config))
    else:
        ctx.obj['config'] = Config.default()


@cli.group()
def animation():
    """Animation suite commands."""
    pass


@animation.command('create')
@click.argument('project_name')
@click.option('--fps', type=int, default=30, help='Frames per second')
@click.option('--duration', type=float, default=10.0, help='Duration in seconds')
@click.option('--quality', type=click.Choice(['draft', 'tv', 'cinema']), default='tv', help='Quality preset')
@click.pass_context
def animation_create(ctx, project_name, fps, duration, quality):
    """Create a new animation project."""
    config = ctx.obj['config']
    framework = Framework(config)
    framework.initialize()
    
    try:
        animation_suite = framework.get_module('animation')
        project = animation_suite.create_project(
            name=project_name,
            fps=fps,
            duration=duration,
            quality=quality
        )
        click.echo(f"✓ Created animation project: {project_name}")
        click.echo(f"  FPS: {fps}, Duration: {duration}s, Quality: {quality}")
    finally:
        framework.shutdown()


@animation.command('render')
@click.argument('project_name')
@click.pass_context
def animation_render(ctx, project_name):
    """Render an animation project."""
    config = ctx.obj['config']
    framework = Framework(config)
    framework.initialize()
    
    try:
        animation_suite = framework.get_module('animation')
        output_path = animation_suite.render_project(project_name)
        click.echo(f"✓ Rendered project to: {output_path}")
    finally:
        framework.shutdown()


@cli.group()
def cmd():
    """Command interface operations."""
    pass


@cmd.command('exec')
@click.argument('command', nargs=-1, required=True)
@click.pass_context
def cmd_exec(ctx, command):
    """Execute a command."""
    config = ctx.obj['config']
    framework = Framework(config)
    framework.initialize()
    
    try:
        cmd_interface = framework.get_module('commands')
        command_line = ' '.join(command)
        result = cmd_interface.execute_command(command_line)
        
        if result['success']:
            click.echo(result['result'])
        else:
            click.echo(f"Error: {result['error']}", err=True)
    finally:
        framework.shutdown()


@cmd.command('gen-script')
@click.argument('description', nargs=-1, required=True)
@click.option('--language', default='bash', help='Script language')
@click.pass_context
def cmd_gen_script(ctx, description, language):
    """Generate a script from description."""
    config = ctx.obj['config']
    framework = Framework(config)
    framework.initialize()
    
    try:
        cmd_interface = framework.get_module('commands')
        desc_text = ' '.join(description)
        script = cmd_interface.script_generator.generate_script(desc_text, language)
        click.echo(script)
    finally:
        framework.shutdown()


@cli.group()
def model():
    """AI model management."""
    pass


@model.command('list')
@click.pass_context
def model_list(ctx):
    """List available models."""
    config = ctx.obj['config']
    framework = Framework(config)
    framework.initialize()
    
    try:
        model_manager = framework.get_module('models')
        models = model_manager.list_models()
        
        click.echo("Available Models:")
        click.echo("-" * 60)
        for model_info in models:
            status = "✓ Loaded" if model_info.loaded else "○ Not loaded"
            click.echo(f"{model_info.name:15} {status:15} {model_info.memory_gb}GB  {model_info.parameters}")
    finally:
        framework.shutdown()


@model.command('generate')
@click.argument('prompt')
@click.option('--model', default='lightweight', help='Model to use')
@click.option('--max-tokens', type=int, default=100, help='Maximum tokens')
@click.pass_context
def model_generate(ctx, prompt, model, max_tokens):
    """Generate text using AI model."""
    config = ctx.obj['config']
    framework = Framework(config)
    framework.initialize()
    
    try:
        model_manager = framework.get_module('models')
        model_manager.load_model(model)
        result = model_manager.generate(prompt, max_tokens=max_tokens)
        click.echo(result)
    finally:
        framework.shutdown()


@cli.command('init')
@click.option('--output', type=click.Path(), default='kimi-k2-config.yaml', help='Output configuration file')
def init_config(output):
    """Initialize a default configuration file."""
    config = Config.default()
    config.save_to_file(Path(output))
    click.echo(f"✓ Created configuration file: {output}")


@cli.command('info')
@click.pass_context
def info(ctx):
    """Show framework information."""
    config = ctx.obj['config']
    
    click.echo("Kimi-K2 Unified AI Framework v1.0.0")
    click.echo("=" * 60)
    click.echo("\nEnabled Modules:")
    click.echo(f"  Animation:      {'✓' if config.animation.enabled else '✗'}")
    click.echo(f"  Commands:       {'✓' if config.commands.enabled else '✗'}")
    click.echo(f"  Models:         {'✓' if config.models.enabled else '✗'}")
    click.echo(f"  Collaboration:  {'✓' if config.collaboration.enabled else '✗'}")
    click.echo("\nConfiguration:")
    click.echo(f"  Animation Quality: {config.animation.quality_preset}")
    click.echo(f"  Default Model:     {config.models.default_model}")
    click.echo(f"  Max Memory:        {config.models.max_memory_gb}GB")


if __name__ == '__main__':
    cli(obj={})

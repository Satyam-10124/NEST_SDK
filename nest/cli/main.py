#!/usr/bin/env python3
"""
NEST SDK CLI - Main entry point

Usage:
    nest --help
    nest init my-project
    nest create agent
    nest dev
    nest deploy
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional
import sys

# Create CLI app
app = typer.Typer(
    name="nest",
    help="🪺 NEST SDK - Build AI Agents with Agent-to-Agent Communication",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()

# Try to import command modules (they may not all exist yet)
try:
    from nest.cli.commands import create, dev, deploy, test, monitor
    HAS_COMMANDS = True
except ImportError:
    HAS_COMMANDS = False

# Register commands if available
if HAS_COMMANDS:
    try:
        app.add_typer(create.app, name="create", help="🎨 Create new agents")
    except:
        pass
    
    try:
        app.add_typer(dev.app, name="dev", help="🔥 Development server")
    except:
        pass
    
    try:
        app.add_typer(deploy.app, name="deploy", help="☁️  Deploy to cloud")
    except:
        pass
    
    try:
        app.add_typer(test.app, name="test", help="🧪 Test agents")
    except:
        pass
    
    try:
        app.add_typer(monitor.app, name="monitor", help="📊 Monitor agents")
    except:
        pass


@app.command()
def version():
    """Show NEST SDK version"""
    from nest import __version__
    
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]🪺 NEST SDK v{__version__}[/bold cyan]\n"
        "[dim]Build AI Agents with Agent-to-Agent Communication[/dim]\n\n"
        "[green]✨ Create agents in 5 lines of code[/green]\n"
        "[yellow]💬 Agent-to-agent communication built-in[/yellow]\n"
        "[blue]☁️  One-command cloud deployment[/blue]",
        border_style="cyan",
        title="🎉 Welcome"
    ))
    console.print()


@app.command()
def list(
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all registered agents"""
    try:
        from nest import NestClient
        from nest.config import NestConfig
        import os
        
        # Try to load config, fallback to env
        try:
            config = NestConfig.load()
            registry_url = config.registry_url
        except:
            registry_url = os.getenv("NEST_REGISTRY_URL", "http://registry.nanda.ai")
        
        if not registry_url:
            console.print("[red]❌ No registry URL configured[/red]")
            console.print("Set NEST_REGISTRY_URL environment variable or create nest.config.yaml")
            raise typer.Exit(code=1)
        
        client = NestClient(registry_url)
        agents = client.list_agents(status=status)
        
        if json_output:
            import json
            console.print(json.dumps([vars(agent) for agent in agents], indent=2))
        else:
            if not agents:
                console.print("[yellow]No agents found[/yellow]")
                return
            
            table = Table(title="🤖 NEST Agents", show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("URL", style="blue")
            
            for agent in agents:
                status_emoji = "✅" if agent.status == "active" else "⚠️"
                table.add_row(
                    agent.id,
                    agent.name,
                    f"{status_emoji} {agent.status}",
                    agent.url
                )
            
            console.print(table)
            console.print(f"\n[bold]Total:[/bold] {len(agents)} agent(s)")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def info(agent_id: str):
    """Show detailed agent information"""
    try:
        from nest import NestClient
        from nest.config import NestConfig
        import os
        
        try:
            config = NestConfig.load()
            registry_url = config.registry_url
        except:
            registry_url = os.getenv("NEST_REGISTRY_URL")
        
        if not registry_url:
            console.print("[red]❌ No registry URL configured[/red]")
            raise typer.Exit(code=1)
        
        client = NestClient(registry_url)
        agent = client.get_agent(agent_id)
        
        console.print(f"\n[bold cyan]🤖 Agent Information[/bold cyan]")
        console.print(f"[bold]ID:[/bold] {agent.id}")
        console.print(f"[bold]Name:[/bold] {agent.name}")
        console.print(f"[bold]URL:[/bold] {agent.url}")
        console.print(f"[bold]Status:[/bold] {agent.status}")
        
        if agent.capabilities:
            console.print(f"[bold]Capabilities:[/bold]")
            for cap in agent.capabilities:
                console.print(f"  • {cap}")
        
        # Health check
        try:
            health = client.health_check(agent_id)
            status_color = "green" if health.get('status') == 'healthy' else "red"
            console.print(f"\n[bold {status_color}]Health:[/bold {status_color}] {health.get('status', 'unknown')}")
        except:
            pass
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def init(
    project_name: Optional[str] = typer.Argument(None, help="Project name"),
    template: Optional[str] = typer.Option(None, "--template", help="Template to use"),
):
    """Initialize a new NEST project"""
    console.print("\n[bold cyan]🪺 NEST Project Initialization[/bold cyan]\n")
    
    if not project_name:
        import questionary
        project_name = questionary.text(
            "Project name:",
            default="my-nest-project"
        ).ask()
    
    if not project_name:
        console.print("[red]Project name is required[/red]")
        raise typer.Exit(code=1)
    
    from pathlib import Path
    from nest.config import NestConfig
    
    project_path = Path.cwd() / project_name
    
    if project_path.exists():
        console.print(f"[yellow]⚠️  Directory {project_path} already exists[/yellow]")
        import questionary
        if not questionary.confirm("Continue anyway?").ask():
            console.print("[yellow]Aborted[/yellow]")
            raise typer.Exit()
    
    # Create project structure
    console.print(f"📁 Creating project: {project_name}")
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "agents").mkdir(exist_ok=True)
    (project_path / "tests").mkdir(exist_ok=True)
    
    # Create config
    config = NestConfig.create_default(project_name)
    config.save(str(project_path / "nest.config.yaml"))
    
    # Create .env.example
    env_content = """# NEST SDK Environment Variables

# Anthropic API Key (required for LLM agents)
ANTHROPIC_API_KEY=your-api-key-here

# NEST Registry URL
NEST_REGISTRY_URL=http://registry.nanda.ai

# MCP Registry URL (optional)
MCP_REGISTRY_URL=

# Smithery API Key (optional, for MCP)
SMITHERY_API_KEY=

# Default agent settings
PORT=6000
"""
    (project_path / ".env.example").write_text(env_content)
    
    # Create README
    readme_content = f"""# {project_name}

NEST SDK Project - AI Agents with A2A Communication

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install nest-sdk
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Create an agent:**
   ```bash
   nest create agent
   ```

4. **Run locally:**
   ```bash
   nest dev
   ```

5. **Deploy to cloud:**
   ```bash
   nest deploy --provider aws
   ```

## Documentation

- [NEST SDK Docs](https://github.com/projnanda/NEST)
- [API Reference](https://github.com/projnanda/NEST/docs)

## Support

For issues and questions, visit: https://github.com/projnanda/NEST/issues
"""
    (project_path / "README.md").write_text(readme_content)
    
    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# NEST
.env
*.log
logs/
pids/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    (project_path / ".gitignore").write_text(gitignore_content)
    
    console.print("\n[bold green]✅ Project initialized successfully![/bold green]")
    console.print(f"\nNext steps:")
    console.print(f"  1. [cyan]cd {project_name}[/cyan]")
    console.print(f"  2. [cyan]cp .env.example .env[/cyan]")
    console.print(f"  3. [cyan]# Add your ANTHROPIC_API_KEY to .env[/cyan]")
    console.print(f"  4. [cyan]nest create agent[/cyan]")
    console.print(f"  5. [cyan]nest dev[/cyan]")
    console.print()


@app.command()
def templates():
    """📋 List available agent templates"""
    from nest.templates import list_templates, get_template_info
    from rich import box
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]📋 Agent Templates[/bold cyan]\n"
        "[dim]Pre-built agents for common use cases[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    available = list_templates()
    
    if not available:
        console.print("[yellow]⚠️  No templates found[/yellow]\n")
        return
    
    table = Table(
        show_header=True, 
        header_style="bold magenta",
        box=box.ROUNDED,
        title="🎨 Available Templates"
    )
    table.add_column("Template", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Tags", style="dim")
    
    for template_name in available:
        try:
            info = get_template_info(template_name)
            description = info.get('description', 'No description')
            tags = ", ".join(info.get('tags', []))
            table.add_row(template_name, description, tags)
        except:
            table.add_row(template_name, "", "")
    
    console.print(table)
    console.print(f"\n[bold]💡 Usage:[/bold]")
    console.print(f"  [cyan]nest create agent --template <name>[/cyan]")
    console.print(f"\n[bold]Example:[/bold]")
    console.print(f"  [dim]nest create agent --template customer-support[/dim]")
    console.print()


def main():
    """Main entry point for CLI"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]⏸️  Interrupted[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

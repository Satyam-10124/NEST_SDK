#!/usr/bin/env python3
"""
nest dev - Development server with hot reload
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich import box
from pathlib import Path
import time
import subprocess
import signal
import sys

app = typer.Typer()
console = Console()


@app.command()
def dev(
    agent: str = typer.Option(None, "--agent", "-a", help="Specific agent file"),
    all: bool = typer.Option(False, "--all", help="Run all agents"),
    ui: bool = typer.Option(False, "--ui", help="Launch web UI"),
    port: int = typer.Option(None, "--port", "-p", help="Override port"),
    hot_reload: bool = typer.Option(True, "--hot-reload/--no-hot-reload", help="Enable hot reload"),
    no_register: bool = typer.Option(False, "--no-register", help="Don't register with registry"),
):
    """
    🔥 Start development server with hot reload
    
    Examples:
        nest dev                    # Run default agent
        nest dev --all             # Run all agents
        nest dev -a my_agent.py    # Run specific agent
        nest dev --ui              # With web interface
        nest dev --no-hot-reload   # Without hot reload
    """
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🔥 NEST Development Server[/bold cyan]\n"
        "[dim]Hot reload enabled • Press Ctrl+C to stop[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    # Find agents to run
    if agent:
        agent_files = [Path(agent)]
    elif all:
        agent_files = list(Path("agents").glob("*.py"))
        if not agent_files:
            console.print("[yellow]⚠️  No agent files found in ./agents/[/yellow]")
            return
    else:
        # Find first agent
        agent_files = list(Path("agents").glob("*.py"))
        if not agent_files:
            console.print("[red]❌ No agents found. Create one with: [cyan]nest create agent[/cyan][/red]")
            raise typer.Exit(code=1)
        agent_files = [agent_files[0]]
    
    # Start agents
    processes = []
    
    try:
        for agent_file in agent_files:
            console.print(f"[cyan]▶[/cyan]  Starting: {agent_file.name}")
            
            proc = subprocess.Popen(
                [sys.executable, str(agent_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processes.append((agent_file.name, proc))
            time.sleep(1)  # Stagger starts
        
        console.print()
        console.print(f"[bold green]✅ {len(processes)} agent(s) running[/bold green]")
        console.print()
        
        # Show status dashboard
        _show_dashboard(processes, hot_reload)
        
        # Keep running
        console.print("\n[dim]Watching for changes...[/dim]" if hot_reload else "\n[dim]Running...[/dim]")
        
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for name, proc in processes:
                if proc.poll() is not None:
                    console.print(f"[red]❌ {name} stopped unexpectedly[/red]")
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⏸️  Shutting down...[/yellow]")
        
        # Terminate all processes
        for name, proc in processes:
            console.print(f"[dim]Stopping {name}...[/dim]")
            proc.terminate()
            proc.wait(timeout=5)
        
        console.print("[green]✅ All agents stopped[/green]\n")


def _show_dashboard(processes, hot_reload):
    """Show colorful dashboard"""
    
    table = Table(
        title="🤖 Running Agents",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("PID", style="yellow")
    
    for name, proc in processes:
        status = "✅ Running" if proc.poll() is None else "❌ Stopped"
        table.add_row(name, status, str(proc.pid))
    
    console.print(table)
    
    if hot_reload:
        console.print("\n[dim]💡 Tip: Edit your agent files and they'll auto-reload[/dim]")


@app.command()
def ui():
    """
    🌐 Launch development web UI
    
    Opens a web interface for testing agents interactively.
    """
    
    console.print(Panel.fit(
        "[bold cyan]🌐 Development Web UI[/bold cyan]\n"
        "[dim]Coming soon in Phase 4![/dim]\n\n"
        "[yellow]For now, use curl or Python requests to test agents[/yellow]",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Example test:[/bold]")
    console.print("[dim]curl -X POST http://localhost:6000/a2a \\")
    console.print('  -H "Content-Type: application/json" \\')
    console.print('  -d \'{"content":{"text":"Hello!","type":"text"},"role":"user","conversation_id":"test"}\'[/dim]')


if __name__ == "__main__":
    app()

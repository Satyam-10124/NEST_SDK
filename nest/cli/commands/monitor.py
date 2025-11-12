#!/usr/bin/env python3
"""
nest monitor - Monitor agents in real-time
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich import box
import time

app = typer.Typer()
console = Console()


@app.command()
def monitor(
    agent: str = typer.Option(None, "--agent", "-a", help="Monitor specific agent"),
    refresh: int = typer.Option(2, "--refresh", "-r", help="Refresh interval (seconds)"),
):
    """
    📊 Monitor agents in real-time
    
    Examples:
        nest monitor                 # Monitor all agents
        nest monitor -a my-agent    # Monitor specific agent
        nest monitor -r 5           # Refresh every 5 seconds
    """
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]📊 NEST Agent Monitor[/bold cyan]\n"
        "[dim]Press Ctrl+C to exit[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    try:
        _show_dashboard(agent, refresh)
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped[/yellow]\n")


def _show_dashboard(agent_filter, refresh_interval):
    """Show live monitoring dashboard"""
    
    def generate_dashboard():
        """Generate dashboard layout"""
        
        # Agent status table
        status_table = Table(
            title="🤖 Agent Status",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        
        status_table.add_column("Agent", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Requests", style="yellow")
        status_table.add_column("Avg Response", style="blue")
        status_table.add_column("Memory", style="magenta")
        
        # Sample data (would be real in production)
        status_table.add_row("customer-support", "✅ Running", "1,234", "1.2s", "180 MB")
        status_table.add_row("data-analyst", "✅ Running", "567", "2.5s", "220 MB")
        status_table.add_row("code-reviewer", "⏸️  Paused", "0", "-", "150 MB")
        
        # Performance metrics
        metrics_table = Table(
            title="📈 Performance Metrics",
            box=box.ROUNDED,
            show_header=False
        )
        
        metrics_table.add_column("Metric", style="bold")
        metrics_table.add_column("Value", style="cyan")
        
        metrics_table.add_row("Total Requests", "1,801")
        metrics_table.add_row("Success Rate", "99.5%")
        metrics_table.add_row("Avg Response Time", "1.8s")
        metrics_table.add_row("Active Connections", "12")
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(status_table, name="status"),
            Layout(metrics_table, name="metrics")
        )
        
        return layout
    
    # Live updating dashboard
    with Live(generate_dashboard(), refresh_per_second=1/refresh_interval, console=console) as live:
        while True:
            time.sleep(refresh_interval)
            live.update(generate_dashboard())


if __name__ == "__main__":
    app()

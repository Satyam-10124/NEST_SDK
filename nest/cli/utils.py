"""
Utility functions for CLI
"""

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import box
from typing import List, Dict, Any
import time

console = Console()


def print_banner(title: str, subtitle: str = "", style: str = "cyan"):
    """Print a colorful banner"""
    text = f"[bold {style}]{title}[/bold {style}]"
    if subtitle:
        text += f"\n[dim]{subtitle}[/dim]"
    
    console.print()
    console.print(Panel.fit(text, border_style=style))
    console.print()


def print_success(message: str, details: Dict[str, Any] = None):
    """Print success message with optional details"""
    text = f"[bold green]✅ {message}[/bold green]"
    
    if details:
        text += "\n\n"
        for key, value in details.items():
            text += f"[bold]{key}:[/bold] {value}\n"
    
    console.print(Panel.fit(text, border_style="green", title="Success"))


def print_error(message: str, hint: str = None):
    """Print error message with optional hint"""
    text = f"[bold red]❌ {message}[/bold red]"
    
    if hint:
        text += f"\n\n[dim]💡 Hint: {hint}[/dim]"
    
    console.print(Panel.fit(text, border_style="red", title="Error"))


def print_warning(message: str):
    """Print warning message"""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def print_info(message: str):
    """Print info message"""
    console.print(f"[cyan]ℹ️  {message}[/cyan]")


def show_progress(description: str, total: int = None):
    """Show progress spinner or bar"""
    if total:
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        )
    else:
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        )


def create_table(title: str, columns: List[str], rows: List[List[str]], 
                 show_header: bool = True, box_style=box.ROUNDED):
    """Create a formatted table"""
    table = Table(
        title=title,
        box=box_style,
        show_header=show_header,
        header_style="bold magenta"
    )
    
    # Add columns
    styles = ["cyan", "green", "yellow", "blue", "magenta"]
    for i, col in enumerate(columns):
        style = styles[i % len(styles)]
        table.add_column(col, style=style)
    
    # Add rows
    for row in rows:
        table.add_row(*row)
    
    return table


def animate_text(text: str, delay: float = 0.03):
    """Animate text character by character"""
    for char in text:
        console.print(char, end="")
        time.sleep(delay)
    console.print()


def print_code(code: str, language: str = "python"):
    """Print syntax-highlighted code"""
    from rich.syntax import Syntax
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)

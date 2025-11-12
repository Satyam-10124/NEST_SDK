#!/usr/bin/env python3
"""
nest create - Interactive agent creation wizard
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
import questionary
from pathlib import Path

from nest.templates import list_templates, get_template_info
from nest.exceptions import TemplateNotFoundError

app = typer.Typer()
console = Console()


@app.command()
def agent(
    template: str = typer.Option(None, "--template", "-t", help="Template name"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    🤖 Create a new agent (interactive wizard)
    
    Examples:
        nest create agent                      # Interactive wizard
        nest create agent -t customer-support  # From template
        nest create agent --no-interactive     # Quick mode
    """
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🤖 Agent Creation Wizard[/bold cyan]\n"
        "[dim]Let's build your AI agent together![/dim]",
        border_style="cyan"
    ))
    console.print()
    
    if not interactive and not template:
        console.print("[red]❌ Either use interactive mode or specify --template[/red]")
        raise typer.Exit(code=1)
    
    # Interactive wizard
    if interactive:
        agent_config = _interactive_wizard()
    else:
        # Quick mode from template
        agent_config = _quick_create(template)
    
    # Generate agent code
    _generate_agent_code(agent_config, output)
    
    console.print()
    console.print(Panel.fit(
        f"[bold green]✅ Agent created successfully![/bold green]\n\n"
        f"[bold]Agent ID:[/bold] {agent_config['id']}\n"
        f"[bold]Name:[/bold] {agent_config['name']}\n"
        f"[bold]Port:[/bold] {agent_config['port']}\n\n"
        f"[dim]Next steps:[/dim]\n"
        f"  1. Review the generated file\n"
        f"  2. Run: [cyan]python {agent_config['filename']}[/cyan]\n"
        f"  3. Test: [cyan]nest test agent {agent_config['id']}[/cyan]",
        border_style="green",
        title="🎉 Success"
    ))


def _interactive_wizard():
    """Interactive wizard for agent creation"""
    
    # Step 1: Choose creation method
    console.print("[bold cyan]Step 1:[/bold cyan] Choose how to create your agent\n")
    
    creation_method = questionary.select(
        "How would you like to create your agent?",
        choices=[
            "🎨 From scratch (customize everything)",
            "📋 From template (quick start)",
            "📄 From config file (YAML/JSON)"
        ],
        style=questionary.Style([
            ('selected', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
        ])
    ).ask()
    
    if not creation_method:
        raise typer.Exit()
    
    console.print()
    
    # Handle different creation methods
    if "scratch" in creation_method:
        return _create_from_scratch()
    elif "template" in creation_method:
        return _create_from_template()
    else:
        return _create_from_config()


def _create_from_scratch():
    """Create agent from scratch with full customization"""
    
    console.print("[bold cyan]Creating agent from scratch...[/bold cyan]\n")
    
    # Basic info
    agent_id = questionary.text(
        "Agent ID (unique identifier):",
        default="my-agent",
        validate=lambda x: len(x) > 0
    ).ask()
    
    agent_name = questionary.text(
        "Agent Name (display name):",
        default=agent_id.replace("-", " ").title()
    ).ask()
    
    console.print()
    
    # LLM Configuration
    console.print("[bold cyan]LLM Configuration[/bold cyan]\n")
    
    model = questionary.select(
        "Choose LLM model:",
        choices=[
            "claude-3-haiku-20240307 (Fast & economical)",
            "claude-3-5-sonnet-20241022 (Balanced)",
            "claude-3-opus-20240229 (Most capable)"
        ]
    ).ask()
    
    model = model.split()[0]  # Extract model name
    
    temperature = questionary.text(
        "Temperature (0.0-1.0):",
        default="0.7",
        validate=lambda x: 0 <= float(x) <= 1
    ).ask()
    
    max_tokens = questionary.text(
        "Max tokens:",
        default="1000",
        validate=lambda x: int(x) > 0
    ).ask()
    
    console.print()
    
    # System prompt
    console.print("[bold cyan]Agent Personality[/bold cyan]\n")
    
    use_wizard = questionary.confirm(
        "Use prompt builder wizard?",
        default=True
    ).ask()
    
    if use_wizard:
        system_prompt = _build_system_prompt(agent_name)
    else:
        system_prompt = questionary.text(
            "Enter system prompt:",
            default=f"You are {agent_name}, a helpful AI assistant."
        ).ask()
    
    console.print()
    
    # Capabilities
    console.print("[bold cyan]Capabilities[/bold cyan]\n")
    
    capabilities = []
    while True:
        cap = questionary.text(
            f"Add capability (or press Enter to finish) [{len(capabilities)} added]:",
            default=""
        ).ask()
        
        if not cap:
            break
        capabilities.append(cap)
    
    console.print()
    
    # Port configuration
    port = questionary.text(
        "Port number:",
        default="6000",
        validate=lambda x: 1 <= int(x) <= 65535
    ).ask()
    
    return {
        'id': agent_id,
        'name': agent_name,
        'model': model,
        'temperature': float(temperature),
        'max_tokens': int(max_tokens),
        'system_prompt': system_prompt,
        'capabilities': capabilities,
        'port': int(port),
        'filename': f"agents/{agent_id.replace('-', '_')}.py"
    }


def _create_from_template():
    """Create agent from template"""
    
    console.print("[bold cyan]Creating from template...[/bold cyan]\n")
    
    # Show available templates
    templates = list_templates()
    
    if not templates:
        console.print("[red]❌ No templates found[/red]")
        raise typer.Exit(code=1)
    
    # Display templates with descriptions
    table = Table(title="📋 Available Templates", box=box.ROUNDED)
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="white")
    
    template_choices = []
    for tmpl in templates:
        try:
            info = get_template_info(tmpl)
            desc = info.get('description', 'No description')
            table.add_row(tmpl, desc)
            template_choices.append(f"{tmpl} - {desc}")
        except:
            table.add_row(tmpl, "")
            template_choices.append(tmpl)
    
    console.print(table)
    console.print()
    
    # Select template
    selected = questionary.select(
        "Choose a template:",
        choices=template_choices
    ).ask()
    
    template_name = selected.split(" - ")[0] if " - " in selected else selected
    
    # Customizations
    console.print(f"\n[bold cyan]Customizing '{template_name}' template...[/bold cyan]\n")
    
    agent_id = questionary.text(
        "Agent ID:",
        default=template_name
    ).ask()
    
    agent_name = questionary.text(
        "Agent Name:",
        default=agent_id.replace("-", " ").title()
    ).ask()
    
    port = questionary.text(
        "Port:",
        default="6000",
        validate=lambda x: 1 <= int(x) <= 65535
    ).ask()
    
    return {
        'id': agent_id,
        'name': agent_name,
        'template': template_name,
        'port': int(port),
        'filename': f"agents/{agent_id.replace('-', '_')}.py"
    }


def _create_from_config():
    """Create agent from config file"""
    
    console.print("[bold cyan]Creating from config file...[/bold cyan]\n")
    
    config_file = questionary.path(
        "Path to config file (YAML/JSON):",
        only_files=True
    ).ask()
    
    if not config_file or not Path(config_file).exists():
        console.print("[red]❌ Config file not found[/red]")
        raise typer.Exit(code=1)
    
    return {
        'config_file': config_file,
        'filename': 'agents/agent_from_config.py'
    }


def _build_system_prompt(agent_name):
    """Interactive system prompt builder"""
    
    console.print("[dim]Building system prompt...[/dim]\n")
    
    # Role
    role = questionary.text(
        f"What is {agent_name}'s role?",
        default="helpful AI assistant"
    ).ask()
    
    # Domain
    domain = questionary.text(
        "What domain/industry?",
        default="general assistance"
    ).ask()
    
    # Tone
    tone = questionary.select(
        "Communication tone:",
        choices=[
            "Professional and formal",
            "Friendly and casual",
            "Technical and precise",
            "Empathetic and supportive",
            "Educational and patient"
        ]
    ).ask()
    
    # Special instructions
    add_special = questionary.confirm(
        "Add special instructions?",
        default=False
    ).ask()
    
    special_instructions = ""
    if add_special:
        special_instructions = questionary.text(
            "Special instructions:",
            default=""
        ).ask()
    
    # Build prompt
    prompt = f"""You are {agent_name}, a {role} specializing in {domain}.

Communication Style: {tone}

Your responsibilities:
- Provide accurate and helpful information
- Maintain a {tone.lower()} tone
- Be clear and concise in your responses
- Ask clarifying questions when needed

You are part of the NANDA agent network and can communicate with other agents using @agent-id syntax.
"""
    
    if special_instructions:
        prompt += f"\n{special_instructions}"
    
    # Show preview
    console.print("\n[bold cyan]Prompt Preview:[/bold cyan]")
    console.print(Panel(prompt, border_style="dim"))
    
    if not questionary.confirm("Use this prompt?", default=True).ask():
        # Let them edit
        console.print("\n[dim]Opening editor... (paste your prompt)[/dim]")
        prompt = questionary.text(
            "System prompt:",
            default=prompt,
            multiline=True
        ).ask()
    
    return prompt


def _generate_agent_code(config, output_path=None):
    """Generate Python code for the agent"""
    
    if output_path is None:
        output_path = config.get('filename', 'agent.py')
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate code based on config
    if 'config_file' in config:
        # From config file
        code = f"""#!/usr/bin/env python3
\"\"\"
Agent created from config file
\"\"\"

from nest import Agent

def main():
    agent = Agent.from_config("{config['config_file']}")
    agent.start()

if __name__ == "__main__":
    main()
"""
    elif 'template' in config:
        # From template
        code = f"""#!/usr/bin/env python3
\"\"\"
{config['name']} - Created from '{config['template']}' template
\"\"\"

from nest import Agent

def main():
    print("🤖 Starting {config['name']}...")
    
    agent = Agent.from_template(
        "{config['template']}",
        id="{config['id']}",
        name="{config['name']}",
        port={config['port']}
    )
    
    print(f"✅ Agent ready on http://localhost:{config['port']}/a2a")
    print("🛑 Press Ctrl+C to stop\\n")
    
    agent.start()

if __name__ == "__main__":
    main()
"""
    else:
        # From scratch
        capabilities_str = ', '.join(f'"{c}"' for c in config.get('capabilities', []))
        
        code = f"""#!/usr/bin/env python3
\"\"\"
{config['name']} - Custom AI Agent

Created with NEST SDK
\"\"\"

import os
from nest import Agent

def main():
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("   Set it in your environment or .env file\\n")
    
    print("🤖 Starting {config['name']}...")
    
    # Create agent
    agent = Agent.from_llm(
        id="{config['id']}",
        name="{config['name']}",
        model="{config['model']}",
        system_prompt=\"\"\"
{config['system_prompt']}
        \"\"\",
        capabilities=[{capabilities_str}],
        temperature={config['temperature']},
        max_tokens={config['max_tokens']},
        port={config['port']}
    )
    
    print(f"✅ Agent '{agent.config.name}' ready!")
    print(f"🌐 URL: http://localhost:{config['port']}/a2a")
    print("\\n💡 Test with:")
    print(f"   curl -X POST http://localhost:{config['port']}/a2a \\\\")
    print('     -H "Content-Type: application/json" \\\\')
    print('     -d \'{{"content":{{"text":"Hello!","type":"text"}},"role":"user","conversation_id":"test"}}\'')
    print("\\n🛑 Press Ctrl+C to stop\\n")
    
    # Start agent
    agent.start()

if __name__ == "__main__":
    main()
"""
    
    # Write file
    output_file.write_text(code)
    
    # Make executable
    import stat
    output_file.chmod(output_file.stat().st_mode | stat.S_IEXEC)
    
    config['filename'] = str(output_file)


def _quick_create(template_name):
    """Quick create from template without interaction"""
    
    if not template_name:
        console.print("[red]❌ Template name required in non-interactive mode[/red]")
        raise typer.Exit(code=1)
    
    try:
        from nest.templates import load_template
        template_config = load_template(template_name)
        
        return {
            'id': template_config.get('id', template_name),
            'name': template_config.get('name', template_name.title()),
            'template': template_name,
            'port': template_config.get('port', 6000),
            'filename': f"agents/{template_name.replace('-', '_')}.py"
        }
    except TemplateNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

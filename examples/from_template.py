#!/usr/bin/env python3
"""
NEST SDK Template Example

This script shows how to create agents from templates.

Usage:
    python examples/from_template.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nest import Agent
from nest.templates import list_templates


def main():
    print("🪺 NEST SDK - Template Example\n")
    
    # List available templates
    templates = list_templates()
    print(f"📋 Available templates: {', '.join(templates)}\n")
    
    # Create agent from template
    print("Creating customer support agent from template...")
    
    agent = Agent.from_template(
        "customer-support",
        # Override template defaults
        id="my-support-agent",
        name="ACME Support",
        port=6001
    )
    
    print(f"✅ Agent created: {agent.config.name}")
    print(f"🎯 Capabilities: {', '.join(agent.config.capabilities)}")
    print(f"🌐 URL: http://localhost:{agent.config.port}/a2a")
    print("\n🛑 Press Ctrl+C to stop\n")
    
    # Start the agent
    agent.start(register=False)


if __name__ == "__main__":
    main()

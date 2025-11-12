#!/usr/bin/env python3
"""
NEST SDK Quick Start Example

This script demonstrates the simplest way to create and run a NEST agent.

Usage:
    python examples/quick_start.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nest import Agent


def main():
    print("🪺 NEST SDK - Quick Start Example\n")
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("   Set it in your environment or .env file")
        print("   The agent will use echo mode without LLM\n")
    
    # Create a simple agent (5 lines of code!)
    agent = Agent(
        id="quick-start-agent",
        name="Quick Start Assistant",
        prompt="You are a helpful AI assistant. Be friendly and concise."
    )
    
    print(f"✅ Agent created: {agent.config.name}")
    print(f"🌐 URL: http://localhost:{agent.config.port}/a2a")
    print("\n💡 Try testing with curl:")
    print(f'   curl -X POST http://localhost:{agent.config.port}/a2a \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"content":{"text":"Hello! Who are you?","type":"text"},"role":"user","conversation_id":"test"}\'')
    print("\n🛑 Press Ctrl+C to stop\n")
    
    # Start the agent (blocking call)
    agent.start(register=False)  # Don't register for this example


if __name__ == "__main__":
    main()

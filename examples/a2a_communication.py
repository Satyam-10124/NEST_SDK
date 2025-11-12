#!/usr/bin/env python3
"""
NEST SDK A2A Communication Example

This script demonstrates agent-to-agent communication.

Usage:
    python examples/a2a_communication.py
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nest import Agent


async def main():
    print("🪺 NEST SDK - A2A Communication Example\n")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("   Agents will use echo mode\n")
    
    # Create two specialized agents
    print("Creating agents...")
    
    # Agent 1: Research specialist
    researcher = Agent.from_llm(
        id="researcher",
        name="Research Specialist",
        model="claude-3-haiku-20240307",
        system_prompt="You are a research specialist. Provide factual, well-researched information.",
        capabilities=["research", "fact-checking", "analysis"],
        port=6010
    )
    
    # Agent 2: Writer specialist
    writer = Agent.from_llm(
        id="writer",
        name="Content Writer",
        model="claude-3-haiku-20240307",
        system_prompt="You are a content writer. Write engaging, clear content.",
        capabilities=["writing", "editing", "content creation"],
        port=6011
    )
    
    print(f"✅ {researcher.config.name} ready on port {researcher.config.port}")
    print(f"✅ {writer.config.name} ready on port {writer.config.port}")
    
    # Start both agents in background
    print("\n🚀 Starting agents...")
    task1 = asyncio.create_task(researcher.start_async(register=False))
    task2 = asyncio.create_task(writer.start_async(register=False))
    
    # Give them time to start
    await asyncio.sleep(2)
    
    # Demonstrate A2A communication
    print("\n💬 Testing A2A Communication...\n")
    
    try:
        # Researcher sends message to Writer
        response = await researcher.send_message(
            "@writer Based on my research, sustainable fashion is growing 20% annually. Can you write a brief article?",
            to="writer"
        )
        
        print(f"📨 Researcher → Writer:")
        print(f"   {response}\n")
        
    except Exception as e:
        print(f"❌ Communication error: {e}")
    
    # Keep running
    print("🔄 Agents running... Press Ctrl+C to stop\n")
    
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped")

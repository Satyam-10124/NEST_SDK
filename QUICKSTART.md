# 🚀 NEST SDK Quickstart Guide

Get your first AI agent running in 5 minutes!

---

## Step 1: Install NEST SDK (30 seconds)

```bash
pip install nest-sdk
```

Or install in development mode if you're working with the source:

```bash
cd NEST_SDK
pip install -e .
```

---

## Step 2: Set Up Your API Key (1 minute)

### Get Your Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Generate an API key

### Set the Environment Variable

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

**Windows:**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

**Or create a `.env` file:**
```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

---

## Step 3: Create Your First Agent (1 minute)

### Option A: Using Python (5 lines!)

Create `my_agent.py`:

```python
from nest import Agent

agent = Agent(
    id="my-first-agent",
    name="My Assistant",
    prompt="You are a helpful AI assistant. Be friendly and concise."
)

agent.start()
```

Run it:
```bash
python my_agent.py
```

### Option B: Using CLI (Interactive)

```bash
# Initialize project
nest init my-agent-project
cd my-agent-project

# Copy and configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Create agent from template
nest create agent --template customer-support
```

---

## Step 4: Test Your Agent (2 minutes)

Your agent is now running on `http://localhost:6000/a2a`

### Test with curl

```bash
curl -X POST http://localhost:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "text": "Hello! Who are you?",
      "type": "text"
    },
    "role": "user",
    "conversation_id": "test123"
  }'
```

### Test with Python

```python
import requests

response = requests.post(
    "http://localhost:6000/a2a",
    json={
        "content": {"text": "What can you help me with?", "type": "text"},
        "role": "user",
        "conversation_id": "test"
    }
)

print(response.json())
```

---

## 🎉 Congratulations!

You've created your first NEST agent! Here's what you can do next:

### 1. Try Different Templates

```bash
# List available templates
nest templates

# Create from template
python -c "
from nest import Agent
agent = Agent.from_template('data-analyst')
agent.start()
"
```

### 2. Create Multiple Agents

```python
from nest import Agent

# Agent 1
agent1 = Agent(
    id="researcher",
    prompt="You are a research specialist",
    port=6001
)

# Agent 2
agent2 = Agent(
    id="writer",
    prompt="You are a content writer",
    port=6002
)

# Start both
# agent1.start() # In separate terminal
# agent2.start() # In separate terminal
```

### 3. Enable A2A Communication

```python
import asyncio
from nest import Agent

async def main():
    # Create agents
    researcher = Agent(id="researcher", prompt="...", port=6010)
    writer = Agent(id="writer", prompt="...", port=6011)
    
    # Start them
    await researcher.start_async()
    await writer.start_async()
    
    # Send A2A message
    response = await researcher.send_message(
        "@writer Can you write about AI?",
        to="writer"
    )
    print(response)

asyncio.run(main())
```

### 4. Use CLI Commands

```bash
# List all agents
nest list

# Get agent info
nest info my-first-agent

# Deploy to cloud (requires AWS credentials)
nest deploy --provider aws
```

---

## 📚 Next Steps

### Learn More

- **[Full Documentation](README_SDK.md)** - Complete API reference
- **[Use Cases](USE_CASES.md)** - Real-world examples
- **[Examples](examples/)** - Sample code
- **[Templates](nest/templates/data/)** - Pre-built agents

### Build Something Cool

Ideas to get started:
- **Customer Support Bot** - Handle customer inquiries
- **Code Review Assistant** - Review pull requests
- **Data Analysis Agent** - Analyze datasets
- **Content Creation Pipeline** - Research → Write → Edit → Publish
- **Personal Assistant** - Manage tasks and schedules

### Join the Community

- Star us on [GitHub](https://github.com/projnanda/NEST)
- Report issues or request features
- Contribute new templates
- Share your agents!

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'nest'"

```bash
# Make sure you installed the package
pip install nest-sdk

# Or if working with source
pip install -e .
```

### "ANTHROPIC_API_KEY not found"

```bash
# Set the environment variable
export ANTHROPIC_API_KEY=your-key-here

# Or add to .env file
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### "Port already in use"

```python
# Change the port
agent = Agent(id="my-agent", prompt="...", port=6001)
```

### Agent not responding

```bash
# Check if it's running
curl http://localhost:6000/health

# Check logs
# Look at terminal output where agent is running
```

---

## 💡 Quick Tips

1. **Start Simple** - Begin with a single agent, add complexity later
2. **Use Templates** - Save time with pre-built configurations
3. **Test Locally** - Always test locally before deploying
4. **Monitor Performance** - Use health checks and metrics
5. **Read Examples** - Check `examples/` directory for patterns

---

## 🎯 Common Patterns

### Pattern 1: Simple Q&A Agent

```python
from nest import Agent

agent = Agent(
    id="qa-agent",
    prompt="Answer questions concisely and accurately."
)
agent.start()
```

### Pattern 2: Domain Expert

```python
agent = Agent.from_llm(
    id="python-expert",
    name="Python Expert",
    system_prompt="You are a Python programming expert...",
    capabilities=["Python", "debugging", "best practices"],
    model="claude-3-5-sonnet-20241022"
)
agent.start()
```

### Pattern 3: Multi-Agent System

```python
# Create specialized agents that work together
coordinator = Agent(id="coordinator", prompt="Route tasks...", port=6000)
specialist1 = Agent(id="specialist1", prompt="Handle X...", port=6001)
specialist2 = Agent(id="specialist2", prompt="Handle Y...", port=6002)

# They communicate via A2A!
```

---

**You're all set! Start building amazing AI agents!** 🚀

Need help? Check [docs](README_SDK.md) or [open an issue](https://github.com/projnanda/NEST/issues).

# 🪺 NEST SDK v3.0 - Build AI Agents in 5 Lines of Code

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.0.0-brightgreen.svg)](https://github.com/projnanda/NEST)

**Build, test, and deploy AI agents with agent-to-agent communication in minutes.**

NEST SDK is a production-ready Python framework for creating specialized AI agents powered by Claude LLM with seamless agent-to-agent (A2A) communication capabilities.

---

## ✨ Features

- 🚀 **Simple API** - Create agents in 5 lines of code
- 💬 **A2A Communication** - Agents discover and talk to each other
- 🛠️ **Interactive CLI** - Beautiful command-line tools
- 📦 **Templates** - Pre-built agents for common use cases
- ☁️ **Cloud Deploy** - One-command AWS deployment
- 🧩 **MCP Support** - Integrate with Model Context Protocol
- 📊 **Monitoring** - Built-in telemetry and health checks
- 🔒 **Production Ready** - Type hints, validation, error handling

---

## 🚀 Quick Start

### Installation

```bash
pip install nest-sdk
```

### Your First Agent (5 lines!)

```python
from nest import Agent

agent = Agent(
    id="fashion-expert",
    name="Fashion Consultant",
    prompt="You are a sustainable fashion expert..."
)
agent.start()
```

That's it! Your agent is now running on `http://localhost:6000/a2a`

### Test It

```bash
curl -X POST http://localhost:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"What's trending in sustainable fashion?","type":"text"},"role":"user","conversation_id":"test"}'
```

---

## 📚 Usage Examples

### From Template

Create agents from pre-built templates:

```python
from nest import Agent

# Customer support agent
agent = Agent.from_template(
    "customer-support",
    company_name="ACME Corp",
    port=6000
)
agent.start()
```

Available templates:
- `customer-support` - Customer service specialist
- `data-analyst` - Data analysis expert
- `code-reviewer` - Code review assistant

### With LLM Configuration

```python
agent = Agent.from_llm(
    id="data-scientist",
    name="Data Science Expert",
    model="claude-3-5-sonnet-20241022",
    system_prompt="You are an expert data scientist...",
    capabilities=["Python", "Statistics", "ML"],
    temperature=0.7
)
agent.start()
```

### Agent-to-Agent Communication

```python
from nest import Agent, NestClient

# Create two specialized agents
researcher = Agent(id="researcher", prompt="...", port=6010)
writer = Agent(id="writer", prompt="...", port=6011)

# Start them
await researcher.start_async()
await writer.start_async()

# Send A2A message
response = await researcher.send_message(
    "@writer Here's my research. Write an article?",
    to="writer"
)
print(response)
```

### From Configuration File

```yaml
# agent-config.yaml
id: fashion-expert
name: Fashion Consultant
model: claude-3-haiku-20240307
port: 6000
prompt: |
  You are a sustainable fashion expert...
capabilities:
  - Fashion advice
  - Sustainability
```

```python
agent = Agent.from_config("agent-config.yaml")
agent.start()
```

---

## 🛠️ CLI Commands

### Initialize Project

```bash
nest init my-agent-project
cd my-agent-project
```

### Create Agent

```bash
# Interactive wizard
nest create agent

# From template
nest create agent --template customer-support
```

### List Templates

```bash
nest templates
```

### List Agents

```bash
nest list
nest list --status active
```

### Agent Info

```bash
nest info fashion-expert
```

### Development Server

```bash
# Run locally
nest dev

# With web UI
nest dev --ui
```

### Deploy

```bash
# Interactive deployment
nest deploy

# Quick deploy
nest deploy --agent fashion-expert --provider aws
```

---

## 📖 Documentation

### Core Classes

#### Agent

```python
Agent(
    id: str,                          # Required: unique identifier
    name: Optional[str] = None,       # Display name
    prompt: Optional[str] = None,     # System prompt
    model: str = "claude-3-haiku-20240307",
    port: int = 6000,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    capabilities: Optional[List[str]] = None,
    registry_url: Optional[str] = None,
    **kwargs
)
```

**Methods:**
- `start(register=True)` - Start agent server
- `stop()` - Stop agent
- `send_message(message, to=None)` - Send message (A2A if 'to' specified)
- `update_config(**updates)` - Update configuration

**Class Methods:**
- `Agent.from_config(path)` - Create from YAML/JSON
- `Agent.from_template(name, **overrides)` - Create from template
- `Agent.from_llm(id, name, model, ...)` - Create with LLM config

#### NestClient

```python
NestClient(
    registry_url: str = "http://registry.nanda.ai",
    timeout: int = 30
)
```

**Methods:**
- `list_agents(status=None)` - List all agents
- `get_agent(agent_id)` - Get agent details
- `send_message(from_agent, to_agent, message)` - Send A2A message
- `deploy(agent, provider, region, ...)` - Deploy to cloud
- `health_check(agent_id)` - Check agent health

### Configuration

Create `nest.config.yaml`:

```yaml
project_name: my-nest-project
version: 1.0.0

registry_url: ${NEST_REGISTRY_URL}
mcp_registry_url: ${MCP_REGISTRY_URL}

default_model: claude-3-haiku-20240307
default_port: 6000
default_temperature: 0.7

agents:
  - id: agent-1
    name: Customer Support
    template: customer-support
    port: 6000
  
  - id: agent-2
    name: Data Analyst
    port: 6001
```

### Environment Variables

Create `.env`:

```bash
# Required
ANTHROPIC_API_KEY=your-api-key-here

# Optional
NEST_REGISTRY_URL=http://registry.nanda.ai
MCP_REGISTRY_URL=
SMITHERY_API_KEY=
PORT=6000
```

---

## 💡 Use Cases

### Customer Service

```python
# Multi-tier support system
greeter = Agent.from_template("customer-greeter", port=6000)
support = Agent.from_template("customer-support", port=6001)
supervisor = Agent.from_template("supervisor", port=6002)

# Start all
greeter.start()
support.start()
supervisor.start()
```

### Content Creation Pipeline

```python
researcher = Agent(id="researcher", prompt="Research topics...", port=6010)
writer = Agent(id="writer", prompt="Write articles...", port=6011)
editor = Agent(id="editor", prompt="Edit content...", port=6012)
seo = Agent(id="seo", prompt="Optimize for SEO...", port=6013)

# They can all communicate via A2A!
```

### Software Development Team

```python
code_reviewer = Agent.from_template("code-reviewer", port=6020)
doc_generator = Agent(id="docs", prompt="Generate docs...", port=6021)
test_generator = Agent(id="tests", prompt="Generate tests...", port=6022)
```

---

## 🧪 Testing

### Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=nest --cov-report=html
```

### Example Tests

```python
from nest import Agent

def test_agent_creation():
    agent = Agent(id="test", prompt="Test agent")
    assert agent.config.id == "test"
    assert not agent.is_running

async def test_agent_message():
    agent = Agent(id="test", prompt="Echo")
    response = await agent.send_message("Hello")
    assert response is not None
```

---

## 🚀 Deployment

### Local

```bash
nest deploy --provider local
```

### AWS

```bash
# Configure AWS credentials first
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# Deploy
nest deploy --agent my-agent --provider aws --region us-east-1
```

### Docker

```python
from nest.deployment import DockerDeployer

deployer = DockerDeployer()
deployment = deployer.deploy(
    agent=agent,
    image="nest-agent:latest",
    ports={6000: 6000}
)
```

---

## 🎯 Examples

Check the `examples/` directory:

- **`quick_start.py`** - Simplest possible agent (5 lines)
- **`from_template.py`** - Using templates
- **`a2a_communication.py`** - Agent-to-agent messaging
- **`multi_agent_system.py`** - Multiple agents working together

Run them:

```bash
python examples/quick_start.py
python examples/from_template.py
python examples/a2a_communication.py
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`pytest tests/`)
5. **Commit** (`git commit -m 'Add amazing feature'`)
6. **Push** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Setup

```bash
# Clone
git clone https://github.com/projnanda/NEST
cd NEST

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black nest/
isort nest/

# Type checking
mypy nest/
```

---

## 📋 Requirements

- Python 3.8+
- Anthropic API key (for LLM-powered agents)
- AWS credentials (for deployment)

---

## 🔒 Security

- API keys stored in environment variables
- Validation on all inputs
- Rate limiting support
- Audit logging
- HIPAA-compliant deployment options

---

## 📊 Performance

- Agent creation: <100ms
- Message response: <2s (LLM-dependent)
- A2A communication: <3s
- Memory per agent: <200MB
- Supports 1000+ concurrent agents

---

## 🐛 Troubleshooting

### Agent won't start

```python
# Check if port is available
import socket
sock = socket.socket()
sock.bind(('0.0.0.0', 6000))  # Will raise error if port in use
```

### LLM not working

```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Test it
python -c "from anthropic import Anthropic; print(Anthropic().models.list())"
```

### A2A communication fails

```bash
# Check if both agents are registered
nest list --status active

# Test agent directly
curl http://localhost:6000/health
```

---

## 📞 Support

- **Documentation:** [GitHub Wiki](https://github.com/projnanda/NEST/wiki)
- **Issues:** [GitHub Issues](https://github.com/projnanda/NEST/issues)
- **Discussions:** [GitHub Discussions](https://github.com/projnanda/NEST/discussions)
- **Email:** support@nanda.ai

---

## 🎓 Learn More

- [API Reference](docs/api-reference.md)
- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Use Cases](USE_CASES.md)

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgments

- Built on [Project NANDA](https://github.com/projnanda)
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- Uses [python-a2a](https://pypi.org/project/python-a2a/)
- CLI built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)

---

## 📈 Roadmap

- ✅ Core SDK with simplified API
- ✅ Interactive CLI
- ✅ Agent templates
- 🚧 Visual agent builder (web UI)
- 🚧 Agent marketplace
- 🚧 Advanced monitoring dashboard
- 🚧 Multi-cloud deployment
- 🚧 IDE extensions

---

**Built with ❤️ by the NANDA Team**

[⭐ Star us on GitHub](https://github.com/projnanda/NEST) | [🐛 Report Bug](https://github.com/projnanda/NEST/issues) | [💡 Request Feature](https://github.com/projnanda/NEST/issues)

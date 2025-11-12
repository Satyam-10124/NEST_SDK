# 🔧 NANDA NEST SDK - Technical Specifications

## API Design Specifications

### 1. Agent Class API

```python
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass

class Agent:
    """Main Agent class - Simple and Pythonic"""
    
    # Constructor
    def __init__(
        self,
        id: str,                          # Required: unique identifier
        name: Optional[str] = None,       # Display name
        prompt: Optional[str] = None,     # System prompt
        model: str = "claude-3-haiku-20240307",
        port: int = 6000,
        registry_url: Optional[str] = None,
        mcp_registry_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        capabilities: Optional[List[str]] = None,
        **kwargs
    )
    
    # Lifecycle methods
    def start(self, register: bool = True) -> None
    async def start_async(self, register: bool = True) -> None
    def stop(self) -> None
    
    # Communication
    async def send_message(self, message: str, to: Optional[str] = None) -> str
    
    # Configuration
    def update_config(self, **updates) -> None
    
    # Factory methods
    @classmethod
    def from_config(cls, config_path: str) -> "Agent"
    
    @classmethod
    def from_template(cls, template_name: str, **overrides) -> "Agent"
    
    @classmethod
    def from_llm(
        cls,
        id: str,
        name: str,
        model: str,
        system_prompt: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        **kwargs
    ) -> "Agent"
```

### 2. NestClient API

```python
class NestClient:
    """Client for managing NANDA agents"""
    
    def __init__(self, registry_url: str = "http://registry.nanda.ai")
    
    # Agent discovery
    def list_agents(self, status: Optional[str] = None) -> List[AgentInfo]
    def get_agent(self, agent_id: str) -> AgentInfo
    def search_agents(self, query: str) -> List[AgentInfo]
    
    # Communication
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> str
    
    async def send_message_async(...) -> str
    
    # Deployment
    def deploy(
        self,
        agent: Agent,
        provider: str = "aws",
        region: str = "us-east-1",
        instance_type: str = "t3.micro",
        **kwargs
    ) -> DeploymentInfo
    
    # Monitoring
    def health_check(self, agent_id: str) -> Dict[str, Any]
    def get_metrics(self, agent_id: str) -> MetricsInfo
    def get_logs(self, agent_id: str, lines: int = 100) -> List[str]
```

### 3. Configuration API

```python
class NestConfig(BaseModel):
    """Project configuration using Pydantic"""
    
    project_name: str
    version: str = "1.0.0"
    
    # Registry
    registry_url: Optional[str] = None
    mcp_registry_url: Optional[str] = None
    
    # Defaults
    default_model: str = "claude-3-haiku-20240307"
    default_port: int = 6000
    default_temperature: float = 0.7
    
    # Deployment
    deployment: Dict[str, Any] = Field(default_factory=dict)
    
    # Agents
    agents: List[Dict[str, Any]] = Field(default_factory=list)
    
    @classmethod
    def load(cls, config_path: str = "nest.config.yaml") -> "NestConfig"
    
    def save(self, config_path: str = "nest.config.yaml") -> None
    
    @classmethod
    def create_default(cls, project_name: str) -> "NestConfig"
```

---

## CLI Command Specifications

### nest init

```bash
nest init [PROJECT_NAME] [OPTIONS]

Arguments:
  PROJECT_NAME          Project name (interactive if not provided)

Options:
  --template TEXT       Template to use (basic, multi-agent, mcp-integration, custom)
  --path TEXT          Project directory (default: .)
  --no-interactive     Skip interactive prompts

Examples:
  nest init                           # Interactive mode
  nest init my-project                # Quick init
  nest init my-project --template multi-agent
```

### nest create

```bash
nest create agent [OPTIONS]

Options:
  --id TEXT              Agent ID
  --name TEXT            Agent name
  --template TEXT        Use template
  --model TEXT           LLM model to use
  --port INTEGER         Port number
  --interactive          Interactive wizard (default)

Examples:
  nest create agent                           # Interactive
  nest create agent --id fashion-expert --template customer-support
```

### nest dev

```bash
nest dev [OPTIONS]

Options:
  --agent TEXT           Run specific agent
  --all                  Run all agents
  --port INTEGER         Port override
  --ui                   Start web UI
  --hot-reload           Enable hot reload (default)
  --no-register          Don't register with registry

Examples:
  nest dev                    # Run default agent
  nest dev --all             # Run all agents
  nest dev --ui              # With web interface
```

### nest test

```bash
nest test [SUBCOMMAND] [OPTIONS]

Subcommands:
  agent            Test single agent
  a2a              Test agent-to-agent communication
  mcp              Test MCP integration
  scenario         Test from scenario file
  all              Run all tests

Options for 'agent':
  --agent TEXT          Agent ID
  --message TEXT        Test message
  --interactive         Interactive chat mode

Options for 'a2a':
  --from TEXT           Source agent
  --to TEXT             Target agent
  --message TEXT        Message content

Options for 'scenario':
  --file TEXT           Scenario YAML/JSON file

Examples:
  nest test agent fashion-expert --message "Hello"
  nest test a2a --from user --to fashion-expert --message "Test"
  nest test scenario ./tests/flow.yaml
  nest test all
```

### nest deploy

```bash
nest deploy [OPTIONS]

Options:
  --agent TEXT          Agent to deploy (default: all)
  --provider TEXT       Cloud provider (aws, gcp, azure, local)
  --region TEXT         Deployment region
  --instance-type TEXT  Instance type
  --config TEXT         Deployment config file
  --dry-run            Preview deployment
  --no-interactive     Skip confirmations

Examples:
  nest deploy                                    # Interactive
  nest deploy --agent fashion-expert --provider aws
  nest deploy --config deploy.yaml
```

### nest monitor

```bash
nest monitor [OPTIONS]

Options:
  --agent TEXT          Monitor specific agent
  --metrics             Show metrics
  --logs                Show logs
  --export TEXT         Export to file
  --format TEXT         Output format (json, csv, table)
  --refresh INTEGER     Refresh interval (seconds)

Examples:
  nest monitor                        # TUI dashboard
  nest monitor --agent fashion-expert
  nest monitor --metrics --export metrics.json
```

---

## Template Specifications

### Template Structure

```yaml
# templates/customer-support.yaml

metadata:
  name: "Customer Support Agent"
  description: "Friendly customer support specialist"
  version: "1.0.0"
  author: "NEST Team"
  tags: [customer-service, support, communication]

agent:
  id: "customer-support-{random}"
  name: "Support Agent"
  model: "claude-3-haiku-20240307"
  port: 6000
  
  system_prompt: |
    You are a friendly and professional customer support agent.
    
    Your responsibilities:
    - Answer customer inquiries politely and accurately
    - Provide product information
    - Troubleshoot common issues
    - Escalate complex problems when needed
    
    Always maintain a helpful, empathetic tone.
  
  capabilities:
    - Customer inquiries
    - Product information
    - Troubleshooting
    - Escalation handling
  
  tools:
    - type: mcp
      server: "crm-connector"
      description: "Access CRM data"
    
    - type: function
      name: "escalate_ticket"
      description: "Escalate to human agent"
      parameters:
        ticket_id: string
        reason: string
        priority: enum[low, medium, high, critical]

config:
  temperature: 0.7
  max_tokens: 1000
  timeout: 30
  
  a2a:
    can_communicate_with:
      - supervisor-agent
      - knowledge-base-agent
    
  deployment:
    min_instances: 1
    max_instances: 5
    auto_scale: true

variables:
  company_name: "ACME Corp"
  support_hours: "24/7"
  languages: ["English", "Spanish"]

files:
  - src: "prompts/customer-support.txt"
    dest: "prompts/"
  - src: "tests/customer-support-tests.py"
    dest: "tests/"
```

### Available Templates

1. **basic/general-assistant** - General purpose helper
2. **basic/simple-chatbot** - Basic conversational agent
3. **industry/customer-support** - Customer service specialist
4. **industry/data-analyst** - Data analysis expert
5. **industry/content-writer** - Content creation specialist
6. **industry/code-reviewer** - Code review assistant
7. **industry/research-assistant** - Academic research helper
8. **advanced/multi-agent-coordinator** - Orchestrator agent
9. **advanced/mcp-integration** - Pre-configured MCP tools
10. **advanced/rag-agent** - RAG implementation

---

## Configuration File Formats

### nest.config.yaml

```yaml
project_name: my-nest-project
version: 1.0.0

# Registry settings
registry_url: ${NEST_REGISTRY_URL}
mcp_registry_url: ${MCP_REGISTRY_URL}

# Default settings
default_model: claude-3-haiku-20240307
default_port: 6000
default_temperature: 0.7

# Deployment settings
deployment:
  provider: aws
  region: us-east-1
  instance_type: t3.micro
  auto_scale: true
  min_instances: 1
  max_instances: 5

# Agent definitions
agents:
  - id: fashion-expert
    name: Fashion Consultant
    template: customer-support
    port: 6000
    config:
      company_name: Fashion Co
  
  - id: data-analyst
    name: Data Analyst
    model: claude-3-5-sonnet-20241022
    port: 6001

# Monitoring
monitoring:
  enabled: true
  metrics_port: 9090
  log_level: INFO

# Security
security:
  require_api_key: true
  allowed_origins: ["*"]
  rate_limit: 100
```

### .env.example

```bash
# Anthropic API
ANTHROPIC_API_KEY=your-api-key-here

# NEST Registry
NEST_REGISTRY_URL=http://registry.nanda.ai
MCP_REGISTRY_URL=https://mcp-registry.nanda.ai

# Smithery (Optional)
SMITHERY_API_KEY=your-smithery-key

# AWS Credentials (for deployment)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# Agent Settings
AGENT_ID=my-agent
AGENT_NAME=My Agent
PORT=6000

# Monitoring
ENABLE_TELEMETRY=true
LOG_LEVEL=INFO
```

---

## Deployment Specifications

### AWS Deployment

```python
from nest.deployment import AWSDeployer

deployer = AWSDeployer(
    region="us-east-1",
    instance_type="t3.micro",
    security_group="nest-agents",
    key_name="nest-key",
    subnet_id="subnet-xxx"
)

deployment = deployer.deploy(
    agent=agent,
    ami="ami-xxxxx",  # Ubuntu 22.04
    user_data_script="install.sh"
)

print(f"Instance ID: {deployment.instance_id}")
print(f"Public URL: {deployment.public_url}")
```

### Docker Deployment

```python
from nest.deployment import DockerDeployer

deployer = DockerDeployer()

deployment = deployer.deploy(
    agent=agent,
    image="nest-agent:latest",
    container_name=f"nest-{agent.id}",
    ports={agent.port: agent.port},
    environment={
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "AGENT_ID": agent.id
    }
)
```

### Local Deployment

```python
from nest.deployment import LocalDeployer

deployer = LocalDeployer()

deployment = deployer.deploy(
    agent=agent,
    process_manager="supervisor",  # or systemd
    log_dir="./logs",
    pid_dir="./pids"
)
```

---

## Testing Framework

### Unit Tests Structure

```python
# tests/unit/test_agent.py

import pytest
from nest import Agent

def test_agent_creation():
    agent = Agent(id="test-agent", prompt="Test prompt")
    assert agent.config.id == "test-agent"

def test_agent_from_template():
    agent = Agent.from_template("customer-support")
    assert agent.config.name is not None

async def test_agent_message():
    agent = Agent(id="test", prompt="Echo: ")
    response = await agent.send_message("Hello")
    assert "Hello" in response
```

### Integration Tests

```python
# tests/integration/test_a2a.py

import pytest
from nest import Agent, NestClient

@pytest.fixture
async def two_agents():
    agent1 = Agent(id="agent-1", port=6001)
    agent2 = Agent(id="agent-2", port=6002)
    
    await agent1.start_async()
    await agent2.start_async()
    
    yield agent1, agent2
    
    agent1.stop()
    agent2.stop()

async def test_a2a_communication(two_agents):
    agent1, agent2 = two_agents
    
    client = NestClient()
    response = await client.send_message_async(
        from_agent="agent-1",
        to_agent="agent-2",
        message="Test message"
    )
    
    assert response is not None
```

### E2E Tests

```python
# tests/e2e/test_full_lifecycle.py

async def test_full_lifecycle():
    # Create agent
    agent = Agent.from_template("customer-support")
    
    # Start
    await agent.start_async(register=True)
    
    # Test
    response = await agent.send_message("Hello")
    assert response
    
    # Deploy (to local)
    from nest.deployment import LocalDeployer
    deployer = LocalDeployer()
    deployment = deployer.deploy(agent)
    
    # Verify deployment
    assert deployment.status == "running"
    
    # Cleanup
    deployer.undeploy(deployment.id)
    agent.stop()
```

---

## Performance Specifications

### Target Metrics

**Latency:**
- Agent creation: <100ms
- Message response: <2s (depends on LLM)
- A2A communication: <3s
- CLI command execution: <500ms

**Throughput:**
- Messages/second: >100 (single agent)
- Concurrent agents: >1000 (per machine)

**Resource Usage:**
- Memory per agent: <200MB
- CPU per agent: <10% (idle)
- Disk space: <50MB (per agent)

**Scalability:**
- Agents per project: Unlimited
- A2A connections: >10,000
- Registry size: >100,000 agents

---

## Security Specifications

### API Key Management

```python
# Secure API key handling
from nest.security import SecureConfig

config = SecureConfig()
config.set("anthropic_api_key", "sk-ant-...")  # Encrypted
api_key = config.get("anthropic_api_key")      # Decrypted
```

### Agent Authentication

```python
# Require API key for agent access
agent = Agent(
    id="secure-agent",
    prompt="...",
    require_auth=True,
    api_key="nest-key-xxx"
)

# Client must provide key
client = NestClient(api_key="nest-key-xxx")
```

### Rate Limiting

```python
# Configure rate limits
agent = Agent(
    id="rate-limited",
    rate_limit={
        "requests_per_minute": 60,
        "requests_per_hour": 1000
    }
)
```

---

## Error Handling Specifications

### Custom Exceptions

```python
from nest.exceptions import (
    NestError,              # Base exception
    AgentNotFoundError,     # Agent doesn't exist
    RegistryError,          # Registry communication failed
    DeploymentError,        # Deployment failed
    ConfigError,            # Configuration invalid
    AuthenticationError,    # Auth failed
    RateLimitError         # Rate limit exceeded
)
```

### Error Handling Pattern

```python
try:
    agent = Agent.from_template("invalid-template")
except nest.ConfigError as e:
    console.print(f"[red]Configuration error:[/red] {e}")
    console.print("Available templates:", nest.list_templates())
except nest.NestError as e:
    console.print(f"[red]Error:[/red] {e}")
```

---

## Monitoring & Telemetry

### Metrics Collection

```python
from nest.telemetry import TelemetrySystem

telemetry = TelemetrySystem(agent_id="fashion-expert")

# Automatic metrics
- requests_total
- requests_per_second
- response_time_avg
- response_time_p95
- response_time_p99
- errors_total
- memory_usage_mb
- cpu_usage_percent

# Custom metrics
telemetry.record_metric("custom_metric", value)
```

### Health Checks

```python
# Built-in health endpoint
GET /health

Response:
{
  "status": "healthy",
  "agent_id": "fashion-expert",
  "uptime": 3600,
  "requests_total": 150,
  "errors_total": 2,
  "memory_mb": 180,
  "cpu_percent": 8.5
}
```

---

## Migration Guide (NEST v2 → v3)

### Breaking Changes

1. **Import path changed:**
   ```python
   # Old
   from nanda_core.core.adapter import NANDA
   
   # New
   from nest import Agent
   ```

2. **Agent creation simplified:**
   ```python
   # Old
   nanda = NANDA(
       agent_id="id",
       agent_logic=my_logic,
       port=6000
   )
   nanda.start()
   
   # New
   agent = Agent(
       id="id",
       prompt="..."
   )
   agent.start()
   ```

3. **CLI commands changed:**
   ```bash
   # Old
   bash scripts/aws-single-agent-deployment.sh ...
   
   # New
   nest deploy --provider aws
   ```

### Migration Script

```python
# migrate_v2_to_v3.py

from nest.migration import migrate_project

migrate_project(
    source_dir="./old-nest-project",
    target_dir="./new-nest-project",
    backup=True
)
```

---

## Development Workflow

### Local Development

```bash
# Clone repo
git clone https://github.com/yourorg/nest-sdk
cd nest-sdk

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black nest/
flake8 nest/

# Type checking
mypy nest/

# Build package
python -m build

# Install locally
pip install -e .
```

### Contributing Workflow

```bash
# Fork & clone
git clone https://github.com/yourname/nest-sdk
cd nest-sdk

# Create branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Test
pytest tests/
black nest/
mypy nest/

# Commit
git add .
git commit -m "feat: add my feature"

# Push
git push origin feature/my-feature

# Create PR on GitHub
```

---

## Release Process

### Version Numbering

- **Major (X.0.0):** Breaking changes
- **Minor (0.X.0):** New features, backward compatible
- **Patch (0.0.X):** Bug fixes

### Release Checklist

- [ ] All tests passing
- [ ] Version bumped in `__init__.py`
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Examples tested
- [ ] Security audit passed
- [ ] Performance benchmarks run
- [ ] Git tag created
- [ ] PyPI package published
- [ ] GitHub release created
- [ ] Announcement posted

### PyPI Publishing

```bash
# Build
python -m build

# Check
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ nest-sdk

# Upload to PyPI
twine upload dist/*
```

---

**Document Version:** 1.0  
**Last Updated:** November 12, 2025  
**Maintained by:** NEST SDK Team

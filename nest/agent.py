"""
Simplified Agent class for NEST SDK

This module provides a clean, Pythonic API for creating and managing AI agents.
"""

import os
import sys
import asyncio
import uuid
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nest.exceptions import ConfigError, ValidationError

# Try to import optional dependencies
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from nanda_core.core.adapter import NANDA
    NANDA_AVAILABLE = True
except ImportError:
    NANDA_AVAILABLE = False


@dataclass
class AgentConfig:
    """Configuration for a NEST agent"""
    
    id: str
    name: str
    model: str = "claude-3-haiku-20240307"
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    port: int = 6000
    host: str = "0.0.0.0"
    registry_url: Optional[str] = None
    mcp_registry_url: Optional[str] = None
    public_url: Optional[str] = None
    smithery_api_key: Optional[str] = None
    enable_telemetry: bool = True
    require_auth: bool = False
    api_key: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.id:
            raise ConfigError("Agent ID is required")
        
        if not self.name:
            self.name = self.id
        
        if self.temperature < 0 or self.temperature > 1:
            raise ConfigError("Temperature must be between 0 and 1")
        
        if self.max_tokens < 1:
            raise ConfigError("max_tokens must be positive")
        
        if self.port < 1 or self.port > 65535:
            raise ConfigError("Port must be between 1 and 65535")


class Agent:
    """
    Simplified NEST Agent with developer-friendly API
    
    This class provides a clean interface for creating and managing AI agents
    with built-in support for LLMs, A2A communication, and production deployment.
    
    Examples:
        Simple agent:
        >>> agent = Agent(
        ...     id="helpful-agent",
        ...     prompt="You are a helpful assistant"
        ... )
        >>> agent.start()
        
        From template:
        >>> agent = Agent.from_template("customer-support")
        >>> agent.start()
        
        With LLM configuration:
        >>> agent = Agent.from_llm(
        ...     id="data-scientist",
        ...     name="Data Science Expert",
        ...     model="claude-3-5-sonnet-20241022",
        ...     capabilities=["Python", "Statistics", "ML"]
        ... )
        >>> agent.start()
    """
    
    def __init__(
        self,
        id: str,
        name: Optional[str] = None,
        prompt: Optional[str] = None,
        model: str = "claude-3-haiku-20240307",
        port: int = 6000,
        host: str = "0.0.0.0",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        capabilities: Optional[List[str]] = None,
        registry_url: Optional[str] = None,
        mcp_registry_url: Optional[str] = None,
        public_url: Optional[str] = None,
        smithery_api_key: Optional[str] = None,
        enable_telemetry: bool = True,
        **kwargs
    ):
        """
        Create a new NEST agent
        
        Args:
            id: Unique agent identifier
            name: Display name (defaults to id if not provided)
            prompt: System prompt for the agent
            model: LLM model to use (default: claude-3-haiku-20240307)
            port: Port number for the agent server
            host: Host to bind to (default: 0.0.0.0)
            temperature: LLM temperature (0-1)
            max_tokens: Maximum tokens in response
            capabilities: List of agent capabilities
            registry_url: NANDA registry URL
            mcp_registry_url: MCP registry URL
            public_url: Public URL for agent registration
            smithery_api_key: Smithery API key for MCP
            enable_telemetry: Enable telemetry logging
            **kwargs: Additional configuration options
        
        Raises:
            ConfigError: If configuration is invalid
        """
        # Create configuration
        self.config = AgentConfig(
            id=id,
            name=name or id,
            system_prompt=prompt,
            model=model,
            port=port,
            host=host,
            temperature=temperature,
            max_tokens=max_tokens,
            capabilities=capabilities or [],
            registry_url=registry_url or os.getenv("NEST_REGISTRY_URL"),
            mcp_registry_url=mcp_registry_url or os.getenv("MCP_REGISTRY_URL"),
            public_url=public_url or os.getenv("PUBLIC_URL"),
            smithery_api_key=smithery_api_key or os.getenv("SMITHERY_API_KEY"),
            enable_telemetry=enable_telemetry,
            **kwargs
        )
        
        # Internal state
        self._llm_client = None
        self._adapter = None
        self._running = False
        
        # Initialize the agent
        self._initialize()
        
        print(f"✅ Agent '{self.config.name}' created (id: {self.config.id})")
    
    def _initialize(self):
        """Initialize the agent internals"""
        # Setup LLM client if API key available
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and ANTHROPIC_AVAILABLE:
            try:
                self._llm_client = Anthropic(api_key=api_key)
                print(f"🧠 LLM client initialized ({self.config.model})")
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize LLM client: {e}")
        
        # Setup NANDA adapter
        if NANDA_AVAILABLE:
            try:
                self._adapter = NANDA(
                    agent_id=self.config.id,
                    agent_logic=self._create_logic(),
                    port=self.config.port,
                    host=self.config.host,
                    registry_url=self.config.registry_url,
                    mcp_registry_url=self.config.mcp_registry_url,
                    public_url=self.config.public_url,
                    smithery_api_key=self.config.smithery_api_key,
                    enable_telemetry=self.config.enable_telemetry
                )
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize NANDA adapter: {e}")
        else:
            print("⚠️  Warning: NANDA core not available. Install with: pip install -e .")
    
    def _create_logic(self) -> Callable[[str, str], str]:
        """
        Create the agent logic function
        
        Returns:
            Function that takes (message, conversation_id) and returns response
        """
        def logic(message: str, conversation_id: str) -> str:
            """Agent logic function"""
            
            # Use LLM if available
            if self._llm_client:
                try:
                    response = self._llm_client.messages.create(
                        model=self.config.model,
                        max_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        system=self.config.system_prompt or f"You are {self.config.name}",
                        messages=[{"role": "user", "content": message}]
                    )
                    return response.content[0].text
                except Exception as e:
                    print(f"❌ LLM Error: {e}")
                    return f"Sorry, I encountered an error: {str(e)}"
            
            # Fallback to echo
            return f"Echo from {self.config.name}: {message}"
        
        return logic
    
    def start(self, register: bool = True) -> None:
        """
        Start the agent server
        
        Args:
            register: Whether to register with NANDA registry
        
        Raises:
            RuntimeError: If agent is already running or adapter not available
        """
        if self._running:
            raise RuntimeError(f"Agent '{self.config.id}' is already running")
        
        if not self._adapter:
            raise RuntimeError("NANDA adapter not available. Cannot start agent.")
        
        print(f"🚀 Starting agent '{self.config.name}' on {self.config.host}:{self.config.port}")
        
        if register and self.config.registry_url:
            print(f"📝 Will register with: {self.config.registry_url}")
        
        self._running = True
        
        try:
            # Start the A2A server (blocking call)
            self._adapter.start(register=register)
        except KeyboardInterrupt:
            print(f"\n⏸️  Interrupted. Stopping agent '{self.config.name}'...")
            self.stop()
        except Exception as e:
            print(f"❌ Error starting agent: {e}")
            self._running = False
            raise
    
    async def start_async(self, register: bool = True) -> None:
        """
        Start the agent server asynchronously
        
        Args:
            register: Whether to register with NANDA registry
        """
        await asyncio.to_thread(self.start, register)
    
    def stop(self) -> None:
        """Gracefully stop the agent"""
        if self._adapter:
            self._adapter.stop()
        
        self._running = False
        print(f"🛑 Agent '{self.config.name}' stopped")
    
    async def send_message(
        self,
        message: str,
        to: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Send a message (A2A if 'to' is specified)
        
        Args:
            message: Message content
            to: Target agent ID (for A2A communication)
            conversation_id: Optional conversation ID
        
        Returns:
            Response from agent
        
        Example:
            >>> response = await agent.send_message("Hello")
            >>> response = await agent.send_message("Help me", to="expert-agent")
        """
        if to:
            # A2A communication
            from nest.client import NestClient
            client = NestClient(self.config.registry_url)
            return await client.send_message_async(
                from_agent=self.config.id,
                to_agent=to,
                message=message,
                conversation_id=conversation_id
            )
        else:
            # Direct message to this agent
            logic = self._create_logic()
            return await asyncio.to_thread(
                logic,
                message,
                conversation_id or str(uuid.uuid4())
            )
    
    def update_config(self, **updates) -> None:
        """
        Update agent configuration
        
        Args:
            **updates: Configuration fields to update
        
        Example:
            >>> agent.update_config(temperature=0.9, max_tokens=2000)
        """
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                print(f"✏️  Updated {key} = {value}")
            else:
                print(f"⚠️  Warning: Unknown config field '{key}'")
    
    @classmethod
    def from_config(cls, config_path: str) -> "Agent":
        """
        Create agent from YAML/JSON configuration file
        
        Args:
            config_path: Path to configuration file
        
        Returns:
            Configured Agent instance
        
        Example:
            >>> agent = Agent.from_config("./config/my-agent.yaml")
        """
        import yaml
        import json
        from pathlib import Path
        
        path = Path(config_path)
        
        if not path.exists():
            raise ConfigError(f"Config file not found: {config_path}")
        
        # Load config
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                config = yaml.safe_load(f)
            elif path.suffix == '.json':
                config = json.load(f)
            else:
                raise ConfigError(f"Unsupported config format: {path.suffix}")
        
        print(f"📄 Loaded config from: {config_path}")
        return cls(**config)
    
    @classmethod
    def from_template(cls, template_name: str, **overrides) -> "Agent":
        """
        Create agent from template
        
        Args:
            template_name: Name of template (e.g., 'customer-support')
            **overrides: Override template values
        
        Returns:
            Agent instance from template
        
        Example:
            >>> agent = Agent.from_template(
            ...     "customer-support",
            ...     company_name="ACME Corp"
            ... )
        """
        from nest.templates import load_template
        
        template_config = load_template(template_name)
        template_config.update(overrides)
        
        print(f"📋 Created agent from template: {template_name}")
        return cls(**template_config)
    
    @classmethod
    def from_llm(
        cls,
        id: str,
        name: str,
        model: str = "claude-3-haiku-20240307",
        system_prompt: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        **kwargs
    ) -> "Agent":
        """
        Create LLM-powered agent with explicit configuration
        
        Args:
            id: Agent ID
            name: Agent name
            model: LLM model to use
            system_prompt: System prompt for the agent
            capabilities: List of capabilities
            **kwargs: Additional configuration
        
        Returns:
            Configured Agent instance
        
        Example:
            >>> agent = Agent.from_llm(
            ...     id="data-expert",
            ...     name="Data Scientist",
            ...     model="claude-3-5-sonnet-20241022",
            ...     capabilities=["Python", "Statistics", "ML"]
            ... )
        """
        # Generate system prompt from capabilities if not provided
        if system_prompt is None and capabilities:
            caps_text = ", ".join(capabilities)
            system_prompt = (
                f"You are {name}, an AI assistant.\n\n"
                f"Your capabilities include: {caps_text}\n\n"
                f"You are part of the NANDA agent network and can communicate "
                f"with other agents using the @agent-id syntax."
            )
        
        return cls(
            id=id,
            name=name,
            prompt=system_prompt,
            model=model,
            capabilities=capabilities or [],
            **kwargs
        )
    
    @property
    def is_running(self) -> bool:
        """Check if agent is currently running"""
        return self._running
    
    @property
    def url(self) -> str:
        """Get agent URL"""
        return f"http://{self.config.host}:{self.config.port}"
    
    def __repr__(self) -> str:
        status = "running" if self._running else "stopped"
        return (
            f"Agent(id='{self.config.id}', "
            f"name='{self.config.name}', "
            f"port={self.config.port}, "
            f"status='{status}')"
        )
    
    def __str__(self) -> str:
        return f"{self.config.name} ({self.config.id})"

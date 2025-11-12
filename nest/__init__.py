"""
NEST SDK - Build AI Agents with Agent-to-Agent Communication

A production-ready framework for creating, deploying, and managing 
specialized AI agents with seamless A2A communication.

Example:
    >>> from nest import Agent
    >>> agent = Agent(
    ...     id="fashion-expert",
    ...     name="Fashion Consultant",
    ...     prompt="You are a sustainable fashion expert..."
    ... )
    >>> agent.start()
"""

__version__ = "3.0.0"
__author__ = "NANDA Team"
__license__ = "MIT"

# Core exports
from nest.agent import Agent, AgentConfig
from nest.client import NestClient, AgentInfo, DeploymentInfo
from nest.config import NestConfig
from nest.exceptions import (
    NestError,
    AgentNotFoundError,
    RegistryError,
    DeploymentError,
    ConfigError,
    AuthenticationError,
    RateLimitError,
)

__all__ = [
    # Core classes
    "Agent",
    "AgentConfig",
    "NestClient",
    "NestConfig",
    # Data classes
    "AgentInfo",
    "DeploymentInfo",
    # Exceptions
    "NestError",
    "AgentNotFoundError",
    "RegistryError",
    "DeploymentError",
    "ConfigError",
    "AuthenticationError",
    "RateLimitError",
    # Metadata
    "__version__",
]

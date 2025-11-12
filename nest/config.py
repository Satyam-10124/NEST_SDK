"""
Configuration management for NEST SDK
"""

import os
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, validator

from nest.exceptions import ConfigError


class NestConfig(BaseModel):
    """
    NEST project configuration
    
    This class manages configuration for NEST projects using Pydantic
    for validation and type safety.
    """
    
    project_name: str
    version: str = "1.0.0"
    
    # Registry settings
    registry_url: Optional[str] = Field(
        default=None,
        description="NANDA registry URL"
    )
    mcp_registry_url: Optional[str] = Field(
        default=None,
        description="MCP registry URL"
    )
    
    # Default agent settings
    default_model: str = Field(
        default="claude-3-haiku-20240307",
        description="Default LLM model"
    )
    default_port: int = Field(
        default=6000,
        ge=1,
        le=65535,
        description="Default port for agents"
    )
    default_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Default LLM temperature"
    )
    default_max_tokens: int = Field(
        default=1000,
        ge=1,
        description="Default max tokens"
    )
    
    # Deployment settings
    deployment: Dict[str, Any] = Field(
        default_factory=lambda: {
            "provider": "aws",
            "region": "us-east-1",
            "instance_type": "t3.micro",
            "auto_scale": False
        },
        description="Deployment configuration"
    )
    
    # Agent definitions
    agents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of agent configurations"
    )
    
    # Monitoring
    monitoring: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "metrics_port": 9090,
            "log_level": "INFO"
        },
        description="Monitoring configuration"
    )
    
    # Security
    security: Dict[str, Any] = Field(
        default_factory=lambda: {
            "require_api_key": False,
            "allowed_origins": ["*"],
            "rate_limit": 100
        },
        description="Security configuration"
    )
    
    class Config:
        """Pydantic config"""
        extra = "allow"  # Allow additional fields
    
    @validator('project_name')
    def validate_project_name(cls, v):
        """Validate project name"""
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()
    
    @classmethod
    def load(cls, config_path: str = "nest.config.yaml") -> "NestConfig":
        """
        Load configuration from file
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
        
        Returns:
            NestConfig instance
        
        Raises:
            ConfigError: If config file not found or invalid
        
        Example:
            >>> config = NestConfig.load("nest.config.yaml")
            >>> print(config.project_name)
        """
        path = Path(config_path)
        
        if not path.exists():
            raise ConfigError(f"Config file not found: {config_path}")
        
        try:
            with open(path, 'r') as f:
                if path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif path.suffix == '.json':
                    data = json.load(f)
                else:
                    raise ConfigError(f"Unsupported config format: {path.suffix}")
            
            # Expand environment variables
            data = cls._expand_env_vars(data)
            
            print(f"✅ Loaded config from: {config_path}")
            return cls(**data)
            
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file: {e}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load config: {e}")
    
    def save(self, config_path: str = "nest.config.yaml") -> None:
        """
        Save configuration to file
        
        Args:
            config_path: Path to save configuration
        
        Example:
            >>> config = NestConfig.create_default("my-project")
            >>> config.save("nest.config.yaml")
        """
        path = Path(config_path)
        
        try:
            # Convert to dict
            data = self.dict()
            
            with open(path, 'w') as f:
                if path.suffix in ['.yaml', '.yml']:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
                elif path.suffix == '.json':
                    json.dump(data, f, indent=2)
                else:
                    raise ConfigError(f"Unsupported config format: {path.suffix}")
            
            print(f"💾 Saved config to: {config_path}")
            
        except Exception as e:
            raise ConfigError(f"Failed to save config: {e}")
    
    @staticmethod
    def _expand_env_vars(data: Any) -> Any:
        """
        Recursively expand environment variables in configuration
        
        Supports ${VAR_NAME} syntax
        
        Args:
            data: Configuration data (dict, list, or string)
        
        Returns:
            Data with environment variables expanded
        """
        if isinstance(data, dict):
            return {k: NestConfig._expand_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [NestConfig._expand_env_vars(item) for item in data]
        elif isinstance(data, str):
            # Check for ${VAR_NAME} pattern
            if data.startswith("${") and data.endswith("}"):
                env_var = data[2:-1]
                return os.getenv(env_var, data)  # Return original if not found
        return data
    
    @classmethod
    def create_default(cls, project_name: str) -> "NestConfig":
        """
        Create default configuration
        
        Args:
            project_name: Name of the project
        
        Returns:
            NestConfig with default values
        
        Example:
            >>> config = NestConfig.create_default("my-nest-project")
            >>> config.save()
        """
        return cls(
            project_name=project_name,
            registry_url="${NEST_REGISTRY_URL}",
            mcp_registry_url="${MCP_REGISTRY_URL}",
            agents=[]
        )
    
    def add_agent(
        self,
        agent_id: str,
        **agent_config
    ) -> None:
        """
        Add agent configuration
        
        Args:
            agent_id: Agent identifier
            **agent_config: Agent configuration fields
        
        Example:
            >>> config.add_agent(
            ...     agent_id="fashion-expert",
            ...     name="Fashion Consultant",
            ...     port=6000
            ... )
        """
        agent_config['id'] = agent_id
        self.agents.append(agent_config)
        print(f"➕ Added agent: {agent_id}")
    
    def get_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for specific agent
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent configuration dict or None if not found
        """
        for agent in self.agents:
            if agent.get('id') == agent_id:
                return agent
        return None
    
    def __repr__(self) -> str:
        return f"NestConfig(project='{self.project_name}', agents={len(self.agents)})"

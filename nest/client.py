"""
NEST Client for managing and interacting with agents
"""

import asyncio
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from nest.exceptions import AgentNotFoundError, RegistryError, NestError


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    
    id: str
    name: str
    url: str
    status: str
    capabilities: List[str]
    uptime: Optional[int] = None
    last_seen: Optional[str] = None
    model: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id}) - {self.status}"


@dataclass
class DeploymentInfo:
    """Information about an agent deployment"""
    
    agent_id: str
    provider: str
    region: str
    instance_id: str
    url: str
    status: str
    deployed_at: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.agent_id} on {self.provider} ({self.status})"


class NestClient:
    """
    Client for managing NANDA agents
    
    This class provides methods for discovering agents, sending A2A messages,
    and managing deployments.
    
    Examples:
        >>> from nest import NestClient
        >>> client = NestClient(registry_url="http://registry.nanda.ai")
        >>> agents = client.list_agents()
        >>> for agent in agents:
        ...     print(agent.name, agent.status)
        
        >>> response = client.send_message(
        ...     from_agent="user",
        ...     to_agent="fashion-expert",
        ...     message="What's trending?"
        ... )
    """
    
    def __init__(
        self,
        registry_url: str = "http://registry.nanda.ai",
        timeout: int = 30,
        api_key: Optional[str] = None
    ):
        """
        Initialize NEST client
        
        Args:
            registry_url: URL of the NANDA registry
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        self.registry_url = registry_url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key
        
        # Setup session with headers
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        print(f"🌐 NEST Client initialized (registry: {self.registry_url})")
    
    def list_agents(
        self,
        status: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> List[AgentInfo]:
        """
        List all registered agents
        
        Args:
            status: Filter by status ('active', 'inactive', 'error')
            capabilities: Filter by capabilities
        
        Returns:
            List of AgentInfo objects
        
        Raises:
            RegistryError: If registry communication fails
        
        Example:
            >>> agents = client.list_agents(status="active")
            >>> print(f"Found {len(agents)} active agents")
        """
        try:
            params = {}
            if status:
                params['status'] = status
            if capabilities:
                params['capabilities'] = ','.join(capabilities)
            
            response = self.session.get(
                f"{self.registry_url}/agents",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            agents_data = response.json()
            agents = [AgentInfo(**agent) for agent in agents_data]
            
            print(f"📋 Found {len(agents)} agent(s)")
            return agents
            
        except requests.exceptions.RequestException as e:
            raise RegistryError(f"Failed to list agents: {e}")
    
    def get_agent(self, agent_id: str) -> AgentInfo:
        """
        Get specific agent details
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            AgentInfo object
        
        Raises:
            AgentNotFoundError: If agent doesn't exist
            RegistryError: If registry communication fails
        
        Example:
            >>> agent = client.get_agent("fashion-expert")
            >>> print(agent.url)
        """
        try:
            response = self.session.get(
                f"{self.registry_url}/agents/{agent_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 404:
                raise AgentNotFoundError(f"Agent '{agent_id}' not found")
            
            response.raise_for_status()
            return AgentInfo(**response.json())
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
                raise AgentNotFoundError(f"Agent '{agent_id}' not found")
            raise RegistryError(f"Failed to get agent: {e}")
    
    def search_agents(
        self,
        query: str,
        limit: int = 10
    ) -> List[AgentInfo]:
        """
        Search for agents by name, capabilities, or description
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of matching AgentInfo objects
        
        Example:
            >>> agents = client.search_agents("customer support")
        """
        try:
            params = {
                'q': query,
                'limit': limit
            }
            
            response = self.session.get(
                f"{self.registry_url}/agents/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            agents_data = response.json()
            return [AgentInfo(**agent) for agent in agents_data]
            
        except requests.exceptions.RequestException as e:
            raise RegistryError(f"Failed to search agents: {e}")
    
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Send A2A message between agents
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            message: Message content
            conversation_id: Optional conversation ID for tracking
        
        Returns:
            Response from target agent
        
        Raises:
            AgentNotFoundError: If target agent not found
            NestError: If message sending fails
        
        Example:
            >>> response = client.send_message(
            ...     from_agent="user-agent",
            ...     to_agent="fashion-expert",
            ...     message="What's trending in sustainable fashion?"
            ... )
            >>> print(response)
        """
        # Get target agent info
        agent_info = self.get_agent(to_agent)
        
        # Prepare A2A message payload
        payload = {
            "content": {
                "text": message,
                "type": "text"
            },
            "role": "user",
            "conversation_id": conversation_id or f"cli-{datetime.now().timestamp()}",
            "from_agent": from_agent
        }
        
        try:
            response = self.session.post(
                f"{agent_info.url}/a2a",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("content", {}).get("text", "")
            
        except requests.exceptions.RequestException as e:
            raise NestError(f"Failed to send message to {to_agent}: {e}")
    
    async def send_message_async(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Async version of send_message
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            message: Message content
            conversation_id: Optional conversation ID
        
        Returns:
            Response from target agent
        """
        return await asyncio.to_thread(
            self.send_message,
            from_agent,
            to_agent,
            message,
            conversation_id
        )
    
    def deploy(
        self,
        agent: "Agent",
        provider: str = "aws",
        region: str = "us-east-1",
        instance_type: str = "t3.micro",
        **kwargs
    ) -> DeploymentInfo:
        """
        Deploy agent to cloud
        
        Args:
            agent: Agent instance to deploy
            provider: Cloud provider ('aws', 'gcp', 'azure', 'local')
            region: Deployment region
            instance_type: Instance type
            **kwargs: Additional deployment options
        
        Returns:
            DeploymentInfo object
        
        Raises:
            DeploymentError: If deployment fails
        
        Example:
            >>> from nest import Agent, NestClient
            >>> agent = Agent(id="my-agent", prompt="...")
            >>> client = NestClient()
            >>> deployment = client.deploy(agent, provider="aws")
            >>> print(f"Deployed at: {deployment.url}")
        """
        from nest.deployment import deploy_to_cloud
        
        print(f"🚀 Deploying agent '{agent.config.id}' to {provider}...")
        
        return deploy_to_cloud(
            agent=agent,
            provider=provider,
            region=region,
            instance_type=instance_type,
            **kwargs
        )
    
    def health_check(self, agent_id: str) -> Dict[str, Any]:
        """
        Check agent health
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Health status dictionary
        
        Example:
            >>> health = client.health_check("fashion-expert")
            >>> print(health['status'])
        """
        agent_info = self.get_agent(agent_id)
        
        try:
            response = self.session.get(
                f"{agent_info.url}/health",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_metrics(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent metrics
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Metrics dictionary
        
        Example:
            >>> metrics = client.get_metrics("fashion-expert")
            >>> print(f"Requests: {metrics['requests_total']}")
        """
        agent_info = self.get_agent(agent_id)
        
        try:
            response = self.session.get(
                f"{agent_info.url}/metrics",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NestError(f"Failed to get metrics: {e}")
    
    def __repr__(self) -> str:
        return f"NestClient(registry='{self.registry_url}')"

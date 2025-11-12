"""
Deployment modules for NEST agents
"""

from typing import Any
from nest.client import DeploymentInfo
from nest.exceptions import DeploymentError


def deploy_to_cloud(
    agent: "Agent",
    provider: str = "aws",
    region: str = "us-east-1",
    instance_type: str = "t3.micro",
    **kwargs
) -> DeploymentInfo:
    """
    Deploy agent to cloud provider
    
    Args:
        agent: Agent instance to deploy
        provider: Cloud provider ('aws', 'gcp', 'azure', 'local')
        region: Deployment region
        instance_type: Instance type/size
        **kwargs: Provider-specific options
    
    Returns:
        DeploymentInfo object
    
    Raises:
        DeploymentError: If deployment fails
    """
    if provider == "aws":
        from nest.deployment.aws import AWSDeployer
        deployer = AWSDeployer(region=region, instance_type=instance_type)
        return deployer.deploy(agent, **kwargs)
    
    elif provider == "local":
        from nest.deployment.local import LocalDeployer
        deployer = LocalDeployer()
        return deployer.deploy(agent, **kwargs)
    
    elif provider == "docker":
        from nest.deployment.docker import DockerDeployer
        deployer = DockerDeployer()
        return deployer.deploy(agent, **kwargs)
    
    else:
        raise DeploymentError(
            f"Unsupported provider: {provider}. "
            f"Supported: aws, local, docker"
        )


__all__ = ['deploy_to_cloud']

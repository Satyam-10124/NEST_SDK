"""
Custom exceptions for NEST SDK
"""


class NestError(Exception):
    """Base exception for all NEST errors"""
    pass


class AgentNotFoundError(NestError):
    """Raised when an agent is not found in the registry"""
    pass


class RegistryError(NestError):
    """Raised when there's an error communicating with the registry"""
    pass


class DeploymentError(NestError):
    """Raised when deployment fails"""
    pass


class ConfigError(NestError):
    """Raised when there's a configuration error"""
    pass


class AuthenticationError(NestError):
    """Raised when authentication fails"""
    pass


class RateLimitError(NestError):
    """Raised when rate limit is exceeded"""
    pass


class ValidationError(NestError):
    """Raised when validation fails"""
    pass


class TemplateNotFoundError(NestError):
    """Raised when a template is not found"""
    pass

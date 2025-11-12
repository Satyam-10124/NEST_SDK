"""
Agent templates for quick starts
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List

from nest.exceptions import TemplateNotFoundError


def get_templates_dir() -> Path:
    """Get the templates directory path"""
    return Path(__file__).parent / "data"


def list_templates() -> List[str]:
    """
    List all available templates
    
    Returns:
        List of template names
    
    Example:
        >>> from nest.templates import list_templates
        >>> templates = list_templates()
        >>> print(templates)
        ['customer-support', 'data-analyst', 'code-reviewer', ...]
    """
    templates_dir = get_templates_dir()
    
    if not templates_dir.exists():
        return []
    
    templates = []
    for file in templates_dir.glob("*.yaml"):
        templates.append(file.stem)
    
    return sorted(templates)


def load_template(template_name: str) -> Dict[str, Any]:
    """
    Load agent template configuration
    
    Args:
        template_name: Name of the template (without .yaml extension)
    
    Returns:
        Template configuration dictionary
    
    Raises:
        TemplateNotFoundError: If template doesn't exist
    
    Example:
        >>> from nest.templates import load_template
        >>> config = load_template("customer-support")
        >>> print(config['name'])
    """
    templates_dir = get_templates_dir()
    template_file = templates_dir / f"{template_name}.yaml"
    
    if not template_file.exists():
        available = list_templates()
        raise TemplateNotFoundError(
            f"Template '{template_name}' not found. "
            f"Available templates: {', '.join(available)}"
        )
    
    try:
        with open(template_file, 'r') as f:
            template_data = yaml.safe_load(f)
        
        # Extract agent configuration
        if 'agent' in template_data:
            agent_config = template_data['agent']
        else:
            agent_config = template_data
        
        # Add template metadata
        agent_config['_template'] = template_name
        
        return agent_config
        
    except Exception as e:
        raise TemplateNotFoundError(f"Failed to load template '{template_name}': {e}")


def get_template_info(template_name: str) -> Dict[str, Any]:
    """
    Get template metadata without loading full config
    
    Args:
        template_name: Name of the template
    
    Returns:
        Template metadata (name, description, version, etc.)
    
    Example:
        >>> from nest.templates import get_template_info
        >>> info = get_template_info("customer-support")
        >>> print(info['description'])
    """
    templates_dir = get_templates_dir()
    template_file = templates_dir / f"{template_name}.yaml"
    
    if not template_file.exists():
        raise TemplateNotFoundError(f"Template '{template_name}' not found")
    
    with open(template_file, 'r') as f:
        data = yaml.safe_load(f)
    
    return data.get('metadata', {})


__all__ = [
    'list_templates',
    'load_template',
    'get_template_info',
    'get_templates_dir'
]

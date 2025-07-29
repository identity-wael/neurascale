"""Configuration management for MCP servers."""

import yaml
import os
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load MCP server configuration.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "server_config.yaml")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Expand environment variables
    config = _expand_env_vars(config)
    
    return config


def _expand_env_vars(obj: Any) -> Any:
    """Recursively expand environment variables in configuration."""
    if isinstance(obj, dict):
        return {key: _expand_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # Expand ${VAR:-default} syntax
        import re
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_expr = match.group(1)
            if ':-' in var_expr:
                var_name, default = var_expr.split(':-', 1)
                return os.environ.get(var_name, default)
            else:
                return os.environ.get(var_expr, match.group(0))
        
        return re.sub(pattern, replace_var, obj)
    else:
        return obj
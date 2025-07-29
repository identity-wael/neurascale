"""Configuration management for MCP servers."""

import yaml
import os
import logging
from typing import Dict, Any, Optional

from ..utils.gcp_secrets import GCPSecretManager, resolve_gcp_secret_uri

logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load MCP server configuration.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "server_config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Expand environment variables
    config = _expand_env_vars(config)

    # Resolve GCP secrets
    config = _resolve_gcp_secrets(config)

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

        pattern = r"\$\{([^}]+)\}"

        def replace_var(match):
            var_expr = match.group(1)
            if ":-" in var_expr:
                var_name, default = var_expr.split(":-", 1)
                return os.environ.get(var_name, default)
            else:
                return os.environ.get(var_expr, match.group(0))

        return re.sub(pattern, replace_var, obj)
    else:
        return obj


def _resolve_gcp_secrets(
    obj: Any, secret_manager: Optional[GCPSecretManager] = None
) -> Any:
    """Recursively resolve GCP secret URIs in configuration.

    Args:
        obj: Configuration object to process
        secret_manager: Optional GCPSecretManager instance (created if None)

    Returns:
        Configuration with resolved secrets
    """
    if isinstance(obj, dict):
        return {
            key: _resolve_gcp_secrets(value, secret_manager)
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [_resolve_gcp_secrets(item, secret_manager) for item in obj]
    elif isinstance(obj, str) and obj.startswith("gcp-secret://"):
        # Initialize secret manager if needed
        if secret_manager is None:
            project_id = os.getenv("GCP_PROJECT_ID")
            if not project_id:
                logger.warning("GCP_PROJECT_ID not set, cannot resolve GCP secrets")
                return obj
            secret_manager = GCPSecretManager(project_id)

        resolved_value = resolve_gcp_secret_uri(obj, secret_manager)
        if resolved_value is None:
            logger.error(f"Failed to resolve GCP secret: {obj}")
            # Return the original URI as fallback
            return obj
        return resolved_value
    else:
        return obj


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate MCP server configuration.

    Args:
        config: Configuration dictionary

    Returns:
        True if configuration is valid
    """
    required_sections = ["servers", "auth", "permissions"]

    for section in required_sections:
        if section not in config:
            logger.error(f"Missing required configuration section: {section}")
            return False

    # Validate server configurations
    servers = config.get("servers", {})
    if not servers:
        logger.error("No servers configured")
        return False

    for server_name, server_config in servers.items():
        if "port" not in server_config:
            logger.error(f"Server {server_name} missing required 'port' configuration")
            return False

        port = server_config["port"]
        if not isinstance(port, int) or port < 1 or port > 65535:
            logger.error(f"Server {server_name} has invalid port: {port}")
            return False

    # Validate auth configuration
    auth = config.get("auth", {})
    if "api_key_salt" not in auth:
        logger.error("Missing required auth.api_key_salt configuration")
        return False

    if "jwt_secret" not in auth:
        logger.error("Missing required auth.jwt_secret configuration")
        return False

    logger.info("Configuration validation passed")
    return True


def get_server_config(
    config: Dict[str, Any], server_name: str
) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific server.

    Args:
        config: Full configuration dictionary
        server_name: Name of the server

    Returns:
        Server configuration or None if not found
    """
    servers = config.get("servers", {})
    server_config = servers.get(server_name)

    if not server_config:
        logger.error(f"Server configuration not found: {server_name}")
        return None

    # Merge with global configuration
    merged_config = {
        "auth": config.get("auth", {}),
        "permissions": config.get("permissions", {}),
        "rate_limits": config.get("rate_limits", {}),
        **server_config,
    }

    return merged_config

"""GCP Secret Manager integration for MCP server configuration."""

import logging
import os
from typing import Optional, Dict, Any

try:
    from google.cloud import secretmanager

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    secretmanager = None

logger = logging.getLogger(__name__)


class GCPSecretManager:
    """GCP Secret Manager client for retrieving secrets."""

    def __init__(self, project_id: Optional[str] = None):
        """Initialize GCP Secret Manager client.

        Args:
            project_id: GCP project ID. If None, uses GCP_PROJECT_ID env var.
        """
        if not GCP_AVAILABLE:
            logger.warning(
                "Google Cloud Secret Manager not available. "
                "Install google-cloud-secret-manager to use GCP secrets."
            )
            self.client = None
            self.project_id = None
            return

        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        if not self.project_id:
            logger.warning("GCP_PROJECT_ID not set. GCP Secret Manager unavailable.")
            self.client = None
            return

        try:
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info(
                f"Initialized GCP Secret Manager for project: {self.project_id}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize GCP Secret Manager: {e}")
            self.client = None

    def get_secret(self, secret_name: str, version: str = "latest") -> Optional[str]:
        """Retrieve a secret from GCP Secret Manager.

        Args:
            secret_name: Name of the secret
            version: Version of the secret (default: "latest")

        Returns:
            Secret value as string, or None if not found/error
        """
        if not self.client or not self.project_id:
            logger.warning(
                f"GCP Secret Manager not available for secret: {secret_name}"
            )
            return None

        try:
            secret_path = (
                f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            )
            response = self.client.access_secret_version(request={"name": secret_path})
            secret_value = response.payload.data.decode("UTF-8")

            logger.debug(f"Successfully retrieved secret: {secret_name}")
            return secret_value

        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            return None

    def create_secret(self, secret_name: str, secret_value: str) -> bool:
        """Create a new secret in GCP Secret Manager.

        Args:
            secret_name: Name of the secret to create
            secret_value: Value of the secret

        Returns:
            True if successful, False otherwise
        """
        if not self.client or not self.project_id:
            logger.warning("GCP Secret Manager not available for secret creation")
            return False

        try:
            # Create the secret
            parent = f"projects/{self.project_id}"
            secret = {"replication": {"automatic": {}}}

            response = self.client.create_secret(
                request={"parent": parent, "secret_id": secret_name, "secret": secret}
            )

            # Add the secret version
            response = self.client.add_secret_version(
                request={
                    "parent": response.name,
                    "payload": {"data": secret_value.encode("UTF-8")},
                }
            )

            logger.info(f"Created secret: {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create secret {secret_name}: {e}")
            return False

    def update_secret(self, secret_name: str, secret_value: str) -> bool:
        """Update an existing secret with a new version.

        Args:
            secret_name: Name of the secret to update
            secret_value: New value of the secret

        Returns:
            True if successful, False otherwise
        """
        if not self.client or not self.project_id:
            logger.warning("GCP Secret Manager not available for secret update")
            return False

        try:
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}"

            response = self.client.add_secret_version(
                request={
                    "parent": secret_path,
                    "payload": {"data": secret_value.encode("UTF-8")},
                }
            )

            logger.info(f"Updated secret: {secret_name} (version: {response.name})")
            return True

        except Exception as e:
            logger.error(f"Failed to update secret {secret_name}: {e}")
            return False

    def list_secrets(self) -> Dict[str, Dict[str, Any]]:
        """List all secrets in the project.

        Returns:
            Dictionary mapping secret names to their metadata
        """
        if not self.client or not self.project_id:
            logger.warning("GCP Secret Manager not available for listing secrets")
            return {}

        try:
            parent = f"projects/{self.project_id}"
            secrets = {}

            for secret in self.client.list_secrets(request={"parent": parent}):
                secret_name = secret.name.split("/")[-1]
                secrets[secret_name] = {
                    "name": secret.name,
                    "create_time": secret.create_time,
                    "replication": secret.replication,
                }

            logger.debug(f"Listed {len(secrets)} secrets")
            return secrets

        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return {}


def resolve_gcp_secret_uri(
    uri: str, secret_manager: Optional[GCPSecretManager] = None
) -> Optional[str]:
    """Resolve a GCP secret URI to its actual value.

    Args:
        uri: URI in format "gcp-secret://projects/{project}/secrets/{name}/versions/{version}"
        secret_manager: Optional GCPSecretManager instance

    Returns:
        Secret value or None if not found
    """
    if not uri.startswith("gcp-secret://"):
        return uri  # Not a GCP secret URI

    try:
        # Parse the URI: gcp-secret://projects/{project}/secrets/{name}/versions/{version}
        path = uri.replace("gcp-secret://", "")
        parts = path.split("/")

        if (
            len(parts) < 6
            or parts[0] != "projects"
            or parts[2] != "secrets"
            or parts[4] != "versions"
        ):
            logger.error(f"Invalid GCP secret URI format: {uri}")
            return None

        project_id = parts[1]
        secret_name = parts[3]
        version = parts[5]

        # Use provided secret manager or create a new one
        if secret_manager is None:
            secret_manager = GCPSecretManager(project_id)

        return secret_manager.get_secret(secret_name, version)

    except Exception as e:
        logger.error(f"Failed to resolve GCP secret URI {uri}: {e}")
        return None


def create_mcp_secrets(project_id: str) -> bool:
    """Create required MCP secrets in GCP Secret Manager.

    Args:
        project_id: GCP Project ID

    Returns:
        True if all secrets created successfully
    """
    import secrets
    import string

    secret_manager = GCPSecretManager(project_id)
    if not secret_manager.client:
        logger.error("Unable to initialize GCP Secret Manager")
        return False

    # Generate secure random values
    api_key_salt = "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
    )
    jwt_secret = "".join(
        secrets.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(64)
    )

    secrets_to_create = [
        ("mcp-api-key-salt", api_key_salt),
        ("mcp-jwt-secret", jwt_secret),
    ]

    success = True
    for secret_name, secret_value in secrets_to_create:
        if not secret_manager.create_secret(secret_name, secret_value):
            logger.error(f"Failed to create secret: {secret_name}")
            success = False
        else:
            logger.info(f"Created MCP secret: {secret_name}")

    return success


if __name__ == "__main__":
    """CLI for managing MCP secrets."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python gcp_secrets.py <command> [args...]")
        print("Commands:")
        print("  create-mcp-secrets <project_id>  - Create required MCP secrets")
        print("  get-secret <project_id> <secret_name> [version] - Get a secret value")
        print("  list-secrets <project_id>  - List all secrets")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-mcp-secrets":
        if len(sys.argv) < 3:
            print("Usage: python gcp_secrets.py create-mcp-secrets <project_id>")
            sys.exit(1)
        project_id = sys.argv[2]
        success = create_mcp_secrets(project_id)
        sys.exit(0 if success else 1)

    elif command == "get-secret":
        if len(sys.argv) < 4:
            print(
                "Usage: python gcp_secrets.py get-secret <project_id> <secret_name> [version]"
            )
            sys.exit(1)
        project_id = sys.argv[2]
        secret_name = sys.argv[3]
        version = sys.argv[4] if len(sys.argv) > 4 else "latest"

        sm = GCPSecretManager(project_id)
        value = sm.get_secret(secret_name, version)
        if value:
            print(value)
        else:
            print("Secret not found or error occurred")
            sys.exit(1)

    elif command == "list-secrets":
        if len(sys.argv) < 3:
            print("Usage: python gcp_secrets.py list-secrets <project_id>")
            sys.exit(1)
        project_id = sys.argv[2]

        sm = GCPSecretManager(project_id)
        secrets = sm.list_secrets()
        for name, info in secrets.items():
            print(f"{name}: {info['name']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

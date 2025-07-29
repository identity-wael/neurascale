"""NVIDIA Nucleus server client for Omniverse."""

import logging
from typing import Dict, List, Any
from urllib.parse import urlparse
import aiohttp

logger = logging.getLogger(__name__)


class NucleusClient:
    """Client for interacting with NVIDIA Nucleus server.

    Nucleus provides the collaboration layer for Omniverse,
    handling file storage, versioning, and live synchronization.
    """

    def __init__(self, server_url: str):
        """Initialize Nucleus client.

        Args:
            server_url: Nucleus server URL (e.g., "omniverse://localhost/neurascale")
        """
        self.server_url = server_url
        self.parsed_url = urlparse(server_url)
        self.session = None
        self.connected = False
        self.auth_token = None

        # Connection parameters
        self.timeout = 30.0
        self.max_retries = 3

        logger.info(f"NucleusClient initialized for {server_url}")

    async def connect(self) -> bool:
        """Connect to Nucleus server.

        Returns:
            Success status
        """
        try:
            # Create HTTP session for REST API
            self.session = aiohttp.ClientSession()

            # Authenticate with Nucleus
            await self._authenticate()

            # Verify connection
            if await self._verify_connection():
                self.connected = True
                logger.info("Connected to Nucleus server")
                return True
            else:
                logger.error("Failed to verify Nucleus connection")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to Nucleus: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Nucleus server."""
        try:
            if self.session:
                await self.session.close()

            self.connected = False
            self.auth_token = None

            logger.info("Disconnected from Nucleus server")

        except Exception as e:
            logger.error(f"Error disconnecting from Nucleus: {e}")

    async def create_folder(self, path: str) -> bool:
        """Create folder on Nucleus server.

        Args:
            path: Folder path relative to server root

        Returns:
            Success status
        """
        if not self.connected:
            raise RuntimeError("Not connected to Nucleus")

        try:
            # Nucleus API endpoint for folder creation
            api_url = self._build_api_url("folders")

            payload = {"path": path, "recursive": True}

            async with self.session.post(
                api_url, json=payload, headers=self._get_headers()
            ) as response:
                if response.status == 201:
                    logger.info(f"Created folder: {path}")
                    return True
                else:
                    logger.error(f"Failed to create folder: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return False

    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to Nucleus server.

        Args:
            local_path: Local file path
            remote_path: Remote path on Nucleus

        Returns:
            Success status
        """
        if not self.connected:
            raise RuntimeError("Not connected to Nucleus")

        try:
            # Read file data
            with open(local_path, "rb") as f:
                file_data = f.read()

            # Upload to Nucleus
            api_url = self._build_api_url("files")

            data = aiohttp.FormData()
            data.add_field("file", file_data, filename=remote_path)

            async with self.session.post(
                api_url, data=data, headers=self._get_headers()
            ) as response:
                if response.status == 201:
                    logger.info(f"Uploaded file: {remote_path}")
                    return True
                else:
                    logger.error(f"Failed to upload file: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False

    async def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """List files in Nucleus folder.

        Args:
            path: Folder path

        Returns:
            List of file information
        """
        if not self.connected:
            raise RuntimeError("Not connected to Nucleus")

        try:
            api_url = self._build_api_url("files")
            params = {"path": path}

            async with self.session.get(
                api_url, params=params, headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    files = await response.json()
                    return files.get("items", [])
                else:
                    logger.error(f"Failed to list files: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []

    async def get_checkpoints(self, path: str) -> List[Dict[str, Any]]:
        """Get file checkpoints (versions).

        Args:
            path: File path

        Returns:
            List of checkpoints
        """
        if not self.connected:
            raise RuntimeError("Not connected to Nucleus")

        try:
            api_url = self._build_api_url("checkpoints")
            params = {"path": path}

            async with self.session.get(
                api_url, params=params, headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    checkpoints = await response.json()
                    return checkpoints.get("checkpoints", [])
                else:
                    return []

        except Exception as e:
            logger.error(f"Error getting checkpoints: {e}")
            return []

    async def create_live_session(self, session_name: str) -> str:
        """Create live collaboration session.

        Args:
            session_name: Name for the session

        Returns:
            Session URL
        """
        if not self.connected:
            raise RuntimeError("Not connected to Nucleus")

        try:
            api_url = self._build_api_url("live-sessions")

            payload = {"name": session_name, "type": "collaboration", "max_users": 10}

            async with self.session.post(
                api_url, json=payload, headers=self._get_headers()
            ) as response:
                if response.status == 201:
                    session_data = await response.json()
                    session_url = session_data.get("url")
                    logger.info(f"Created live session: {session_url}")
                    return session_url
                else:
                    raise RuntimeError(f"Failed to create session: {response.status}")

        except Exception as e:
            logger.error(f"Error creating live session: {e}")
            raise

    async def _authenticate(self):
        """Authenticate with Nucleus server."""
        # In a real implementation, this would handle OAuth or API key auth
        # For now, we'll simulate authentication
        self.auth_token = "simulated_auth_token"
        logger.info("Authenticated with Nucleus (simulated)")

    async def _verify_connection(self) -> bool:
        """Verify connection to Nucleus server."""
        try:
            # Try to access server info endpoint
            api_url = self._build_api_url("info")

            async with self.session.get(
                api_url, headers=self._get_headers(), timeout=self.timeout
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Connection verification failed: {e}")
            return False

    def _build_api_url(self, endpoint: str) -> str:
        """Build API URL for Nucleus endpoint."""
        # Convert omniverse:// to http:// for REST API
        base_url = self.server_url.replace("omniverse://", "http://")
        return f"{base_url}/api/v1/{endpoint}"

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Nucleus API."""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        return headers

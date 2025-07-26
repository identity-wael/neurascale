"""Digital signature implementation for critical Neural Ledger events.

This module handles signing and verification of critical events using
Google Cloud KMS for HIPAA and FDA 21 CFR Part 11 compliance.
"""

import base64
import hashlib
import json
import logging
from typing import Dict, Any, Optional

from google.cloud import kms
from google.api_core import exceptions

from .event_schema import NeuralLedgerEvent, requires_signature

logger = logging.getLogger(__name__)


class EventSigner:
    """Handles digital signatures for Neural Ledger events using Cloud KMS.

    This class provides:
    - Event signing for critical events (FDA 21 CFR Part 11 compliance)
    - Signature verification
    - Key rotation support
    - Audit trail for all signing operations
    """

    def __init__(
        self,
        project_id: str,
        location: str,
        keyring: str,
        key: str,
        kms_client: Optional[kms.KeyManagementServiceClient] = None,
    ):
        """Initialize the event signer.

        Args:
            project_id: GCP project ID
            location: GCP region for KMS
            keyring: KMS keyring name
            key: KMS crypto key name
            kms_client: Optional pre-initialized KMS client
        """
        self.project_id = project_id
        self.location = location
        self.keyring = keyring
        self.key = key

        # Initialize KMS client
        self.kms_client = kms_client or kms.KeyManagementServiceClient()

        # Build key name
        self.key_name = (
            f"projects/{project_id}/locations/{location}/"
            f"keyRings/{keyring}/cryptoKeys/{key}/cryptoKeyVersions / 1"
        )

        logger.info(f"Initialized EventSigner with key: {self.key_name}")

    async def sign_event(self, event: NeuralLedgerEvent) -> str:
        """Digitally sign a critical event.

        Args:
            event: The event to sign

        Returns:
            Base64-encoded signature

        Raises:
            ValueError: If event doesn't require signature
            Exception: If signing fails
        """
        if not requires_signature(event.event_type):
            raise ValueError(
                f"Event type {event.event_type.value} does not require signature"
            )

        # Create signing payload with critical fields only
        payload = self._create_signing_payload(event)

        # Convert to canonical JSON
        message = json.dumps(payload, sort_keys=True).encode()

        # Create SHA-256 digest
        digest = {"sha256": hashlib.sha256(message).digest()}

        try:
            # Sign with KMS
            response = self.kms_client.asymmetric_sign(
                request={
                    "name": self.key_name,
                    "digest": digest,
                }
            )

            # Return base64-encoded signature
            signature = base64.b64encode(response.signature).decode()

            logger.info(
                f"Signed event {event.event_id} of type {event.event_type.value}"
            )

            return signature

        except exceptions.NotFound:
            logger.error(f"KMS key not found: {self.key_name}")
            raise
        except Exception as e:
            logger.error(f"Failed to sign event {event.event_id}: {e}")
            raise

    async def verify_signature(self, event: NeuralLedgerEvent, signature: str) -> bool:
        """Verify the digital signature of an event.

        Args:
            event: The event to verify
            signature: Base64-encoded signature

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.exceptions import InvalidSignature

            # Create the same payload that was signed
            payload = self._create_signing_payload(event)
            message = json.dumps(payload, sort_keys=True).encode()

            # Decode signature
            signature_bytes = base64.b64decode(signature)

            # Get public key for verification
            public_key_response = self.kms_client.get_public_key(
                request={"name": self.key_name}
            )

            if not public_key_response.pem:
                raise ValueError("No public key returned from KMS")

            # Load the public key
            public_key = serialization.load_pem_public_key(
                public_key_response.pem.encode()
            )

            # Verify the signature using RSA PSS padding with SHA-256
            try:
                public_key.verify(
                    signature_bytes,
                    message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH,
                    ),
                    hashes.SHA256(),
                )

                logger.info(
                    f"Signature verified successfully for event {event.event_id} "
                    f"(signature: {signature[:16]}..., key: {self.key_name})"
                )
                return True

            except InvalidSignature:
                logger.error(
                    f"Invalid signature for event {event.event_id}: "
                    "signature does not match message"
                )
                return False

        except Exception as e:
            logger.error(
                f"Signature verification failed for event {event.event_id}: {e}"
            )
            return False

    def _create_signing_payload(self, event: NeuralLedgerEvent) -> Dict[str, Any]:
        """Create a deterministic payload for signing.

        Only includes fields that are critical for integrity and compliance.

        Args:
            event: The event to create payload for

        Returns:
            Dictionary with fields to sign
        """
        payload = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "event_hash": event.event_hash,
            "previous_hash": event.previous_hash,
        }

        # Include identity fields if present
        if event.user_id:
            payload["user_id"] = event.user_id
        if event.session_id:
            payload["session_id"] = event.session_id
        if event.data_hash:
            payload["data_hash"] = event.data_hash

        # Include critical metadata fields
        if event.metadata:
            # Only include specific metadata fields that are critical
            critical_metadata_fields = [
                "resource",
                "action",
                "ip_address",
                "data_size_bytes",
            ]
            critical_metadata = {
                k: v for k, v in event.metadata.items() if k in critical_metadata_fields
            }
            if critical_metadata:
                payload["metadata"] = critical_metadata

        return payload

    async def rotate_key(self) -> str:
        """Rotate to a new key version.

        Returns:
            New key version name
        """
        try:
            # Create new key version
            parent = self.key_name.rsplit("/", 2)[0]  # Remove version suffix

            response = self.kms_client.create_crypto_key_version(
                request={
                    "parent": parent,
                    "crypto_key_version": {
                        "state": kms.CryptoKeyVersion.CryptoKeyVersionState.ENABLED,
                    },
                }
            )

            # Update key name to use new version
            self.key_name = response.name

            logger.info(f"Rotated to new key version: {self.key_name}")

            return self.key_name

        except Exception as e:
            logger.error(f"Failed to rotate key: {e}")
            raise

    async def get_key_info(self) -> Dict[str, Any]:
        """Get information about the current signing key.

        Returns:
            Dictionary with key information
        """
        try:
            # Get key version info
            key_version = self.kms_client.get_crypto_key_version(
                request={"name": self.key_name}
            )

            # Get public key
            public_key = self.kms_client.get_public_key(request={"name": self.key_name})

            return {
                "key_name": self.key_name,
                "state": key_version.state.name,
                "algorithm": key_version.algorithm.name,
                "create_time": key_version.create_time.isoformat(),
                "public_key_pem": public_key.pem,
            }

        except Exception as e:
            logger.error(f"Failed to get key info: {e}")
            raise

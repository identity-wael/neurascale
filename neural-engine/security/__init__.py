"""NeuraScale Security Module.

This module provides comprehensive security features including encryption,
authentication, authorization, HIPAA compliance, and audit logging for
protecting sensitive neural data.
"""

# Encryption
from .encryption import (
    NeuralDataEncryption,
    FieldLevelEncryption,
    EncryptionError,
    KeyRotationError,
)

# Access Control & RBAC
from .access_control import (
    Role,
    Permission,
    RolePermissionMapping,
    UserContext,
    RBACManager,
)

# Authentication & JWT
from .authentication import (
    JWTManager,
    SessionManager,
    TokenPair,
    TokenClaims,
    create_auth_system,
)

# HIPAA Compliance
from .hipaa_compliance import (
    ConsentType,
    ConsentStatus,
    ConsentRecord,
    PHIAnonymizer,
    ConsentManager,
    HIPAAComplianceManager,
    create_hipaa_system,
)

# Security Middleware
from .middleware import (
    SecurityMiddleware,
    SecurityHeaders,
    RateLimiter,
    AuthenticationDependency,
    AuthorizationDependency,
    ResourceAccessDependency,
    AuditLogger,
    require_auth,
    require_permission,
    require_resource_access,
    create_security_system,
)

# Neural Ledger Integration
from .ledger_integration import (
    SecurityEventType,
    SecurityEvent,
    SecurityAuditLogger,
    create_security_audit_system,
)

__all__ = [
    # Encryption
    "NeuralDataEncryption",
    "FieldLevelEncryption",
    "EncryptionError",
    "KeyRotationError",
    # Access Control
    "Role",
    "Permission",
    "RolePermissionMapping",
    "UserContext",
    "RBACManager",
    # Authentication
    "JWTManager",
    "SessionManager",
    "TokenPair",
    "TokenClaims",
    "create_auth_system",
    # HIPAA Compliance
    "ConsentType",
    "ConsentStatus",
    "ConsentRecord",
    "PHIAnonymizer",
    "ConsentManager",
    "HIPAAComplianceManager",
    "create_hipaa_system",
    # Middleware
    "SecurityMiddleware",
    "SecurityHeaders",
    "RateLimiter",
    "AuthenticationDependency",
    "AuthorizationDependency",
    "ResourceAccessDependency",
    "AuditLogger",
    "require_auth",
    "require_permission",
    "require_resource_access",
    "create_security_system",
    # Audit Logging
    "SecurityEventType",
    "SecurityEvent",
    "SecurityAuditLogger",
    "create_security_audit_system",
]

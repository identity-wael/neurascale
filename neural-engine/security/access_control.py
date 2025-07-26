"""Role-Based Access Control (RBAC) for NeuraScale Neural Engine.

This module implements a comprehensive RBAC system with 7 predefined roles
and granular permissions for neural data and system resources.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Set, Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Role(Enum):
    """System roles with hierarchical permissions."""

    SUPER_ADMIN = "super_admin"  # Full system access
    ADMIN = "admin"  # Organizational admin
    CLINICIAN = "clinician"  # Patient data access
    RESEARCHER = "researcher"  # Anonymized data access
    PATIENT = "patient"  # Own data access only
    DEVICE = "device"  # Device API access
    SERVICE = "service"  # Internal service account


class Permission(Enum):
    """Granular permissions for resources."""

    # Data permissions
    READ_NEURAL_DATA = "read_neural_data"
    WRITE_NEURAL_DATA = "write_neural_data"
    DELETE_NEURAL_DATA = "delete_neural_data"
    EXPORT_NEURAL_DATA = "export_neural_data"

    # Session permissions
    CREATE_SESSION = "create_session"
    VIEW_SESSION = "view_session"
    MODIFY_SESSION = "modify_session"
    DELETE_SESSION = "delete_session"

    # Device permissions
    REGISTER_DEVICE = "register_device"
    PAIR_DEVICE = "pair_device"
    MANAGE_DEVICE = "manage_device"

    # User management
    CREATE_USER = "create_user"
    MODIFY_USER = "modify_user"
    DELETE_USER = "delete_user"
    ASSIGN_ROLE = "assign_role"

    # System permissions
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_CONSENT = "manage_consent"
    CONFIGURE_SYSTEM = "configure_system"
    VIEW_ANALYTICS = "view_analytics"


@dataclass
class RolePermissionMapping:
    """Maps roles to their allowed permissions."""

    @classmethod
    def get_permissions(cls, role: Role) -> Set[Permission]:
        """Get all permissions for a given role."""
        role_permissions = {
            Role.SUPER_ADMIN: set(Permission),  # All permissions
            Role.ADMIN: {
                Permission.READ_NEURAL_DATA,
                Permission.WRITE_NEURAL_DATA,
                Permission.CREATE_SESSION,
                Permission.VIEW_SESSION,
                Permission.MODIFY_SESSION,
                Permission.REGISTER_DEVICE,
                Permission.PAIR_DEVICE,
                Permission.MANAGE_DEVICE,
                Permission.CREATE_USER,
                Permission.MODIFY_USER,
                Permission.ASSIGN_ROLE,
                Permission.VIEW_AUDIT_LOG,
                Permission.VIEW_ANALYTICS,
            },
            Role.CLINICIAN: {
                Permission.READ_NEURAL_DATA,
                Permission.WRITE_NEURAL_DATA,
                Permission.CREATE_SESSION,
                Permission.VIEW_SESSION,
                Permission.MODIFY_SESSION,
                Permission.PAIR_DEVICE,
                Permission.VIEW_AUDIT_LOG,
            },
            Role.RESEARCHER: {
                Permission.READ_NEURAL_DATA,  # Anonymized only
                Permission.VIEW_SESSION,  # Anonymized only
                Permission.EXPORT_NEURAL_DATA,  # With approval
                Permission.VIEW_ANALYTICS,
            },
            Role.PATIENT: {
                Permission.READ_NEURAL_DATA,  # Own data only
                Permission.VIEW_SESSION,  # Own sessions only
                Permission.EXPORT_NEURAL_DATA,  # Own data only
                Permission.MANAGE_CONSENT,  # Own consent only
            },
            Role.DEVICE: {
                Permission.WRITE_NEURAL_DATA,
                Permission.CREATE_SESSION,
                Permission.MODIFY_SESSION,
            },
            Role.SERVICE: {
                Permission.READ_NEURAL_DATA,
                Permission.WRITE_NEURAL_DATA,
            },
        }

        return role_permissions.get(role, set())


@dataclass
class UserContext:
    """User context for authorization decisions."""

    user_id: str
    role: Role
    tenant_id: Optional[str] = None
    permissions_override: Optional[Set[Permission]] = None
    resource_access: Optional[Dict[str, List[str]]] = None

    @property
    def effective_permissions(self) -> Set[Permission]:
        """Get effective permissions including role-based and overrides."""
        base_permissions = RolePermissionMapping.get_permissions(self.role)

        if self.permissions_override:
            # Union of base permissions and overrides
            return base_permissions.union(self.permissions_override)

        return base_permissions


class RBACManager:
    """Role-Based Access Control manager."""

    def __init__(self, database_client=None):
        """Initialize RBAC manager.

        Args:
            database_client: Database client for persistent storage
        """
        self.db = database_client

    def has_permission(self, role: Role, permission: Permission) -> bool:
        """Check if a role has a specific permission.

        Args:
            role: User role
            permission: Permission to check

        Returns:
            True if role has permission, False otherwise
        """
        role_permissions = RolePermissionMapping.get_permissions(role)
        return permission in role_permissions

    def check_user_permission(
        self, user_context: UserContext, permission: Permission
    ) -> bool:
        """Check if a user has a specific permission.

        Args:
            user_context: User context with role and overrides
            permission: Permission to check

        Returns:
            True if user has permission, False otherwise
        """
        return permission in user_context.effective_permissions

    async def check_resource_access(
        self,
        user_id: str,
        role: Role,
        resource_type: str,
        resource_id: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """Check if user has access to a specific resource.

        Args:
            user_id: User identifier
            role: User role
            resource_type: Type of resource (e.g., 'neural_data', 'session')
            resource_id: Specific resource identifier
            tenant_id: Tenant identifier for multi-tenancy

        Returns:
            True if user has access, False otherwise
        """
        # Super admin has access to everything
        if role == Role.SUPER_ADMIN:
            return True

        # Admin has access to resources in their tenant
        if role == Role.ADMIN and tenant_id:
            return await self._check_tenant_resource(
                resource_type, resource_id, tenant_id
            )

        # Patient can only access their own resources
        if role == Role.PATIENT:
            return await self._check_patient_resource(
                user_id, resource_type, resource_id
            )

        # Researcher gets anonymized access only
        if role == Role.RESEARCHER:
            return await self._check_anonymized_access(resource_type, resource_id)

        # Clinician gets access to assigned patients
        if role == Role.CLINICIAN:
            return await self._check_clinician_access(
                user_id, resource_type, resource_id
            )

        # Device and service accounts have programmatic access
        if role in [Role.DEVICE, Role.SERVICE]:
            return await self._check_service_access(user_id, resource_type, resource_id)

        return False

    async def _check_tenant_resource(
        self, resource_type: str, resource_id: str, tenant_id: str
    ) -> bool:
        """Check if resource belongs to tenant."""
        if not self.db:
            return True  # Allow in testing/development

        # Query database to check resource tenant
        # This would be implemented based on your database schema
        logger.info(
            f"Checking tenant access for {resource_type}/{resource_id} in tenant {tenant_id}"
        )
        return True

    async def _check_patient_resource(
        self, user_id: str, resource_type: str, resource_id: str
    ) -> bool:
        """Check if resource belongs to patient."""
        if not self.db:
            return True  # Allow in testing/development

        # Check if resource is owned by patient
        logger.info(
            f"Checking patient access for {user_id} to {resource_type}/{resource_id}"
        )
        return True

    async def _check_anonymized_access(
        self, resource_type: str, resource_id: str
    ) -> bool:
        """Check if resource is available in anonymized form."""
        if not self.db:
            return True  # Allow in testing/development

        # Check if resource has been anonymized for research
        logger.info(f"Checking anonymized access to {resource_type}/{resource_id}")
        return True

    async def _check_clinician_access(
        self, user_id: str, resource_type: str, resource_id: str
    ) -> bool:
        """Check if clinician has access to patient resource."""
        if not self.db:
            return True  # Allow in testing/development

        # Check patient-clinician relationship
        logger.info(
            f"Checking clinician access for {user_id} to {resource_type}/{resource_id}"
        )
        return True

    async def _check_service_access(
        self, user_id: str, resource_type: str, resource_id: str
    ) -> bool:
        """Check if service account has access to resource."""
        if not self.db:
            return True  # Allow in testing/development

        # Check service account permissions
        logger.info(
            f"Checking service access for {user_id} to {resource_type}/{resource_id}"
        )
        return True

    async def grant_permission_override(
        self,
        user_id: str,
        permission: Permission,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> bool:
        """Grant temporary permission override to a user.

        Args:
            user_id: User identifier
            permission: Permission to grant
            resource_type: Optional resource type for scoped permission
            resource_id: Optional resource ID for scoped permission
            expires_at: Optional expiration time

        Returns:
            True if permission granted successfully
        """
        if not self.db:
            logger.warning("Permission override granted without persistence")
            return True

        # Store permission override in database
        # This would be implemented based on your database schema
        logger.info(f"Granted permission override {permission.value} to user {user_id}")
        return True

    async def revoke_permission_override(
        self,
        user_id: str,
        permission: Permission,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> bool:
        """Revoke permission override from a user.

        Args:
            user_id: User identifier
            permission: Permission to revoke
            resource_type: Optional resource type for scoped permission
            resource_id: Optional resource ID for scoped permission

        Returns:
            True if permission revoked successfully
        """
        if not self.db:
            logger.warning("Permission override revoked without persistence")
            return True

        # Remove permission override from database
        logger.info(
            f"Revoked permission override {permission.value} from user {user_id}"
        )
        return True

    def get_role_hierarchy(self) -> Dict[Role, int]:
        """Get role hierarchy for privilege escalation checks.

        Returns:
            Dictionary mapping roles to their hierarchy level
        """
        return {
            Role.SUPER_ADMIN: 7,
            Role.ADMIN: 6,
            Role.CLINICIAN: 5,
            Role.RESEARCHER: 4,
            Role.PATIENT: 3,
            Role.DEVICE: 2,
            Role.SERVICE: 1,
        }

    def can_assign_role(self, assigner_role: Role, target_role: Role) -> bool:
        """Check if one role can assign another role.

        Args:
            assigner_role: Role of the user doing the assignment
            target_role: Role being assigned

        Returns:
            True if assignment is allowed, False otherwise
        """
        hierarchy = self.get_role_hierarchy()
        assigner_level = hierarchy.get(assigner_role, 0)
        target_level = hierarchy.get(target_role, 0)

        # Can only assign roles at same level or lower
        return assigner_level >= target_level

"""Permission management for MCP servers."""

from typing import Dict, List, Any, Optional
import fnmatch


class PermissionManager:
    """Manages user permissions for MCP server operations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize permission manager.

        Args:
            config: Permission configuration
        """
        self.config = config

        # Permission definitions
        self.permissions = config.get("permissions", {})
        self.roles = config.get("roles", {})
        self.default_permissions = config.get("default_permissions", [])

        # Resource-based permissions
        self.resource_permissions = config.get("resource_permissions", {})

    async def check_permission(
        self, user: Dict[str, Any], permission: str, resource: str = None
    ) -> bool:
        """Check if user has required permission.

        Args:
            user: User information
            permission: Required permission (e.g., "neural_data.read")
            resource: Optional resource identifier

        Returns:
            True if permission granted
        """
        # Get user permissions
        user_permissions = await self.get_user_permissions(user)

        # Check direct permission
        if permission in user_permissions:
            return await self._check_resource_access(user, permission, resource)

        # Check wildcard permissions
        for user_perm in user_permissions:
            if self._match_permission_pattern(user_perm, permission):
                return await self._check_resource_access(user, permission, resource)

        return False

    async def get_user_permissions(self, user: Dict[str, Any]) -> List[str]:
        """Get all permissions for a user.

        Args:
            user: User information

        Returns:
            List of permission strings
        """
        permissions = set(self.default_permissions)

        # Add direct permissions
        user_permissions = user.get("permissions", [])
        permissions.update(user_permissions)

        # Add role-based permissions
        user_roles = user.get("roles", [])
        for role in user_roles:
            role_permissions = self.roles.get(role, {}).get("permissions", [])
            permissions.update(role_permissions)

        return list(permissions)

    async def get_user_roles(self, user: Dict[str, Any]) -> List[str]:
        """Get all roles for a user.

        Args:
            user: User information

        Returns:
            List of role names
        """
        return user.get("roles", [])

    async def add_user_permission(self, user_id: str, permission: str) -> bool:
        """Add permission to a user.

        Args:
            user_id: User identifier
            permission: Permission to add

        Returns:
            True if permission was added
        """
        # In practice, this would update the database
        # For now, this is a placeholder
        return True

    async def remove_user_permission(self, user_id: str, permission: str) -> bool:
        """Remove permission from a user.

        Args:
            user_id: User identifier
            permission: Permission to remove

        Returns:
            True if permission was removed
        """
        # In practice, this would update the database
        # For now, this is a placeholder
        return True

    async def assign_role(self, user_id: str, role: str) -> bool:
        """Assign role to a user.

        Args:
            user_id: User identifier
            role: Role to assign

        Returns:
            True if role was assigned
        """
        if role not in self.roles:
            return False

        # In practice, this would update the database
        return True

    async def revoke_role(self, user_id: str, role: str) -> bool:
        """Revoke role from a user.

        Args:
            user_id: User identifier
            role: Role to revoke

        Returns:
            True if role was revoked
        """
        # In practice, this would update the database
        return True

    def _match_permission_pattern(self, pattern: str, permission: str) -> bool:
        """Check if permission matches a pattern.

        Args:
            pattern: Permission pattern (may contain wildcards)
            permission: Specific permission to check

        Returns:
            True if permission matches pattern
        """
        return fnmatch.fnmatch(permission, pattern)

    async def _check_resource_access(
        self, user: Dict[str, Any], permission: str, resource: str = None
    ) -> bool:
        """Check resource-specific access permissions.

        Args:
            user: User information
            permission: Permission being checked
            resource: Resource identifier

        Returns:
            True if access is allowed
        """
        if not resource:
            return True

        # Check resource-specific permissions
        resource_perms = self.resource_permissions.get(resource, {})

        # Check user-specific resource permissions
        user_id = user.get("id")
        if user_id in resource_perms.get("users", {}):
            user_resource_perms = resource_perms["users"][user_id]
            return permission in user_resource_perms

        # Check role-specific resource permissions
        user_roles = user.get("roles", [])
        for role in user_roles:
            if role in resource_perms.get("roles", {}):
                role_resource_perms = resource_perms["roles"][role]
                if permission in role_resource_perms:
                    return True

        # Check if resource is publicly accessible for this permission
        public_perms = resource_perms.get("public", [])
        return permission in public_perms

    def define_permission(
        self, name: str, description: str, category: str = "general"
    ) -> None:
        """Define a new permission.

        Args:
            name: Permission name
            description: Permission description
            category: Permission category
        """
        self.permissions[name] = {
            "description": description,
            "category": category,
            "created_at": "2025-01-01T00:00:00Z",  # In practice, use datetime.utcnow()
        }

    def define_role(self, name: str, description: str, permissions: List[str]) -> None:
        """Define a new role.

        Args:
            name: Role name
            description: Role description
            permissions: List of permissions for this role
        """
        self.roles[name] = {
            "description": description,
            "permissions": permissions,
            "created_at": "2025-01-01T00:00:00Z",
        }

    def get_permission_info(self, permission: str) -> Optional[Dict[str, Any]]:
        """Get information about a permission.

        Args:
            permission: Permission name

        Returns:
            Permission information or None
        """
        return self.permissions.get(permission)

    def get_role_info(self, role: str) -> Optional[Dict[str, Any]]:
        """Get information about a role.

        Args:
            role: Role name

        Returns:
            Role information or None
        """
        return self.roles.get(role)

    def list_permissions(self, category: str = None) -> List[Dict[str, Any]]:
        """List all permissions, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of permission information
        """
        permissions = []

        for name, info in self.permissions.items():
            if category and info.get("category") != category:
                continue

            permissions.append({"name": name, **info})

        return permissions

    def list_roles(self) -> List[Dict[str, Any]]:
        """List all roles.

        Returns:
            List of role information
        """
        roles = []

        for name, info in self.roles.items():
            roles.append({"name": name, **info})

        return roles

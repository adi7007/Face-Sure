"""
Role-Based Access Control (RBAC) module.

Provides FastAPI dependency classes for enforcing role-level authorization
on API endpoints. Validates JWT role claims against required roles.
"""

from typing import Sequence
from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole


class RoleChecker:
    """
    FastAPI dependency that validates the current user has one of the required roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
        async def admin_endpoint(): ...

    Or as a parameter dependency:
        async def endpoint(user: User = Depends(require_admin)): ...
    """

    def __init__(self, allowed_roles: Sequence[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends()) -> User:
        from app.core.security import get_current_user
        # Re-resolve through get_current_user since Depends() alone won't chain
        # This is handled by the shortcut functions below instead
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {[r.value for r in self.allowed_roles]}. "
                       f"Your role: {current_user.role.value}",
            )
        return current_user


async def require_admin(current_user: User = Depends()) -> User:
    """Dependency: requires ADMIN role."""
    from app.core.security import get_current_user as _get_user
    user = await _get_user()
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Admin access required. Your role: {user.role.value}",
        )
    return user


async def require_instructor_or_above(current_user: User = Depends()) -> User:
    """Dependency: requires ADMIN or INSTRUCTOR role."""
    from app.core.security import get_current_user as _get_user
    user = await _get_user()
    if user.role not in (UserRole.ADMIN, UserRole.INSTRUCTOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Instructor or Admin access required. Your role: {user.role.value}",
        )
    return user


async def require_any_authenticated(current_user: User = Depends()) -> User:
    """Dependency: requires any authenticated user (any role)."""
    from app.core.security import get_current_user as _get_user
    return await _get_user()

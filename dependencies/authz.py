from dependencies.authn import authenticated_user
from fastapi import Depends, HTTPException, status
from typing import Annotated, List
from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    ENTERPRISE = "enterprise"
    CUSTOMER = "customer"


def has_roles(roles: List[UserRole]):
    def check_role(user: Annotated[dict, Depends(authenticated_user)]):
        if user.get("role") not in [role.value for role in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied!",
            )
        return user

    return check_role

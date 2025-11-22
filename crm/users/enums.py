from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


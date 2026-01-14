from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

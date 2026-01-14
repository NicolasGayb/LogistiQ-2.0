from sqlalchemy.orm import Session

from app.models.user import User
from app.models.enum import UserRole
from app.core.security import hash_password

def create_system_admin(
    db: Session,
    name: str,
    email: str,
    password: str
):
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.SYSTEM_ADMIN
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
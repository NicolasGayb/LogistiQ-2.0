from datetime import timedelta, datetime, timezone
from typing import Optional
from uuid import UUID

from jose import jwt
from passlib.context import CryptContext

from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------
# Senhas
# -------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


# -------------------------
# Tokens JWT
# -------------------------
def create_access_token(
    *,
    subject: UUID,
    role: str,
    company_id: Optional[UUID],
    expires_delta: Optional[timedelta] = None
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(subject),              # ✅ sempre string
        "role": role,
        "company_id": str(company_id) if company_id else None,
        "exp": expire,
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
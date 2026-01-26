# Dependências
from datetime import timedelta, datetime, timezone
from typing import Optional
from uuid import UUID
from jose import jwt
from passlib.context import CryptContext

# Configurações
from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRE_MINUTES,
)

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------
# Senhas
# -------------------------
def hash_password(password: str) -> str:
    '''
    Gera um hash seguro para a senha fornecida.
    
    :param password: Senha em texto simples.
    :return: Hash da senha.
    '''
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    '''
    Verifica se a senha fornecida corresponde ao hash armazenado.

    :param password: Senha em texto simples.
    :param hashed_password: Hash da senha armazenada.
    :return: True se a senha corresponder ao hash, False caso contrário.
    '''
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
    '''
    Gera um token de acesso JWT.

    :param subject: Identificador único do usuário (UUID).
    :param role: Papel ou função do usuário.
    :param company_id: Identificador único da empresa (UUID), se aplicável.
    :param expires_delta: Tempo opcional para expiração do token.
    :return: Token JWT como string.
    '''
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(subject),              # ✅ sempre string
        "role": role,
        "company_id": str(company_id) if company_id else None,
        "exp": expire.timestamp(),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
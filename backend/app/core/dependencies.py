# Importações de terceiros
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from uuid import UUID
from typing import List, Callable

# Importações locais
from app.core.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.database import get_db
from app.models.user import User
from app.models.enum import UserRole

# Definição do esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ---------------------------------------------------
# Dependências de autenticação e autorização
# ---------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependência para obter o usuário autenticado a partir do token JWT.
    
    Args:
        token (str, optional): Token JWT. Padrão é Depends(oauth2_scheme).
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
    Returns:
        User: Usuário autenticado.
    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("TOKEN RAW:", token)
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        print("PAYLOAD:", payload)

        user_id_raw = payload.get("sub")
        role = payload.get("role")
        company_id_raw = payload.get("company_id")

        if not user_id_raw or not role:
            raise credentials_exception

        user_id = UUID(user_id_raw)
        company_id = UUID(company_id_raw) if company_id_raw not in (None, "") else None

        # SYSTEM_ADMIN pode não ter company
        if role != UserRole.SYSTEM_ADMIN.value and not company_id:
            raise credentials_exception

    except (JWTError, ValueError):
        raise credentials_exception

    query = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    )

    if role != UserRole.SYSTEM_ADMIN.value:
        query = query.filter(User.company_id == company_id)

    user = query.first()

    if not user:
        raise credentials_exception

    return user

# ---------------------------------------------------
# Dependências de autorização por papéis
# ---------------------------------------------------
def require_roles(roles: List[UserRole]) -> Callable:
    """
    Dependência para verificar se o usuário possui um dos papéis permitidos.

    Args:
        roles (List[UserRole]): Lista de papéis permitidos.
    Returns:
        Callable: Função de dependência que verifica o papel do usuário.
    Raises:
        HTTPException: Se o usuário não possuir um dos papéis permitidos.
    """

    allowed_roles = {role.value for role in roles}

    def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user

    return role_checker

# ---------------------------------------------------
# Dependência específica para ADMIN ou MANAGER
# ---------------------------------------------------
def check_admin_or_manager(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependência para verificar se o usuário é ADMIN ou MANAGER.
    Args:
        current_user (User, optional): Usuário autenticado. Padrão é Depends(get_current_user).
    Returns:
        User: Usuário autenticado se for ADMIN ou MANAGER.
    Raises:
        HTTPException: Se o usuário não for ADMIN ou MANAGER.
    """
    if current_user.role not in {UserRole.ADMIN.value, UserRole.MANAGER.value}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return current_user
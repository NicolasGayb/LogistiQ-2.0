# Importações externas
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importações internas
from app.database import get_db
from app.schemas.auth import SystemAdminCreate
from app.services.system_admin_service import create_system_admin
from app.repositories.user_repository import get_user_by_email

router = APIRouter(prefix="/system-admins", tags=["System Admins"])

# ------------------------------------------
# POST System Admin
# ------------------------------------------
@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_system_admin_endpoint(
    payload: SystemAdminCreate,
    db: Session = Depends(get_db),
):
    '''Cria um novo administrador do sistema.
    
    Args:
        payload (SystemAdminCreate): Dados do administrador a ser criado.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
    Returns:
        dict: Dados do administrador criado.
    Raises:
        HTTPException: Se o email já estiver cadastrado.
    '''
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado"
        )

    user = create_system_admin(
        db=db,
        name=payload.name,
        email=payload.email,
        password=payload.password
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
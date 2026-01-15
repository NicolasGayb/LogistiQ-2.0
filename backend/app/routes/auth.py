from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, NotNullViolation
from app.database import get_db
from app.models import User
from app.schemas.auth import ForgotPasswordRequest, RegisterRequest, ResetPasswordRequest, TokenResponse, UserMeResponse
from app.core.security import create_access_token, hash_password, verify_password
from app.core.dependencies import get_current_user, require_roles
from app.models.enum import UserRole
from app.models.company import Company
import secrets

router = APIRouter(prefix="/auth", tags=["Auth"])

# -----------------------
# Informações do Usuário Autenticado
# -----------------------
@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retorna as informações do usuário autenticado.

    Args:
        current_user (User, optional): Usuário autenticado. Padrão é Depends(get_current_user).
    Returns:
        UserMeResponse: Informações do usuário autenticado.
    Raises:
        HTTPException: Se o usuário não estiver autenticado.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return{
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "company_id": current_user.company_id,
        "company_name": current_user.company.name if current_user.company else None,
        "is_active": current_user.is_active,
    }


# -----------------------
# Login
# -----------------------
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token de acesso.
    
    Args:
        form_data (OAuth2PasswordRequestForm, optional): Dados do formulário de login. Padrão é Depends().
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
    Returns:
        TokenResponse: Token de acesso do usuário autenticado.
    Raises:
        HTTPException: Se as credenciais forem inválidas.
    """
    user = (
        db.query(User)
        .filter(User.email == form_data.username, User.is_active == True)
        .first()
    )

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(
        subject=user.id,
        role=user.role,
        company_id=user.company_id
    )

    return TokenResponse(access_token=token, token_type="bearer")

# -----------------------
# Registro de Usuário
# -----------------------
@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN])
    )
):
    # Email duplicado
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Resolver empresa
    company_id = None
    company = None

    if data.role != UserRole.SYSTEM_ADMIN:
        if not data.company_cnpj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company CNPJ is required for this role"
            )

        company = db.query(Company).filter(
            Company.cnpj == data.company_cnpj
        ).first()

        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company not found for provided CNPJ"
            )

        company_id = company.id

    # Autorização por role
    match current_user.role:
        case UserRole.SYSTEM_ADMIN:
            # SYSTEM_ADMIN pode tudo
            pass

        case UserRole.ADMIN:
            # ADMIN não pode criar SYSTEM_ADMIN
            if data.role == UserRole.SYSTEM_ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="ADMIN cannot create SYSTEM_ADMIN users"
                )

            # ADMIN só pode cadastrar usuários da própria empresa
            if company_id != current_user.company_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only register users for your own company"
                )

        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

    # Regra: apenas 1 ADMIN por empresa
    if data.role == UserRole.ADMIN:
        existing_admin = db.query(User).filter(
            User.company_id == company_id,
            User.role == UserRole.ADMIN
        ).first()

        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An ADMIN user already exists for this company"
            )

    # Criar usuário
    try:
        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
            company_id=company_id,
            is_active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error"
        )

    # Token
    token = create_access_token(
        subject=str(user.id),
        role=user.role,
        company_id=user.company_id
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )


# -----------------------
# Esqueci minha senha
# -----------------------
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Inicia o processo de recuperação de senha para um usuário.

    Args:
        data (ForgotPasswordRequest): Dados do pedido de recuperação de senha.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
    Returns:
        dict: Mensagem indicando que o token de redefinição foi gerado.
    Raises:
        HTTPException: Se o usuário não for encontrado.
    """

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="If the user exists, a password reset email has been sent."
        )
    
    token = secrets.token_urlsafe(32)

    user.reset_password_token = token
    user.reset_password_token_expires_at = datetime.utcnow() + timedelta(hours=1)
    
    db.commit()

    return{
        "message": "Redefinition token generated. (In a real application, an email would be sent to the user with this token.)",
        "reset_token": token
    }

# -----------------------
# Redefinir senha
# -----------------------
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.reset_password_token == data.token
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido"
        )

    if not user.reset_password_token_expires_at or user.reset_password_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado"
        )

    user.hashed_password = hash_password(data.new_password)
    user.reset_password_token = None
    user.reset_password_token_expires_at = None

    db.commit()

    return {"message": "Senha redefinida com sucesso"}
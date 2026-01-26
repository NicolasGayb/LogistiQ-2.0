# Importações padrão
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Importações locais
from app.database import get_db
from app.models import User
from app.schemas.auth import ForgotPasswordRequest, RegisterRequest, ResetPasswordRequest, TokenResponse, UserMeResponse
from app.core.security import create_access_token, hash_password, verify_password
from app.core.dependencies import get_current_user, require_roles
from app.models.enum import UserRole
from app.models.company import Company

# Definição do roteador
router = APIRouter(prefix="/auth", tags=["Auth"])

# -----------------------
# Info: Usuário Autenticado
# -----------------------
@router.get(
        "/me",
        summary="Usuário autenticado",
        description="Retorna as informações do usuário com base no token de autenticação fornecido.\n\n"
        "O usuário pode ou não estar associado a uma empresa, dependendo do seu papel no sistema.", 
        response_model=UserMeResponse,
        responses={
            200: {
                "description": "Informações do usuário autenticado",
                "content": {
                    "application/json": {
                        "examples": {
                            "com_empresa": {
                                "summary": "Usuário associado a uma empresa",
                                "value": {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "name": "Marie Doe",
                                    "email": "marie.doe@example.com",
                                    "role": "USER",
                                    "company_id": "123e4567-e89b-12d3-a456-426614174001",
                                    "company_name": "LogistiQ Corp",
                                    "is_active": True
                                }
                            },
                            "sem_empresa": {
                                "summary": "Usuário não associado a uma empresa",
                                "value": {
                                    "id": "223e4567-e89b-12d3-a456-426614174000",
                                    "name": "Admin User",
                                    "email": "admin.user@example.com",
                                    "role": "ADMIN",
                                    "company_id": None,
                                    "company_name": None,
                                    "is_active": True
                                }
                            }
                        }
                    }
                }
            },
            401: {
                "description": "Usuário não autenticado",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Not authenticated"
                        }
                    }
                }
            }
        })
def get_me(current_user: User = Depends(get_current_user)):

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
@router.post(
        "/login",
        summary="Autenticação do usuário",
        description="Realiza login e retorna um token JWT para autenticação nas demais rotas.",
        responses={
            401: {
                "description": "Credenciais inválidas",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Invalid email or password"
                        }
                    }
                }
            }
        },
        response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    summary="Registro de novo usuário",
    description="Registra um novo usuário no sistema. Apenas usuários com papéis SYSTEM_ADMIN ou ADMIN podem registrar novos usuários.",
    responses={
        201: {
            "description": "Usuário registrado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        400: {
            "description": "Erro de validação",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Email already registered"
                    }
                }
            }
        },
        403: {
            "description": "Permissão negada",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "You do not have permission to perform this action"
                    }
                }
            }
        }
    },
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
@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Esqueci minha senha",
    description="Gera um token de redefinição de senha para o usuário com o email fornecido.",
    responses={
        200: {
            "description": "Token de redefinição gerado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Redefinition token generated.",
                        "reset_token": "generated_reset_token_here"
                    }
                }
            }
        },
        404: {
            "description": "Usuário não encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "If the user exists, a password reset email has been sent."
                    }
                }
            }
        }
    }
    status_code=status.HTTP_200_OK,
    response_model=dict
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="If the user exists, a password reset email has been sent."
        )
    
    token = secrets.token_urlsafe(32)

    user.reset_password_token = token
    user.reset_password_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    db.commit()

    return{
        "message": "Redefinition token generated.",
        "reset_token": token
    }

# -----------------------
# Redefinição de senha
# -----------------------
@router.post(
        "/reset-password", 
        status_code=status.HTTP_200_OK,
        summary="Redefinição de senha",
        description="Redefine a senha do usuário utilizando um token de redefinição válido.",
        responses={
            400: {
                "description": "Token inválido ou expirado",
                "content": {
                    "application/json": {
                        "examples": {
                            "invalid_token": {
                                "summary": "Token inválido",
                                "value": {
                                    "detail": "Token inválido"
                                }
                            },
                            "expired_token": {
                                "summary": "Token expirado",
                                "value": {
                                    "detail": "Token expirado"
                                }
                            }
                        }
                    }
                }
            },
            200: {
                "description": "Senha redefinida com sucesso",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Senha redefinida com sucesso"
                        }
                    }
                }
            }
        })
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

    if not user.reset_password_token_expires_at or user.reset_password_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado"
        )

    user.hashed_password = hash_password(data.new_password)
    user.reset_password_token = None
    user.reset_password_token_expires_at = None

    db.commit()

    return {"message": "Senha redefinida com sucesso"}
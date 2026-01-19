import email
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from httpx import request
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import require_roles
from app.models.enum import UserRole
from app.models import User
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserRegisterWithToken, UserResponse, UserUpdate
from app.models.company import Company

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRole.SYSTEM_ADMIN, 
            UserRole.ADMIN, 
            UserRole.MANAGER]
        )
    )
):
    
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return db.query(User).all()
    
    if current_user.role == UserRole.ADMIN:
        return db.query(User).filter(
            User.company_id == current_user.company_id
        ).all() 
    
    if current_user.role == UserRole.MANAGER:
        return db.query(User).filter(
            User.company_id == current_user.company_id,
            User.role != UserRole.ADMIN
        ).all()

@router.post("/auto-create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def auto_create_user(
    data: UserRegisterWithToken,
    db: Session = Depends(get_db),
):
    # Confere se senhas coincidem
    if data.password != data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senhas não coincidem")

    # Checa email duplicado
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")

    # Verifica token da empresa
    company = db.query(Company).filter(Company.token == data.token).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token inválido. Entre em contato com o admin da empresa.")
    
    # Cria usuário com role USER
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.USER,
        company_id=company.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    message = f"Usuário {new_user.email} criado com sucesso na empresa {company.name}."
    print(message)

    return new_user

@router.post("/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN]))
):
    # ADMIN só pode criar usuários da própria empresa
    if current_user.role == UserRole.ADMIN:
        if data.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to create user for this company")
        if data.role != UserRole.USER:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="ADMIN só pode criar usuários USER")

    # Checa email duplicado
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")

    # Cria usuário
    hashed_password = hash_password(data.password)
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed_password,
        role=data.role,
        company_id=data.company_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.put("/update-user/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRole.SYSTEM_ADMIN, 
            UserRole.ADMIN, 
            UserRole.MANAGER]
        )
    )
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if current_user.role == UserRole.ADMIN:
        if user.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
        
    if data.name:
        user.name = data.name
    if data.role:
        user.role = data.role

    db.commit()
    db.refresh(user)
    return user

@router.delete("/delete-user/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRole.SYSTEM_ADMIN]
        )
    )
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    return f"User with ID {user_id} has been deleted."

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRole.SYSTEM_ADMIN, 
            UserRole.ADMIN, 
            UserRole.MANAGER]
        )
    )
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if current_user.role == UserRole.ADMIN:
        if user.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
    
    if current_user.role == UserRole.MANAGER:
        if user.company_id != current_user.company_id or user.role == UserRole.ADMIN:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
        
    return user
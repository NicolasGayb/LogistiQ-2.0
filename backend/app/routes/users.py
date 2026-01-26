# Importações externas
import email
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importações internas
from app.database import get_db
from app.core.dependencies import require_roles
from app.models.enum import UserRole
from app.models import User
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserRegisterWithToken, UserResponse, UserUpdate
from app.models.company import Company

router = APIRouter(prefix="/users", tags=["Users"])

# ------------------------------------------
# GET Users
# ------------------------------------------
@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN, UserRole.MANAGER])
    )
):
    '''Lista usuários com base na role do usuário atual.
    
    Args:
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(require_roles(...)).
    Returns:
        list[User]: Lista de usuários conforme a role do usuário atual.
    '''
    print(f"Listing users for {current_user.email} with role {current_user.role}")
    print(f"Current user's company ID: {current_user.company_id}")
    print(f"User roles: {[role.value for role in UserRole]}")

    total_users = db.query(User).count()
    print(f"Total users in database: {total_users}")
    
    if current_user.role == UserRole.SYSTEM_ADMIN:
        print("SYSTEM_ADMIN access: returning all users")
        return db.query(User).all()
    
    if current_user.role == UserRole.ADMIN:
        print("ADMIN access: returning users for company ID", current_user.company_id)
        return db.query(User).filter(
            User.company_id == current_user.company_id
        ).all() 
    
    if current_user.role == UserRole.MANAGER:
        print("MANAGER access: returning non-ADMIN users for company ID", current_user.company_id)
        return db.query(User).filter(
            User.company_id == current_user.company_id,
            User.role != UserRole.ADMIN
        ).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN, UserRole.MANAGER])
    )
):
    '''Obtém detalhes de um usuário específico com base na role do usuário atual.
    
    Args:
        user_id (UUID): ID do usuário a ser obtido.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(require_roles(...)).
    Returns:
        User: Detalhes do usuário solicitado.
    Raises:
        HTTPException: Se o usuário não for encontrado ou se o usuário atual não tiver permissão para visualizar o usuário solicitado.
    '''
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

# ------------------------------------------
# POST Users
# ------------------------------------------
@router.post("/auto-create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def auto_create_user(
    data: UserRegisterWithToken,
    db: Session = Depends(get_db),
):
    '''Cria um novo usuário associado a uma empresa usando um token de empresa.
    
    Endpoint público para auto-registro de usuários.
    Args:
        data (UserRegisterWithToken): Dados do usuário a ser criado, incluindo token da empresa
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
    Returns:
        User: Dados do usuário criado.
    Raises:
        HTTPException: Se as senhas não coincidirem, email já estiver cadastrado ou token for inválido.
    '''
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
    '''Cria um novo usuário com base na role do usuário atual.

    Apenas SYSTEM_ADMIN e ADMIN podem acessar este endpoint.
    Args:
        data (UserCreate): Dados do usuário a ser criado.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(require_roles(...)).
    Returns:
        User: Dados do usuário criado.
    Raises:
        HTTPException: Se o email já estiver cadastrado ou se o ADMIN tentar criar um usuário fora de sua empresa ou com role inválida.
    '''
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

# ------------------------------------------
# PUT Users
# ------------------------------------------
@router.put("/update-user/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN, UserRole.MANAGER])
    )
):
    '''Atualiza os detalhes de um usuário específico com base na role do usuário atual.
    
    Args:
        user_id (UUID): ID do usuário a ser atualizado.
        data (UserUpdate): Dados para atualizar o usuário.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(require_roles(...)).
    Returns:
        User: Dados do usuário atualizado.
    Raises: 
        HTTPException: Se o usuário não for encontrado ou se o usuário atual não tiver permissão para atualizar o usuário solicitado.
    '''
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

# ------------------------------------------
# DELETE Users
# ------------------------------------------
@router.delete("/delete-user/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.SYSTEM_ADMIN)
    )
):
    '''Deleta um usuário específico. Apenas SYSTEM_ADMIN pode acessar este endpoint.
    
    Args:
        user_id (UUID): ID do usuário a ser deletado.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(require_roles(...)).
    Returns:
        str: Mensagem de confirmação da deleção.
    Raises:
        HTTPException: Se o usuário não for encontrado.
    '''
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    return f"User with ID {user_id} has been deleted."

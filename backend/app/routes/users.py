# Importações externas
import email
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Importações internas
from app.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.enum import UserRole
from app.models import User
from app.core.security import hash_password, verify_password
from app.schemas.user import UserChangePassword, UserCreate, UserRegisterWithToken, UserResponse, UserUpdate, UserUpdateSettings
from app.models.company import Company
from app.schemas.company import CompanySettingsUpdate

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
    
    if current_user.role == UserRole.ADMIN or current_user.role == UserRole.MANAGER:
        if user.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
        
    if data.name:
        user.name = data.name
    if data.role:
        user.role = data.role
    if data.email:
        user.email = data.email
    if data.password:
        user.password_hash = hash_password(data.password)

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
        require_roles([UserRole.SYSTEM_ADMIN])
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
    
    try:
        db.delete(user)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        #Retorna erro 409 de conflito
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Cannot delete user due to existing references in the system.")

    return f"User with ID {user_id} has been deleted."

# ------------------------------------------
# PATCH Users
# ------------------------------------------
@router.patch("/change-password/{user_id}", response_model=str)
def change_user_password(
    user_id: UUID,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN, UserRole.MANAGER, UserRole.USER])
    )
):
    '''Altera a senha de um usuário específico.
    
    Args:
        user_id (UUID): ID do usuário cuja senha será alterada.
        new_password (str): Nova senha para o usuário.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(require_roles(...)).
    Returns:
        str: Mensagem de confirmação da alteração da senha.
    Raises:
        HTTPException: Se o usuário não for encontrado ou se o usuário atual não tiver permissão para alterar a senha do usuário solicitado.
    '''
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if current_user.role != UserRole.SYSTEM_ADMIN:
        if user.id != current_user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to change this user's password")
        
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)

    return f"Password for user with ID {user_id} has been changed."

@router.patch("/toggle-user/{user_id}", response_model=str)
def toggle_user_active_status(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN])
    )
):
    '''Ativa ou desativa um usuário específico com base na role do usuário atual.
    
    Args:
        user_id (UUID): ID do usuário a ser ativado/desativado.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(require_roles(...)).
    Returns:
        str: Mensagem de confirmação da alteração do status do usuário.
    Raises:
        HTTPException: Se o usuário não for encontrado ou se o usuário atual não tiver permissão para alterar o status do usuário solicitado.
    '''
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if current_user.role == UserRole.ADMIN:
        if user.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to toggle this user")
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    status_str = "activated" if user.is_active else "deactivated"
    return f"User with ID {user_id} has been {status_str}."

# ----------------------------------------------------------------------
# Contexto: Eu configurando meu perfil
# ----------------------------------------------------------------------
# Rota para atualizar perfil do usuário logado e preferências
@router.put("/me/profile", response_model=UserResponse)
def update_my_profile(
    data: UserUpdateSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Usa a dependência que pega o token
):
    """Atualiza perfil e preferências do usuário logado.
    
    Args:
        data (UserUpdateSettings): Dados para atualizar o perfil do usuário.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(get_current_user).
    Returns:
        User: Dados do usuário atualizado.
    """
    
    if data.name: current_user.name = data.name
    if data.email: current_user.email = data.email
    
    # Preferências
    if data.notification_stock_alert is not None:
        current_user.notification_stock_alert = data.notification_stock_alert
    if data.notification_weekly_summary is not None:
        current_user.notification_weekly_summary = data.notification_weekly_summary
    if data.theme_preference:
        current_user.theme_preference = data.theme_preference

    db.commit()
    db.refresh(current_user)
    return current_user

# Rota para troca de senha do usuário logado (exige senha atual)
@router.put("/me/change-password")
def change_my_password(
    data: UserChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Troca de senha segura para o usuário logado (exige senha atual).
    
    Args:
        data (UserChangePassword): Dados para troca de senha.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(get_current_user).
    Returns:
        dict: Mensagem de sucesso.
    """
    
    # 1. Verifica se a senha atual bate com o hash no banco
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="A senha atual está incorreta.")

    # 2. Verifica confirmação
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="A nova senha e a confirmação não coincidem.")

    # 3. Salva a nova senha
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    db.refresh(current_user)
    return {"message": f"Senha do usuário {current_user.name} alterada com sucesso."}

# Rota para atualizar configurações da empresa do usuário logado (apenas SYSTEM_ADMIN, ADMIN e MANAGER)
@router.put("/me/company")
def update_my_company_settings(
    data: CompanySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN, UserRole.MANAGER]))
):
    """Atualiza configurações da empresa do usuário logado.
    
    Args:
        data (CompanySettingsUpdate): Dados para atualizar as configurações da empresa.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
        current_user (User, optional): Usuário autenticado. Padrão é Depends(require_roles(...)).
    Returns:
        dict: Mensagem de sucesso.
    """
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    if data.name: company.name = data.name
    if data.stock_alert_limit is not None: 
        company.stock_alert_limit = data.stock_alert_limit

    db.commit()
    db.refresh(company)

    return {"message": f"Configurações da empresa {company.name} atualizadas com sucesso."}
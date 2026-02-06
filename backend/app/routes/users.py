# Importações externas
import os
import email
import shutil
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

# Importações internas
from app.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.enum import UserRole
from app.models import User
from app.core.security import hash_password, verify_password
from app.schemas.user import UserChangePassword, UserCreate, UserRegisterWithToken, UserResponse, UserUpdate
from app.models.company import Company
from app.schemas.company import CompanySettingsUpdate
from app.services.movement_service import MovementService, MovementEntityType, MovementType
from app.models.system_setting import SystemSetting

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
        list[UserResponse]: Lista de usuários conforme a role do usuário atual.
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
    
@router.get('/me', response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    '''Obtém o perfil do usuário autenticado.
    
    Args:
        current_user (User, optional): Usuário autenticado. Padrão é Depends(get_current_user).
    Returns:
        User: Detalhes do usuário autenticado.
    '''
    return current_user

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
    settings = db.query(SystemSetting).first()

    if settings and settings.allow_registrations == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O registro de novos usuários está fechado no momento. Por favor, entre em contato com o administrador do sistema."
        )

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

    # Movimentação
    try:
        MovementService.create_manual(
            db=db,
            entity_id=new_user.id,
            entity_type=MovementEntityType.USER,
            company_id=new_user.company_id,
            movement_type=MovementType.CREATION,
            description=f"Usuário {new_user.email} criado automaticamente",
            created_by=new_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating movement for auto user creation: {str(e)}"
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
    settings = db.query(SystemSetting).first()

    if settings and settings.allow_registrations == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A criação de novos usuários está fechada no momento. Entre em contato com o administrador do sistema."
        )

    # ADMIN só pode criar usuários da própria empresa
    if current_user.role == UserRole.ADMIN:
        if data.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Você não possui permissão para criar usuários fora da sua empresa.")
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

    # Movimentação
    try:
        MovementService.create_manual(
            db=db,
            entity_id=new_user.id,
            entity_type=MovementEntityType.USER,
            company_id=new_user.company_id,
            movement_type=MovementType.CREATION,
            description=f"Usuário {new_user.email} criado por {current_user.email}",
            created_by=current_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating movement for user creation: {str(e)}"
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
    Não é possível ativar/desativar usuários por este endpoint, apenas atualizar nome, email, role e senha.
    
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

    # Movimentação
    try:
        MovementService.create_manual(
            db=db,
            entity_id=user.id,
            entity_type=MovementEntityType.USER,
            company_id=user.company_id,
            movement_type=MovementType.UPDATED,
            description=f"Usuário {user.email} atualizado por {current_user.email}",
            created_by=current_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating movement for user update: {str(e)}"
        )
    
    # Salvar alterações
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
    settings = db.query(SystemSetting).first()

    if settings and settings.allow_registrations == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A deleção de usuários está fechada no momento. Entre em contato com o administrador do sistema."
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        db.delete(user)
        # Movimentação
        MovementService.create_manual(
            db=db,
            entity_id=user.id,
            entity_type=MovementEntityType.USER,
            company_id=user.company_id,
            movement_type=MovementType.DELETED,
            description=f"Usuário {user.email} deletado por {current_user.email}",
            created_by=current_user.id,
        )
        db.commit()
    except IntegrityError as e:
        db.rollback()
        #Retorna erro 409 de conflito
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Cannot delete user due to existing references in the system.")

    return f"User with ID {user_id} has been deleted."

# ------------------------------------------
# PATCH Users
# ------------------------------------------
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
    settings = db.query(SystemSetting).first()
    
    if settings and settings.allow_registrations == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A ativação de usuários está fechada no momento. Entre em contato com o administrador do sistema."
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    if current_user.role == UserRole.ADMIN:
        if user.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Não autorizado a alterar este usuário")
    
    user.is_active = not user.is_active

    # Movimentação
    try:
        MovementService.create_manual(
            db=db,
            entity_id=user.id,
            entity_type=MovementEntityType.USER,
            company_id=user.company_id,
            movement_type=MovementType.STATUS_CHANGED,
            description=f"Usuário {user.email} {'ativado' if user.is_active else 'desativado'} por {current_user.email}",
            created_by=current_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar movimentação para alteração do status do usuário: {str(e)}"
        )

    db.commit()
    db.refresh(user)

    status_str = "ativado" if user.is_active else "desativado"
    return f"Usuário com ID {user_id} foi {status_str}."

# ----------------------------------------------------------------------
# Contexto: Eu configurando meu perfil
# ----------------------------------------------------------------------
# Rota para atualizar perfil do usuário logado e preferências
@router.put("/me/profile")
def update_my_profile(
    # Form(...) para campos de texto e File(...) para o arquivo
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    notification_stock_alert: str = Form("true"), # Recebe como string "true"/"false" do FormData
    notification_weekly_summary: str = Form("true"),
    theme_preference: str = Form("auto"),
    avatar: Optional[UploadFile] = File(None), # O Arquivo
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Atualiza dados de texto
    if name: current_user.name = name
    if email: current_user.email = email
    
    # Converte strings "true"/"false" para boolean
    if notification_stock_alert is not None:
        current_user.notification_stock_alert = (notification_stock_alert.lower() == 'true')
    
    if notification_weekly_summary is not None:
        current_user.notification_weekly_summary = (notification_weekly_summary.lower() == 'true')
        
    if theme_preference:
        current_user.theme_preference = theme_preference

    # 2. Processa o Arquivo (Upload)
    if avatar:
        # Lê o conteúdo do arquivo em bytes
        file_content = avatar.file.read()

        # Salva os dados binários e o content_type no banco
        current_user.profile_image = file_content
        current_user.content_type = avatar.content_type # ex: "image/png"

    # 3. Cria movimento de atualização de perfil
    try:
        MovementService.create_manual(
            db=db,
            entity_id=current_user.id,
            entity_type=MovementEntityType.USER,
            company_id=current_user.company_id,
            movement_type=MovementType.UPDATED,
            description=f"Perfil do usuário {current_user.email} atualizado",
            created_by=current_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar movimentação para atualização do perfil: {str(e)}"
        )

    db.commit()
    db.refresh(current_user)

    # Remove dados binários da imagem do objeto retornado para evitar sobrecarga
    current_user.profile_image = None

    # Adiciona a URL do avatar ao objeto retornado
    setattr(current_user, 'avatar_url', f'/users/{current_user.id}/avatar')

    return current_user

# Rota para obter a foto de perfil do usuário logado
@router.get("/{user_id}/avatar")
def get_user_avatar(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtém a foto de perfil do usuário especificado.
    
    Args:
        user_id (UUID): ID do usuário cuja foto de perfil será obtida.
        db (Session, optional): Sessão do banco de dados. Padrão é Depends(get_db).
    Returns:
        Response: Resposta contendo a imagem do avatar ou um erro 404 se não encontrado.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.profile_image:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")
    
    return Response(content=user.profile_image, media_type=user.content_type)

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

    # 4. Cria movimento de troca de senha
    try:
        MovementService.create_manual(
            db=db,
            entity_id=current_user.id,
            entity_type=MovementEntityType.USER,
            company_id=current_user.company_id,
            movement_type=MovementType.PASSWORD_CHANGE,
            description=f"Senha do usuário {current_user.email} alterada",
            created_by=current_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar movimentação para troca de senha: {str(e)}"
        )
    
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

    # Movimentação
    try:
        MovementService.create_manual(
            db=db,
            entity_id=company.id,
            entity_type=MovementEntityType.COMPANY,
            company_id=company.id,
            movement_type=MovementType.UPDATED,
            description=f"Configurações da empresa {company.name} atualizadas por {current_user.email}",
            created_by=current_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar movimentação para atualização das configurações da empresa: {str(e)}"
        )

    db.commit()
    db.refresh(company)

    return {"message": f"Configurações da empresa {company.name} atualizadas com sucesso."}

@router.get("/active/last-5-min", response_model=int)
def count_active_users_last_five_minutes(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles([UserRole.SYSTEM_ADMIN, UserRole.ADMIN])
    )
):
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)

    active_users_count = (
        db.query(User)
        .filter(User.is_active.is_(True))
        .filter(User.last_active_at != None)
        .filter(User.last_active_at >= cutoff_time)
        .count()
    )

    return active_users_count
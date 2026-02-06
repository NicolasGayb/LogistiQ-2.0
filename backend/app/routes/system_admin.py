# Importações externas
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, text


# Importações internas
from app.database import get_db
from app.schemas.auth import SystemAdminCreate
from app.models.system_setting import SystemSetting
from app.schemas.system_setting import SystemSettingOut, SystemSettingUpdate
from app.services.system_admin_service import create_system_admin
from app.repositories.user_repository import get_user_by_email
from app.core.dependencies import get_current_user, require_roles
from app.models.enum import UserRole, MovementType
from app.models.movement import Movement
from app.models.operation import Operation
from app.models.user import User
from app.routes.users import count_active_users_last_five_minutes

# Prefixo e Tags
router = APIRouter(prefix="/system-admins", tags=["System Admins"])

# ------------------------------------------
# GET Audit Logs (Alimenta a aba Auditoria)
# ------------------------------------------
@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    """
    Busca os últimos 50 movimentos do sistema para a tabela de Auditoria.
    Apenas SYSTEM_ADMIN pode acessar.
    """
    # Busca os 50 movimentos mais recentes
    # Usa joinedload para trazer o usuário que criou o movimento (se houver)
    movements = db.query(Movement)\
        .options(joinedload(Movement.updater))\
        .order_by(desc(Movement.created_at))\
        .limit(50)\
        .all()

    logs = []
    for mov in movements:
        # Define a cor do status baseado no tipo de movimento
        status_color = "warning" # Padrão
        if mov.type in [MovementType.CREATION, MovementType.INPUT]:
            status_color = "success"
        elif mov.type in [MovementType.DELETED, MovementType.OUTPUT]:
            status_color = "error"
        
        # Formata o nome do usuário ou "Sistema" se for nulo
        user_name = "Sistema"
        if mov.created_by and hasattr(mov, 'updater') and mov.updater:
             user_name = mov.updater.name

        logs.append({
            "id": str(mov.id),
            "action": f"{mov.type.value} - {mov.entity_type.value}", # Ex: "Criação - Produto"
            "user": user_name,
            "ip": mov.ip_address if hasattr(mov, 'ip_address') and mov.ip_address else "127.0.0.1",
            "date": mov.created_at.strftime("%d/%m/%Y %H:%M") if hasattr(mov.created_at, 'strftime') else str(mov.created_at),
            "status": status_color,
            "description": mov.description
        })

    return logs

# ------------------------------------------
# GET System Stats (Alimenta a aba Monitoramento)
# ------------------------------------------
@router.get("/stats")
def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    """
    Retorna métricas gerais do sistema baseadas nas Operações e Conexões.

    Apenas SYSTEM_ADMIN pode acessar.
    Returns:
        Dict[str, Any]: Dicionário com status do sistema e métricas.
    """
    
    # 1. Total de Operações
    total_ops = db.query(Operation).count()

    # 2. Operações Atrasadas
    # Verifica se a tabela já tem a coluna nova, senão retorna 0
    delayed_ops = 0

    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    
    active_connections = (
        db.query(User)
        .filter(User.is_active == True)
        .filter(User.last_active_at.is_not(None))
        .filter(User.last_active_at >= cutoff_time)
        .count()
    )
    
    try:
        # Busca operações com expected_delivery_date no passado e status diferente de DELIVERED
        delayed_ops = db.query(Operation).filter(
            Operation.expected_delivery_date < func.now(),
            Operation.status != "DELIVERED"
        ).count()
    except Exception:
        db.rollback()  # Em caso de erro (ex: coluna não existe), garante que a sessão está limpa

    # 3. Status do Banco de Dados (Simples verificação se query roda)
    db_status = "online"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Database connection error at {datetime.now()}: {e}")
        db_status = "offline"
        db.rollback()

    return {
        "api_status": "online",
        "db_status": db_status,
        "email_service": "online", # Mockado por enquanto (exige verificação SMTP)
        "version": "2.1.0",
        "metrics": {
            "total_operations": total_ops,
            "delayed_operations": delayed_ops,
            "active_connections": active_connections
        }
    }

# ------------------------------------------
# POST System Admin (Criação de Admin)
# ------------------------------------------
@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_system_admin_endpoint(
    payload: SystemAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    '''Cria um novo administrador do sistema.

    Apenas um SYSTEM_ADMIN pode criar outro.
    Args:
        payload (SystemAdminCreate): Dados para criação do admin.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado (deve ser SYSTEM_ADMIN).
    Returns:
        Dict[str, Any]: Dados do novo administrador criado.
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

# ------------------------------------------
# GET & PUT Settings (Configurações Reais)
# ------------------------------------------

@router.get("/settings", response_model=SystemSettingOut)
def get_system_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    """Retorna as configurações atuais. Cria o registro padrão se não existir."""
    settings = db.query(SystemSetting).first()
    
    if not settings:
        # Auto-initialize: Cria a configuração padrão na primeira vez
        settings = SystemSetting(
            maintenance_mode=False,
            allow_registrations=True,
            session_timeout=60
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
    return settings

@router.put("/settings", response_model=SystemSettingOut)
def update_system_settings(
    payload: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    """Atualiza as configurações globais."""
    settings = db.query(SystemSetting).first()
    
    # Se por algum motivo não existir (raro), cria
    if not settings:
        settings = SystemSetting()
        db.add(settings)

    # Atualiza os campos
    settings.maintenance_mode = payload.maintenance_mode
    settings.allow_registrations = payload.allow_registrations
    settings.session_timeout = payload.session_timeout
    settings.updated_by = current_user.id
    
    db.commit()
    db.refresh(settings)
    
    return settings
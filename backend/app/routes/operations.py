# Importações de terceiros
import datetime
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID

# Importação local
from app.database import get_db, Base
from app.core.dependencies import get_current_user
from app.models.operation import Operation
from app.schemas.operation import (
    OperationCreateSchema,
    OperationUpdateStatusSchema,
    OperationResponseSchema
)
from app.services.operation_service import OperationService
from app.domain.operation_validator import InvalidOperationTransition
from app.models.enum import OperationStatus


router = APIRouter(prefix="/operations", tags=["Operations"])

# ----------------------------------------------
# POST /operations
# ----------------------------------------------
@router.post("/", response_model=OperationResponseSchema)
def create_operation(
    data: OperationCreateSchema,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    '''Cria uma nova operação.
    
    - Gera uma nova operação com base nos dados fornecidos.
    - Associa a operação à empresa do usuário autenticado.
    
    Parâmetros:
    - `data`: Dados necessários para criar a operação.
    - `db`: Sessão do banco de dados.
    - `user`: Usuário autenticado.
    
    Retorna:
    - A operação criada.
    '''
    service = OperationService(db)
    return service.create(data, user)

# ----------------------------------------------
# GET /operations
# ----------------------------------------------
@router.get("/")
def list_operations(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    type: Optional[str] = None,
    partner_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Operation).options(joinedload(Operation.partner)) # Carrega o nome do parceiro

    # Aplicando Filtros Dinâmicos
    if status:
        query = query.filter(Operation.status == status)
    if type:
        query = query.filter(Operation.type == type)
    if partner_id:
        query = query.filter(Operation.partner_id == partner_id)
    if start_date:
        query = query.filter(Operation.created_at >= start_date)
    if end_date:
        query = query.filter(Operation.created_at <= end_date)

    # Ordenação: Mais recentes primeiro e Atrasados com prioridade
    operations = query.order_by(
        desc(Operation.expected_delivery_date)
    ).offset(skip).limit(limit).all()

    return operations

@router.get("/kpis")
def get_operation_kpis(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    '''Obtém KPIs relacionados às operações da empresa do usuário autenticado.
    
    Parâmetros:
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.
    
    Retorna:
    - KPIs calculados com base nas operações da empresa.'''
    today = date.today()

    final_statuses = [OperationStatus.DELIVERED, OperationStatus.CANCELED, OperationStatus.COMPLETED]
    
    # Total Pendente (Tudo que não foi finalizado ou cancelado)
    if current_user.role != "SYSTEM_ADMIN":
        pending = db.query(Operation).filter(
            Operation.company_id == current_user.company_id,
            Operation.status.notin_(final_statuses)
        ).count()
    else:
        pending = db.query(Operation).filter(
            Operation.status.notin_(final_statuses)
        ).count()

    # Atrasados (Não finalizado E Data Prevista < Hoje)
    if current_user.role != "SYSTEM_ADMIN":
        late = db.query(Operation).filter(
            Operation.company_id == current_user.company_id,
            Operation.status.notin_(final_statuses),
            Operation.expected_delivery_date < datetime.now()
        ).count()
    else:
        late = db.query(Operation).filter(
            Operation.status.notin_(final_statuses),
            Operation.expected_delivery_date < datetime.now()
        ).count()

    # Concluídos Hoje
    if current_user.role != "SYSTEM_ADMIN":
        completed_today = db.query(Operation).filter(
            Operation.company_id == current_user.company_id,
            Operation.status == OperationStatus.DELIVERED,
            func.date(Operation.updated_at) == today
        ).count()
    else:
        completed_today = db.query(Operation).filter(
            Operation.status == OperationStatus.DELIVERED,
            func.date(Operation.updated_at) == today
        ).count()

    return {
        "pending": pending,
        "late": late,
        "completed_today": completed_today
    }

@router.get("/{operation_id}", response_model=OperationResponseSchema)
def get_operation(
    operation_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    '''Obtém os detalhes de uma operação específica.
    
    Parâmetros:
    - `operation_id`: ID da operação a ser obtida.
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.
    Retorna:
    - Detalhes da operação solicitada.
    '''
    operation = (
        db.query(Operation)
        .filter(
            Operation.id == operation_id,
            Operation.company_id == current_user.company_id
        )
        .first()
    )

    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    return operation

# ----------------------------------------------
# PATCH /operations
# ----------------------------------------------
@router.patch("/{operation_id}/status", response_model=OperationResponseSchema)
def update_operation_status(
    operation_id: UUID,
    data: OperationUpdateStatusSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    '''Atualiza o status de uma operação específica.

    Parâmetros:
    - `operation_id`: ID da operação a ser atualizada.
    - `data`: Dados contendo o novo status.
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.
    
    Retorna:
    - A operação atualizada.
    '''
    operation = db.query(Operation).filter(Operation.id == operation_id)

    if current_user.role != "SYSTEM_ADMIN":
        operation = operation.filter(Operation.company_id == current_user.company_id)

    operation = operation.first()

    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    service = OperationService(db)
    try:
        return service.update_status(operation, data.status, current_user)
    except InvalidOperationTransition as e:
        raise HTTPException(status_code=400, detail=str(e))
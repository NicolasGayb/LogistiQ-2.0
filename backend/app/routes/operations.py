# Importações de terceiros
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
@router.get("/", response_model=list[OperationResponseSchema])
def list_operations(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    '''Lista todas as operações associadas à empresa do usuário autenticado.
    
    Parâmetros:
    - `db`: Sessão do banco de dados.
    - `user`: Usuário autenticado.
    Retorna:
    - Lista de operações.'''
    return (
        db.query(Operation)
        .filter(Operation.company_id == user.company_id)
        .all()
    )


@router.get("/{operation_id}", response_model=OperationResponseSchema)
def get_operation(
    operation_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    '''Obtém os detalhes de uma operação específica.
    
    Parâmetros:
    - `operation_id`: ID da operação a ser obtida.
    - `db`: Sessão do banco de dados.
    - `user`: Usuário autenticado.
    Retorna:
    - Detalhes da operação solicitada.
    '''
    operation = (
        db.query(Operation)
        .filter(
            Operation.id == operation_id,
            Operation.company_id == user.company_id
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
    user = Depends(get_current_user)
):
    '''Atualiza o status de uma operação específica.

    Parâmetros:
    - `operation_id`: ID da operação a ser atualizada.
    - `data`: Dados contendo o novo status.
    - `db`: Sessão do banco de dados.
    - `user`: Usuário autenticado.
    
    Retorna:
    - A operação atualizada.
    '''
    operation = (
        db.query(Operation)
        .filter(
            Operation.id == operation_id,
            Operation.company_id == user.company_id
        )
        .first()
    )

    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    service = OperationService(db)
    try:
        return service.update_status(operation, data.status, user)
    except InvalidOperationTransition as e:
        raise HTTPException(status_code=400, detail=str(e))
# Importações externas
from http.client import HTTPException
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

# Importações internas
from app.models.enum import (
    MovementType,
    MovementEntityType,
    OperationStatus,
)
from app.repositories.movement_repository import MovementRepository
from app.models.movement import Movement
from app.models.operation import Operation

# Serviço de Movimentações
class MovementService:
    ''' Serviço responsável por gerenciar as movimentações no sistema.
    
    Responsabilidades:
    - Registrar movimentações relacionadas a operações.
    - Validar regras de negócio associadas às movimentações.
    - Fornecer métodos para criação e consulta de movimentações.
    '''

    def __init__(self, db: Session):
        ''' Inicializa o serviço com a sessão do banco de dados. 
        
        :param db: Sessão do banco de dados.
        '''
        self.db = db

    @staticmethod
    def register_operation_created(
        db: Session,
        *,
        operation_id: UUID,
        company_id: UUID,
        created_by: UUID | None = None,
    ):
        ''' Registra a criação de uma nova operação. 
        
        :param db: Sessão do banco de dados.
        :param operation_id: ID da operação criada.
        :param company_id: ID da empresa associada.
        :param created_by: ID do usuário que criou a operação.
        :return: Instância da movimentação criada.
        '''
        # Cria a movimentação de operação criada
        return MovementRepository.create(
            db=db,
            company_id=company_id,
            entity_type=MovementEntityType.OPERATION,
            entity_id=operation_id,
            movement_type=MovementType.OPERATION_CREATED,
            description="Operação criada",
            created_by=created_by,
        )

    @staticmethod
    def register_status_change(
        db: Session,
        *,
        operation_id: UUID,
        company_id: UUID,
        previous_status: OperationStatus,
        new_status: OperationStatus,
        created_by: UUID | None = None,
    ):
        ''' Registra a alteração de status de uma operação. 
        
        :param db: Sessão do banco de dados.
        :param operation_id: ID da operação.
        :param company_id: ID da empresa associada.
        :param previous_status: Status anterior da operação.
        :param new_status: Novo status da operação.
        :param created_by: ID do usuário que realizou a alteração.
        :return: Instância da movimentação criada.
        '''
        # Cria a movimentação de alteração de status
        return MovementRepository.create(
            db=db,
            company_id=company_id,
            entity_type=MovementEntityType.OPERATION,
            entity_id=operation_id,
            movement_type=MovementType.STATUS_CHANGED,
            previous_status=previous_status,
            new_status=new_status,
            description=f"Status alterado de {previous_status} para {new_status}",
            created_by=created_by,
        )

    @staticmethod
    def register_event(
        db: Session,
        *,
        entity_type: MovementEntityType,
        entity_id: UUID,
        company_id: UUID,
        movement_type: MovementType,
        description: str,
        created_by: UUID | None = None,
    ):
        ''' Registra um evento genérico de movimentação. 
        
        :param db: Sessão do banco de dados.
        :param entity_type: Tipo da entidade associada à movimentação.
        :param entity_id: ID da entidade associada.
        :param company_id: ID da empresa associada.
        :param movement_type: Tipo da movimentação.
        :param description: Descrição da movimentação.
        :param created_by: ID do usuário que criou a movimentação.
        :return: Instância da movimentação criada.
        '''
        # Cria a movimentação genérica
        return MovementRepository.create(
            db=db,
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            movement_type=movement_type,
            description=description,
            created_by=created_by,
        )
    
    @staticmethod
    def _validate_entity_exists(
        db: Session,
        *,
        entity_id: UUID,
        entity_type: MovementEntityType,
        company_id: UUID
    ):
        ''' Valida se a entidade existe no banco de dados.
        
        :param db: Sessão do banco de dados.
        :param entity_id: ID da entidade.
        :param entity_type: Tipo da entidade.
        :param company_id: ID da empresa associada.
        :raises HTTPException: Se a entidade não for encontrada.
        '''
        # Validação para o tipo OPERATION
        if entity_type == MovementEntityType.OPERATION:
            exists = (
                db.query(Operation)
                .filter(
                    Operation.id == entity_id,
                    Operation.company_id == company_id
                )
                .first()
            )
            # Se a operação não existir, lança uma exceção
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Operation not found"
                )

    @staticmethod
    def create_manual(
        *,
        db: Session,
        entity_id: UUID,
        entity_type: MovementEntityType,
        company_id: UUID,
        movement_type: MovementType,
        description: str | None,
        created_by: UUID
    ):
        ''' Cria uma movimentação manualmente, validando a existência da entidade.

        :param db: Sessão do banco de dados.
        :param entity_id: ID da entidade associada.
        :param entity_type: Tipo da entidade associada.
        :param company_id: ID da empresa associada.
        :param movement_type: Tipo da movimentação.
        :param description: Descrição da movimentação.
        :param created_by: ID do usuário que criou a movimentação.
        :return: Instância da movimentação criada.
        '''
        # Regra de domínio - validação da existência da entidade
        MovementService._validate_entity_exists(
            db,
            entity_id=entity_id,
            entity_type=entity_type,
            company_id=company_id
        )

        # Cria a movimentação manualmente
        movement = Movement(
            entity_id=entity_id,
            entity_type=entity_type,
            company_id=company_id,
            type=movement_type,
            description=description,
            created_by=created_by
        )

        # Persiste a movimentação no banco de dados
        db.add(movement)
        db.commit()
        db.refresh(movement)

        return movement
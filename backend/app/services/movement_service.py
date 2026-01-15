from uuid import UUID
from sqlalchemy.orm import Session

from app.models.enum import (
    MovementType,
    MovementEntityType,
    OperationStatus,
)
from app.repositories.movement_repository import MovementRepository


class MovementService:

    @staticmethod
    def register_operation_created(
        db: Session,
        *,
        operation_id: UUID,
        company_id: UUID,
        created_by: UUID | None = None,
    ):
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
        return MovementRepository.create(
            db=db,
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            movement_type=movement_type,
            description=description,
            created_by=created_by,
        )
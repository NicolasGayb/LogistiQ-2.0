from http.client import HTTPException
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.enum import (
    MovementType,
    MovementEntityType,
    OperationStatus,
)
from app.repositories.movement_repository import MovementRepository
from app.models.movement import Movement
from app.models.operation import Operation


class MovementService:

    def __init__(self, db: Session):
        self.db = db

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
    
    @staticmethod
    def _validate_entity_exists(
        db: Session,
        *,
        entity_id: UUID,
        entity_type: MovementEntityType,
        company_id: UUID
    ):
        if entity_type == MovementEntityType.OPERATION:
            exists = (
                db.query(Operation)
                .filter(
                    Operation.id == entity_id,
                    Operation.company_id == company_id
                )
                .first()
            )

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
        # regra de domínio
        MovementService._validate_entity_exists(
            db,
            entity_id=entity_id,
            entity_type=entity_type,
            company_id=company_id
        )

        movement = Movement(
            entity_id=entity_id,
            entity_type=entity_type,
            company_id=company_id,
            type=movement_type,
            description=description,
            created_by=created_by
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        return movement
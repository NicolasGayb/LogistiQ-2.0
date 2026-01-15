from uuid import UUID
from sqlalchemy.orm import Session
from app.models.movement import Movement
from app.models.enum import MovementEntityType, MovementType, OperationStatus


class MovementRepository:

    @staticmethod
    def create(
        db: Session,
        *,
        entity_type: MovementEntityType,
        entity_id: UUID,
        company_id: UUID,
        movement_type: MovementType,
        previous_status: OperationStatus | None = None,
        new_status: OperationStatus | None = None,
        description: str | None = None,
        created_by: UUID | None = None,
    ) -> Movement:
        movement = Movement(
            entity_type=entity_type,
            entity_id=entity_id,
            company_id=company_id,
            type=movement_type,
            previous_status=previous_status,
            new_status=new_status,
            description=description,
            created_by=created_by,
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        return movement

    @staticmethod
    def list_by_entity(
        db: Session,
        *,
        entity_type: MovementEntityType,
        entity_id: UUID,
    ) -> list[Movement]:
        return (
            db.query(Movement)
            .filter(
                Movement.entity_type == entity_type,
                Movement.entity_id == entity_id
            )
            .order_by(Movement.created_at.asc())
            .all()
        )
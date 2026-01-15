from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.movement import MovementResponseSchema, MovementCreateSchema
from app.database import get_db
from app.models.base import Base
from app.core.dependencies import get_current_user
from app.models.movement import Movement
from app.services.movement_service import MovementService
from app.models.enum import MovementEntityType

router = APIRouter(prefix="/operations", tags=["Movements"])

@router.get("/{entity_id}/movements", response_model=list[MovementResponseSchema], status_code=status.HTTP_200_OK)
def list_movements(
    entity_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    movements = (
        db.query(Movement)
        .filter(
            Movement.entity_id == entity_id,
            Movement.company_id == user.company_id
        )
        .order_by(Movement.created_at.asc())
        .all()
    )

    return movements

@router.post("/{entity_id}/movements", response_model=MovementResponseSchema, status_code=status.HTTP_201_CREATED)
def create_manual_movement(
    entity_id: UUID,
    data: MovementCreateSchema,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return MovementService.create_manual(
        db=db,
        entity_id=entity_id,
        entity_type=MovementEntityType.OPERATION,
        company_id=user.company_id,
        movement_type=data.type,
        description=data.description,
        created_by=user.id
    )

    
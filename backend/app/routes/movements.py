from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.movement import MovementResponseSchema, MovementCreateSchema
from app.database import get_db, Base
from app.core.dependencies import get_current_user
from app.models.movement import Movement
from app.services.movement_service import MovementService

router = APIRouter(prefix="/operations", tags=["Movements"])

@router.get("/{operation_id}/movements", response_model=list[MovementResponseSchema])
def list_movements(
    operation_id: UUID,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    movements = (
        db.query(Movement)
        .filter(
            Movement.operation_id == operation_id,
            Movement.company_id == user.company_id
        )
        .order_by(Movement.created_at.asc())
        .all()
    )

    return movements

@router.post("/{operation_id}/movements", response_model=MovementResponseSchema)
def create_manual_movement(
    operation_id: UUID,
    data: MovementCreateSchema,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return MovementService(db).create(
        operation_id=operation_id,
        company_id=user.company_id,
        type=data.type,
        description=data.description,
        user_id=user.id
    )
    
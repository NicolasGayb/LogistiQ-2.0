from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enum import MovementEntityType, MovementType, OperationStatus

class MovementBase(BaseModel):
    type: MovementType
    description: str | None = None
    previous_status: OperationStatus | None = None
    new_status: OperationStatus | None = None
    created_at: datetime


class MovementResponse(MovementBase):
    id: UUID
    entity_id: UUID
    entity_type: MovementEntityType
    company_id: UUID
    created_by: UUID | None = None

    model_config = ConfigDict(from_attributes=True)

class MovementCreateSchema(BaseModel):
    type: MovementType
    description: str | None = None

class MovementResponseSchema(MovementResponse):
    pass

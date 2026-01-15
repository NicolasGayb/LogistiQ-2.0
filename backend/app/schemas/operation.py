from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.operation import OperationStatus


class OperationCreateSchema(BaseModel):
    reference_code: str
    origin: str
    destination: str


class OperationUpdateStatusSchema(BaseModel):
    status: OperationStatus


class OperationResponseSchema(BaseModel):
    id: UUID
    reference_code: str
    status: OperationStatus
    origin: str
    destination: str
    created_at: datetime

    class Config:
        from_attributes = True

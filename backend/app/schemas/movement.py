# Importação padrão
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Importação interna
from app.models.enum import MovementEntityType, MovementType, OperationStatus

# Esquema base para movimentos
class MovementBase(BaseModel):
    type: MovementType
    description: str | None = None
    previous_status: OperationStatus | None = None
    new_status: OperationStatus | None = None
    created_at: datetime

# Esquema de resposta para movimentos
class MovementResponse(MovementBase):
    id: UUID
    entity_id: UUID
    entity_type: MovementEntityType
    company_id: UUID
    created_by: UUID | None = None

    model_config = ConfigDict(from_attributes=True)

# Esquema para criação de movimentos
class MovementCreateSchema(BaseModel):
    type: MovementType
    description: str | None = None

# Esquema de resposta para movimentos (herda de MovementResponse)
class MovementResponseSchema(MovementResponse):
    pass

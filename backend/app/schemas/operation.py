# Importação padrão
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from app.models.enum import OperationType

# Importação interna
from app.models.operation import OperationStatus

# Esquema para itens da operação
class OperationItemSchema(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float

# Esquema para criação de operações
class OperationCreateSchema(BaseModel):
    reference_code: str
    origin: str
    destination: str
    type: OperationType
    partner_id: UUID
    expected_delivery_date: Optional[datetime] = Field(alias="expected_delivery_date", default=None)
    observation: Optional[str] = None
    items: List[OperationItemSchema]

# Esquema para atualização do status da operação
class OperationUpdateStatusSchema(BaseModel):
    status: OperationStatus

# Esquema de resposta para operações
class OperationResponseSchema(BaseModel):
    id: UUID
    reference_code: str
    status: OperationStatus
    origin: str
    destination: str
    created_at: datetime
    updated_at: datetime | None = None
    updated_by: UUID | None = None
    expected_delivery_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


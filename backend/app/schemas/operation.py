# Importação padrão
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

# Importação interna
from app.models.operation import OperationStatus

# Esquema para criação de operações
class OperationCreateSchema(BaseModel):
    reference_code: str
    origin: str
    destination: str

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

    model_config = ConfigDict(from_attributes=True)


# Importações padrão
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional

# Importação interna
from app.models.enum import UserRole

# Esquema de Resumo da Empresa
class CompanySummary(BaseModel):
    id: uuid.UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

# Esquema de criação de Usuário
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    company_id: Optional[uuid.UUID] = None

# Esquema de registro de Usuário com Token
class UserRegisterWithToken(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str
    token: str

# Esquema de atualização de Usuário
class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    email: Optional[EmailStr] = None
    company_id: Optional[uuid.UUID] = None

# Esquema de resposta de Usuário
class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    company_id: Optional[uuid.UUID] = None

    is_active: bool
    company: Optional[CompanySummary] = None

    model_config = ConfigDict(from_attributes=True)



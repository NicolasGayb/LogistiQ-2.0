# Importações padrão
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, computed_field, field_validator
from typing import Optional
from datetime import datetime

# Importação interna
from app.models.enum import UserRole

# Esquema de Resumo da Empresa
class CompanySummary(BaseModel):
    id: uuid.UUID
    name: str
    cnpj: Optional[str]

    stock_alert_limit: Optional[int] = 10  # Limite padrão de alerta de estoque

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
    password: Optional[str] = None
    company_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None

# Esquema de resposta de Usuário
class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    company_id: Optional[uuid.UUID] = None
    updated_at: datetime
    created_at: datetime

    notification_stock_alert: bool = True
    notification_weekly_summary: bool = True
    theme_preference: str = "auto"
    
    @computed_field
    def avatar_url(self) -> str:
        # Gera a URL do avatar com base no ID do usuário
        return f"/users/{self.id}/avatar"

    is_active: bool
    company: Optional[CompanySummary] = None

    model_config = ConfigDict(from_attributes=True)

# Esquema de atualização de configurações do Usuário
class UserUpdateSettings(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    notification_stock_alert: Optional[bool] = None
    notification_weekly_summary: Optional[bool] = None
    theme_preference: Optional[str] = None

# Esquema para troca de senha
class UserChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

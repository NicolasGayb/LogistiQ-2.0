# Importações padrão
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Optional

# Importação interna
from app.core.validators import normalize_cnpj

# Esquema para criação de empresa
class CompanyCreate(BaseModel):
    name: str
    cnpj: Optional[str] = None

    # Validador para normalizar o CNPJ antes da validação
    @field_validator("cnpj", mode="before")
    @classmethod
    def validate_cnpj(cls, value: str) -> str:
        return normalize_cnpj(value)

# Esquema para resposta de empresa
class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    cnpj: Optional[str]
    token: str

    model_config = ConfigDict(from_attributes=True)

# Esquema para atualização do nome da empresa
class CompanyNameUpdate(BaseModel):
    name: Optional[str] = None

# Esquema para criação de empresa com administrador
class CompanyWithAdminCreate(BaseModel):
    company: CompanyCreate
    admin_name: str
    admin_email: EmailStr
    admin_password: str

# Esquema para atualização do status da empresa
class CompanyStatusUpdate(BaseModel):
    is_active: bool

# Esquema para resposta de estatísticas do dashboard
class DashboardStatsResponse(BaseModel):
    companies_count: int  
    users_count: int      
    system_status: str
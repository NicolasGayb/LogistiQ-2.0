import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Optional
from app.core.validators import normalize_cnpj


class CompanyCreate(BaseModel):
    name: str
    cnpj: Optional[str] = None
    token: str

    @field_validator("cnpj", mode="before")
    @classmethod
    def validate_cnpj(cls, value: str) -> str:
        return normalize_cnpj(value)

class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    cnpj: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class CompanyNameUpdate(BaseModel):
    name: Optional[str] = None

class CompanyWithAdminCreate(BaseModel):
    company: CompanyCreate
    admin_name: str
    admin_email: EmailStr
    admin_password: str

class CompanyStatusUpdate(BaseModel):
    is_active: bool
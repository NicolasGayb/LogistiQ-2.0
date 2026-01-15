import uuid
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class CompanyCreate(BaseModel):
    name: str
    cnpj: Optional[str] = None

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
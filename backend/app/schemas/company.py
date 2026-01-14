import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional


class CompanyCreate(BaseModel):
    name: str
    cnpj: Optional[str] = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    cnpj: Optional[str]

    class Config:
        from_attributes = True


class CompanyWithAdminCreate(BaseModel):
    company: CompanyCreate
    admin_name: str
    admin_email: EmailStr
    admin_password: str
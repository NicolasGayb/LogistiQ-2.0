import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from app.models.enum import UserRole

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserMeResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str
    company_id: Optional[uuid.UUID] = None
    company_name: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class SystemAdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    company_cnpj: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8)
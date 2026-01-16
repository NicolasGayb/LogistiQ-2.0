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

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class UserMeResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str
    company_id: Optional[uuid.UUID] = None
    company_name: Optional[str] = None
    is_active: bool

    class Config:
        ConfigDict(from_attributes=True)
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "ADMIN",
                "company_id": "123e4567-e89b-12d3-a456-426614174001",
                "company_name": "Example Corp",
                "is_active": True
            }
        }

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
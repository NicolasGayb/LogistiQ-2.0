import uuid
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from app.models.enum import UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    company_id: Optional[uuid.UUID] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    email: Optional[EmailStr] = None
    company_id: Optional[uuid.UUID] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    company_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)



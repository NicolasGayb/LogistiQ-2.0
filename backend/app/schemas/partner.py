from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID

# --- SCHEMAS (Modelos de Entrada/Saída da API) ---

class PartnerBase(BaseModel):
    name: str
    document: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    is_customer: bool = True
    is_supplier: bool = False
    active: bool = True

class PartnerCreate(PartnerBase):
    company_id: Optional[UUID] = None # Opcional se pegarmos do usuário logado

class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    document: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    is_customer: Optional[bool] = None
    is_supplier: Optional[bool] = None
    active: Optional[bool] = None

class PartnerResponse(PartnerBase):
    id: UUID
    company_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
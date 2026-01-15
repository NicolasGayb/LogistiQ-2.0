from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None, max_length=1024)
    sku: str = Field(..., max_length=64)
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1024)
    sku: Optional[str] = Field(default=None, max_length=64)
    price: Optional[float] = Field(default=None, ge=0)
    quantity: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ProductOut(ProductBase):
    id: uuid.UUID
    name: str
    description: str | None
    sku: str
    price: float
    quantity: int
    is_active: bool
    company_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

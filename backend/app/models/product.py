import uuid
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    # Multi-tenant
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Dados do produto
    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)
    sku = Column(String(80), nullable=True, index=True)
    quantity = Column(Integer, default=0, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    created_at = Column(
        String,
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        String,
        nullable=True,
        onupdate=func.now()
    )

    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relacionamentos
    company = relationship("Company", back_populates="products")

    def __repr__(self):
        return f"<Product id={self.id} name={self.name}>"
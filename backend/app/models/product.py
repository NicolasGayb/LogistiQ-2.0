import uuid
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


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

    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    company = relationship("Company", back_populates="products")

    def __repr__(self):
        return f"<Product id={self.id} name={self.name}>"
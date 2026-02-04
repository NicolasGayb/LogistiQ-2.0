# Importações padrão
import uuid
from sqlalchemy import Column, DateTime, Integer, String, Numeric, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# Importação local
from app.models.base import Base

# Definição do modelo Product
class Product(Base):
    '''Modelo que representa um produto dentro do sistema.
    
    Atributos:
        id (UUID): Identificador único do produto.
        company_id (UUID): Identificador da empresa proprietária do produto.
        name (str): Nome do produto.
        description (str): Descrição do produto.
        sku (str): Código SKU do produto.
        quantity (int): Quantidade disponível do produto.
        price (Decimal): Preço do produto.
        is_active (bool): Indica se o produto está ativo.
        created_by (UUID): Identificador do usuário que criou o produto.
        created_at (datetime): Data e hora de criação do produto.
        updated_at (datetime): Data e hora da última atualização do produto.
        updated_by (UUID): Identificador do usuário que atualizou o produto pela última vez.
    Relações:
        company (Company): Empresa proprietária do produto.
    '''
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
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
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

    updater = relationship("User", foreign_keys=[updated_by])

    @property
    def company_name(self):
        '''Retorna o nome da empresa proprietária do produto.'''
        return self.company.name if self.company else "N/A"

    @property
    def updated_by_name(self):
        '''Retorna o nome do usuário que atualizou o produto pela última vez.'''
        return self.updater.name if self.updater else None

    def __repr__(self):
        return f"<Product id={self.id} name={self.name}>"
import uuid
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

# Modelo da tabela Company
class Company(Base):
    '''Modelo da tabela Company
    
    Attributes:
        id (uuid.UUID): Identificador único da empresa.
        name (str): Nome da empresa.
        cnpj (str): CNPJ da empresa.
        is_active (bool): Indica se a empresa está ativa.
        created_at (DateTime): Data e hora de criação do registro.
        token (str): Token único associado à empresa.
        products (List[Product]): Relação com os produtos da empresa.
        users (List[User]): Relação com os usuários associados à empresa.
    '''
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    products = relationship("Product", back_populates="company", cascade="all, delete-orphan")

    users = relationship("User", back_populates="company")
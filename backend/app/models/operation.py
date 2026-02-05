# Importações padrão
import uuid
from sqlalchemy import String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

# Importações internas
from app.models.base import Base
from app.models.enum import OperationStatus

# Definição do modelo Operation
class Operation(Base):
    '''Modelo que representa uma operação dentro do sistema.
    
    A operação está associada a uma empresa e a um produto, e possui
    atributos como status, origem, destino, timestamps de criação e atualização,
    e o usuário que realizou a última atualização.
    
    Attributes:
        id (uuid.UUID): Identificador único da operação.
        company_id (uuid.UUID): Identificador da empresa associada.
        product_id (uuid.UUID): Identificador do produto associado.
        status (OperationStatus): Status atual da operação.
        origin (str | None): Local de origem da operação.
        destination (str | None): Local de destino da operação.
        expected_delivery_date (str | None): Data prevista para entrega.
        created_at (str): Timestamp de criação da operação.
        updated_at (str): Timestamp da última atualização da operação.
        updated_by (uuid.UUID | None): Identificador do usuário que realizou a última atualização.
    '''
    __tablename__ = "operations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    status: Mapped[OperationStatus] = mapped_column(
        Enum(OperationStatus),
        nullable=False,
        default=OperationStatus.CREATED
    )

    origin: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True
    )
    destination: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True
    )

    expected_delivery_date: Mapped[str | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
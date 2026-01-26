# Importação de bibliotecas padrão
import uuid
from sqlalchemy import String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

# Importação de módulos internos
from app.models.enum import (
    MovementType,
    MovementEntityType,
    OperationStatus
)
from app.models.base import Base

# Definição do modelo Movement
class Movement(Base):
    '''Modelo que representa um movimento ou alteração de estado de uma entidade dentro do sistema.
    
    Atributos:
        id (uuid.UUID): Identificador único do movimento.
        company_id (uuid.UUID): Identificador da empresa associada ao movimento.
        entity_type (MovementEntityType): Tipo da entidade alvo do movimento.
        entity_id (uuid.UUID): Identificador da entidade alvo do movimento.
        type (MovementType): Tipo do movimento realizado.
        previous_status (OperationStatus | None): Status anterior da entidade antes do movimento.
        new_status (OperationStatus | None): Novo status da entidade após o movimento.
        description (str | None): Descrição adicional sobre o movimento.
        created_by (uuid.UUID | None): Identificador do usuário que criou o movimento.
        created_at (str): Timestamp de quando o movimento foi criado.
    '''
    __tablename__ = "movements"

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

    # 🔑 entidade alvo do movimento
    entity_type: Mapped[MovementEntityType] = mapped_column(
        Enum(MovementEntityType),
        nullable=False
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    type: Mapped[MovementType] = mapped_column(
        Enum(MovementType),
        nullable=False
    )

    previous_status: Mapped[OperationStatus | None] = mapped_column(
        Enum(OperationStatus),
        nullable=True
    )

    new_status: Mapped[OperationStatus | None] = mapped_column(
        Enum(OperationStatus),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(String(500))

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

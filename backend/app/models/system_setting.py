import uuid
from sqlalchemy import Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import Base

class SystemSetting(Base):
    '''Armazena as configurações globais do sistema.
    Geralmente terá apenas 1 registro ativo.
    '''
    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Configurações
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_registrations: Mapped[bool] = mapped_column(Boolean, default=True)
    session_timeout: Mapped[int] = mapped_column(Integer, default=60) # Em minutos
    
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now(),
        server_default=func.now()
    )
    
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
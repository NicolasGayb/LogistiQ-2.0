import uuid
from sqlalchemy import String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import Base
from app.models.enum import OperationStatus


class Operation(Base):
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

    origin: Mapped[str | None] = mapped_column(String(255))
    destination: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now()
    )
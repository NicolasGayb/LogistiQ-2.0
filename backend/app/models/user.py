import uuid
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.enum import UserRole
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    reset_password_token: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    reset_password_token_expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    role: Mapped[UserRole] = mapped_column(
    Enum(
        "ADMIN",
        "MANAGER",
        "USER",
        "SYSTEM_ADMIN",
        name="userrole",
        schema="public",
        create_type=False
    ),
    nullable=False
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    company = relationship("Company", back_populates="users")
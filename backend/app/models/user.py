# Importações padrão
import uuid
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

# Importação local
from app.models.enum import UserRole
from app.models.base import Base

# Definição do modelo User
class User(Base):
    '''Modelo que representa um usuário dentro do sistema.
    
    Atributos:
        id (uuid.UUID): Identificador único do usuário.
        name (str): Nome completo do usuário.
        email (str): Endereço de e-mail do usuário.
        password_hash (str): Hash da senha do usuário.
        reset_password_token (str | None): Token para redefinição de senha.
        reset_password_token_expires_at (DateTime | None): Data de expiração do token de redefinição de senha.
        role (UserRole): Papel do usuário no sistema.
        company_id (uuid.UUID): Identificador da empresa associada ao usuário.
        is_active (bool): Indica se o usuário está ativo.
        created_at (DateTime): Data de criação do registro do usuário.
    Relações:
        company (Company): Relação com o modelo Company.
    '''
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Campos para redefinição de senha
    reset_password_token: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    reset_password_token_expires_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Definição do papel do usuário usando Enum
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

    # Associação opcional com a empresa (vazio apenas para usuários com role SYSTEM_ADMIN)
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
# Importação externa
from sqlalchemy.orm import Session

# Importações internas
from app.models.user import User
from app.models.enum import MovementType, UserRole
from app.core.security import hash_password
from app.services.movement_service import MovementService, MovementEntityType

# Serviço de Administrador do Sistema
def create_system_admin(
    db: Session,
    name: str,
    email: str,
    password: str
):
    '''Cria um usuário administrador do sistema
    Args:
        db (Session): Sessão do banco de dados
        name (str): Nome do administrador
        email (str): Email do administrador
        password (str): Senha do administrador
    Returns:
        User: Usuário administrador criado
    '''
    # Cria o usuário administrador do sistema
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.SYSTEM_ADMIN
    )

    # Cria o movimento de criação do usuário para auditoria
    MovementService.create_manual(
        db=db,
        entity_id=user.id,
        entity_type=MovementEntityType.USER,
        movement_type=MovementType.CREATION,
        performed_by=user.id,  # O próprio usuário é o responsável pela criação
        details=f"Criação do usuário SYSTEM_ADMIN: {user.name} ({user.email})"
    )

    # Adiciona e comita o usuário no banco de dados
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
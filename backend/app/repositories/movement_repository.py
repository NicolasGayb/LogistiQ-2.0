# Importação padrão
from uuid import UUID
from sqlalchemy.orm import Session

# Importação interna
from app.models.movement import Movement
from app.models.enum import MovementEntityType, MovementType, OperationStatus

# Repositório de Movimentações
class MovementRepository:
    '''Repositório para operações relacionadas a Movimentações.
    
    Métodos:
        - create: Cria uma nova movimentação.
        - list_by_entity: Lista movimentações por tipo e ID da entidade.
    '''

    @staticmethod
    def create(
        db: Session,
        *,
        entity_type: MovementEntityType,
        entity_id: UUID,
        company_id: UUID,
        movement_type: MovementType,
        previous_status: OperationStatus | None = None,
        new_status: OperationStatus | None = None,
        description: str | None = None,
        created_by: UUID | None = None,
    ) -> Movement:
        '''Cria uma nova movimentação no banco de dados.
        
        Parâmetros:
            - db: Sessão do banco de dados.
            - entity_type: Tipo da entidade associada à movimentação.
            - entity_id: ID da entidade associada à movimentação.
            - company_id: ID da empresa associada à movimentação.
            - movement_type: Tipo da movimentação.
            - previous_status: Status anterior da entidade (opcional).
            - new_status: Novo status da entidade (opcional).
            - description: Descrição da movimentação (opcional).
            - created_by: ID do usuário que criou a movimentação (opcional).
        '''
        movement = Movement(
            entity_type=entity_type,
            entity_id=entity_id,
            company_id=company_id,
            type=movement_type,
            previous_status=previous_status,
            new_status=new_status,
            description=description,
            created_by=created_by,
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        return movement

    @staticmethod
    def list_by_entity(
        db: Session,
        *,
        entity_type: MovementEntityType,
        entity_id: UUID,
    ) -> list[Movement]:
        '''Lista movimentações por tipo e ID da entidade.

        Parâmetros:
            - db: Sessão do banco de dados.
            - entity_type: Tipo da entidade associada à movimentação.
            - entity_id: ID da entidade associada à movimentação.
        '''
        return (
            db.query(Movement)
            .filter(
                Movement.entity_type == entity_type,
                Movement.entity_id == entity_id
            )
            .order_by(Movement.created_at.asc())
            .all()
        )
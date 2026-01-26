# Importações externas
from sqlalchemy.orm import Session

# Importações internas
from app.models.operation import Operation, OperationStatus
from app.models.movement import MovementType
from app.services.movement_service import MovementService
from app.domain.operation_validator import validate_status_transition, InvalidOperationTransition


class OperationService:
    ''' Serviço responsável por gerenciar operações no sistema.
    
    Responsabilidades:
    - Criar e atualizar operações.
    - Validar regras de negócio associadas às operações.
    - Registrar movimentações relacionadas às operações.
    '''

    def __init__(self, db: Session):
        ''' Inicializa o serviço com a sessão do banco de dados.
        
        :param db: Sessão do banco de dados.
        '''
        self.db = db
        self.movement_service = MovementService(db)

    def create(self, data, user) -> Operation:
        ''' Cria uma nova operação no sistema.
        
        :param data: Dados da operação a ser criada.
        :param user: Usuário que está criando a operação.
        :return: Instância da operação criada.
        '''
        # Cria a instância da operação
        operation = Operation(
            company_id=user.company_id,
            reference_code=data.reference_code,
            origin=data.origin,
            destination=data.destination,
            status=OperationStatus.CREATED
        )

        # Adiciona a operação ao banco de dados
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)

        # Registra a movimentação de criação da operação
        self.movement_service.create(
            operation_id=operation.id,
            company_id=user.company_id,
            type=MovementType.OPERATION_CREATED,
            new_status=OperationStatus.CREATED,
            description="Operação criada",
            user_id=user.id
        )

        return operation

    def update_status(
        self,
        operation: Operation,
        new_status: OperationStatus,
        user
    ) -> Operation:
        ''' Atualiza o status de uma operação.

        :param operation: Instância da operação a ser atualizada.
        :param new_status: Novo status a ser atribuído à operação.
        :param user: Usuário que está realizando a atualização.
        :return: Instância da operação atualizada.
        '''
        # Armazena o status antigo para registro de movimentação
        old_status = operation.status

        # Se o status não mudou, não faz nada
        if old_status == new_status:
            return operation

        # Valida a transição de status
        validate_status_transition(old_status, new_status)

        # Atualiza o status da operação
        operation.status = new_status
        self.db.commit()

        # Registra a movimentação de alteração de status
        self.movement_service.create(
            operation_id=operation.id,
            company_id=operation.company_id,
            type=MovementType.STATUS_CHANGED,
            previous_status=old_status,
            new_status=new_status,
            description=f"Status alterado de {old_status} para {new_status}",
            user_id=user.id
        )

        return operation
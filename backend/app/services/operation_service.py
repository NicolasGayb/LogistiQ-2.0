# Importações externas
from sqlalchemy import func
from sqlalchemy.orm import Session

# Importações internas
from app.models.operation import Operation, OperationStatus
from app.models.movement import MovementType
from app.services.movement_service import MovementService
from app.domain.operation_validator import validate_status_transition, InvalidOperationTransition
from app.models.operation_item import OperationItem


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
            operation_number=self._generate_operation_number(user.company_id),
            company_id=user.company_id,
            partner_id=data.partner_id,
            reference_code=data.reference_code,
            origin=data.origin,
            destination=data.destination,
            type=data.type,
            expected_delivery_date=data.expected_delivery_date,
            observation=data.observation,
            status=OperationStatus.CREATED,
            created_at=func.now(),
            updated_at=func.now(),
            created_by=user.id,
            total_value=sum(item.quantity * item.unit_price for item in data.items)
        )

        # Adiciona a operação ao banco de dados
        self.db.add(operation)
        self.db.flush()  # Gera o ID da operação para associar os itens

        for item in data.items:
            new_item = OperationItem(
                operation_id=operation.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.quantity * item.unit_price
            )
            self.db.add(new_item)

        self.db.commit()
        self.db.refresh(operation)

        # Registra a movimentação de criação da operação
        self.movement_service.register_operation_created(
            operation_id=operation.id,
            company_id=user.company_id,
            ip_address=None,
            created_by=user.id
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
        
        # Registra a movimentação de alteração de status
        self.movement_service.register_status_change(
            db=self.db,
            operation_id=operation.id,
            company_id=operation.company_id,
            previous_status=old_status,
            new_status=new_status,
            created_by=user.id,
            ip_address=None
        )

        self.db.commit()
        self.db.refresh(operation)

        return operation
    
    # --- Definição de métodos ---
    
    def _generate_operation_number(self, company_id: str) -> str:
        ''' Gera um número único para a operação dentro da empresa.
        
        :param company_id: ID da empresa.
        :return: Número único da operação.
        '''
        last_operation = (
            self.db.query(Operation)
            .filter(Operation.company_id == company_id)
            .order_by(Operation.operation_number.desc())
            .first()
        )
        if last_operation:
            last_number = int(last_operation.operation_number)
            new_number = last_number + 1
        else:
            new_number = 1
        return str(new_number).zfill(6)
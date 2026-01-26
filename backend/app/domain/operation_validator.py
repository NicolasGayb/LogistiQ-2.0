from app.models.operation import OperationStatus
from app.domain.operation_state_machine import ALLOWED_TRANSITIONS

# Exceção personalizada para transições inválidas
class InvalidOperationTransition(Exception):
    pass

# Função para validar transições de estado
def validate_status_transition(
    current_status: OperationStatus,
    new_status: OperationStatus
):
    '''
    Valida se a transição de estado é permitida.
    Args:
        current_status (OperationStatus): O estado atual da operação.
        new_status (OperationStatus): O novo estado para o qual a operação está tentando transitar.
    Raises:
        InvalidOperationTransition: Se a transição não for permitida.
    '''
    # Obtém os estados permitidos para a transição atual
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())

    # Verifica se a transição é permitida
    if new_status not in allowed:
        raise InvalidOperationTransition(
            f"Transição inválida: {current_status} → {new_status}"
        )
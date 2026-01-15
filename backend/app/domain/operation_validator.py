from app.models.operation import OperationStatus
from app.domain.operation_state_machine import ALLOWED_TRANSITIONS


class InvalidOperationTransition(Exception):
    pass


def validate_status_transition(
    current_status: OperationStatus,
    new_status: OperationStatus
):
    allowed = ALLOWED_TRANSITIONS.get(current_status, set())

    if new_status not in allowed:
        raise InvalidOperationTransition(
            f"Transição inválida: {current_status} → {new_status}"
        )
from sqlalchemy.orm import Session
from app.models.operation import Operation, OperationStatus
from app.models.movement import MovementType
from app.services.movement_service import MovementService
from app.domain.operation_validator import validate_status_transition, InvalidOperationTransition


class OperationService:

    def __init__(self, db: Session):
        self.db = db
        self.movement_service = MovementService(db)

    def create(self, data, user) -> Operation:
        operation = Operation(
            company_id=user.company_id,
            reference_code=data.reference_code,
            origin=data.origin,
            destination=data.destination,
            status=OperationStatus.CREATED
        )

        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)

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

        old_status = operation.status

        if old_status == new_status:
            return operation

        validate_status_transition(old_status, new_status)

        operation.status = new_status
        self.db.commit()

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
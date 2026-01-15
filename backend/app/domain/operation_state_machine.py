from app.models.operation import OperationStatus

ALLOWED_TRANSITIONS: dict[OperationStatus, set[OperationStatus]] = {
    OperationStatus.CREATED: {
        OperationStatus.AT_ORIGIN,
        OperationStatus.CANCELED,
    },

    OperationStatus.AT_ORIGIN: {
        OperationStatus.LOADED,
        OperationStatus.CANCELED,
    },

    OperationStatus.LOADED: {
        OperationStatus.IN_TRANSIT,
        OperationStatus.CANCELED,
    },

    OperationStatus.IN_TRANSIT: {
        OperationStatus.AT_HUB,
        OperationStatus.UNLOADED,
        OperationStatus.CANCELED,
    },

    OperationStatus.AT_HUB: {
        OperationStatus.IN_TRANSIT,
        OperationStatus.UNLOADED,
        OperationStatus.CANCELED,
    },

    OperationStatus.UNLOADED: {
        OperationStatus.COMPLETED,
        OperationStatus.CANCELED,
    },

    OperationStatus.COMPLETED: set(),
    OperationStatus.CANCELED: set(),
}

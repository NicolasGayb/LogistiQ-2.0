from enum import Enum

# Define enumerators para varios tipos e estados usados na aplicação
class UserRole(str, Enum):
    '''Define os papéis de usuário disponíveis na aplicação
    
    ADMIN: Administrador com permissões completas
    MANAGER: Gerente com permissões de gerenciamento
    USER: Usuário padrão com permissões limitadas
    SYSTEM_ADMIN: Administrador do sistema com permissões avançadas
    '''
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

class MovementEntityType(str, Enum):
    '''Define os tipos de entidades que podem gerar movimentos
    
    OPERATION: Movimento relacionado a uma operação
    PRODUCT: Movimento relacionado a um produto
    '''
    OPERATION = "OPERATION"
    PRODUCT = "PRODUCT"

class MovementType(str, Enum):
    '''Define os tipos de movimentos possíveis na aplicação

    OPERATION_CREATED: Movimento criado para uma nova operação
    CREATION: Movimento indicando criação de um produto
    INPUT: Movimento indicando entrada de um produto
    OUTPUT: Movimento indicando saída de um produto
    ACTIVATED: Movimento indicando que o produto foi ativado
    DEACTIVATED: Movimento indicando que o produto foi desativado
    STATUS_CHANGED: Movimento indicando mudança de status
    UPDATED: Movimento indicando atualização de um produto
    DELETED: Movimento indicando exclusão de um produto
    LOADED: Movimento indicando que o produto foi carregado
    UNLOADED: Movimento indicando que o produto foi descarregado
    IN_TRANSIT: Movimento indicando que o produto está em trânsito
    ARRIVED_AT_HUB: Movimento indicando que o produto chegou ao hub
    DELAY_REPORTED: Movimento indicando que um atraso foi reportado
    INCIDENT_REPORTED: Movimento indicando que um incidente foi reportado
    CANCELED: Movimento indicando que a operação foi cancelada
    UPDATED: Movimento indicando que a operação foi atualizada
    COMPLETED: Movimento indicando que a operação foi concluída
    '''
    OPERATION_CREATED = "OPERATION_CREATED"
    CREATION = "CREATION"
    DELETED = "DELETED"
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    LOADED = "LOADED"
    UNLOADED = "UNLOADED"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED_AT_HUB = "ARRIVED_AT_HUB"
    DELAY_REPORTED = "DELAY_REPORTED"
    INCIDENT_REPORTED = "INCIDENT_REPORTED"
    CANCELED = "CANCELED"
    UPDATED = "UPDATED"
    COMPLETED = "COMPLETED"

class OperationStatus(str, Enum):
    '''
    Define os status possíveis para uma operação

    CREATED: Operação criada
    AT_ORIGIN: Operação no local de origem
    LOADED: Operação com produto carregado
    IN_TRANSIT: Operação em trânsito
    AT_HUB: Operação no hub
    UNLOADED: Operação com produto descarregado
    COMPLETED: Operação concluída
    CANCELED: Operação cancelada
    ''' 
    CREATED = "CREATED"
    AT_ORIGIN = "AT_ORIGIN"
    LOADED = "LOADED"
    IN_TRANSIT = "IN_TRANSIT"
    AT_HUB = "AT_HUB"
    UNLOADED = "UNLOADED"
    COMPLETED = "COMPLETED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"

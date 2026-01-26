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
    STATUS_CHANGED: Movimento indicando mudança de status
    PRODUCT_CREATED: Movimento criado para um novo produto
    PRODUCT_UPDATED: Movimento indicando atualização de um produto
    PRODUCT_DELETED: Movimento indicando exclusão de um produto
    LOADED: Movimento indicando que o produto foi carregado
    UNLOADED: Movimento indicando que o produto foi descarregado
    IN_TRANSIT: Movimento indicando que o produto está em trânsito
    ARRIVED_AT_HUB: Movimento indicando que o produto chegou ao hub
    DELAY_REPORTED: Movimento indicando que um atraso foi reportado
    INCIDENT_REPORTED: Movimento indicando que um incidente foi reportado
    CANCELED: Movimento indicando que a operação foi cancelada
    UPDATED: Movimento indicando que a operação foi atualizada
    COMPLETED: Movimento indicando que a operação foi concluída
    IN: Movimento indicando entrada de produto
    OUT: Movimento indicando saída de produto
    '''
    OPERATION_CREATED = "OPERATION_CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    PRODUCT_CREATED = "PRODUCT_CREATED"
    PRODUCT_UPDATED = "PRODUCT_UPDATED"
    PRODUCT_DELETED = "PRODUCT_DELETED"
    LOADED = "LOADED"
    UNLOADED = "UNLOADED"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED_AT_HUB = "ARRIVED_AT_HUB"
    DELAY_REPORTED = "DELAY_REPORTED"
    INCIDENT_REPORTED = "INCIDENT_REPORTED"
    CANCELED = "CANCELED"
    UPDATED = "UPDATED"
    COMPLETED = "COMPLETED"
    IN = "IN"
    OUT = "OUT"

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
    CANCELED = "CANCELED"

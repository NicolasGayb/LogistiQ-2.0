# Importações externas
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

# Importações internas
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.movement_service import MovementService
from app.models.enum import MovementType, MovementEntityType

class ProductService:
    '''Serviço para gerenciar produtos
    
    Responsabilidades:
    - Listar produtos
    - Obter detalhes de um produto
    - Criar novos produtos
    - Atualizar produtos existentes
    - Ativar/Desativar produtos
    - Deletar produtos
    '''

    def __init__(self, db: Session):
        self.db = db

    # Método público para listar produtos, com opção de filtrar por empresa (para usuários comuns) ou listar todos (para System Admin)
    def list_products(self, company_id: UUID | None = None):
        query = self.db.query(Product).options(joinedload(Product.company))
        if company_id:
            query = query.filter(Product.company_id == company_id)
            return query.filter(Product.is_active == True).all() # Apenas ativos
        else:
            return query.all() # Retorna todos para o System Admin ver os inativos também

    # Método público para obter produto por ID, usado nas rotas para garantir que usuários só acessem produtos da sua empresa (exceto System Admin)
    def get_by_id(self, product_id: UUID, company_id: UUID):
        product = self._get_product_by_id_and_company(product_id=product_id, company_id=company_id)
        
        if not product:
            raise ValueError("Produto não encontrado.")
        return product
    
    # Método privado para obter produto por ID e empresa, usado internamente para garantir que usuários só acessem produtos da sua empresa (exceto System Admin)
    def _get_product_by_id_and_company(
        self,
        product_id: UUID, 
        company_id: UUID | None
    ):
        query = self.db.query(Product).filter(Product.id == product_id)

        # Filtra por company_id se for um usuário que não é SYSTEM_ADMIN
        if company_id:
            query = query.filter(Product.company_id == company_id)

        return query.first()

    def create_product(
        self,
        company_id: UUID, 
        created_by: UUID, 
        data: ProductCreate, 
        ip_address: str | None = None # <--- Recebe IP
    ):
        # Valida SKU
        if data.sku:
            sku_exists = self.db.query(Product).filter(
                Product.sku == data.sku,
                Product.company_id == company_id
            ).first()
            if sku_exists:
                raise ValueError("SKU já existe para esta empresa.")

        # Cria Produto (SEM IP)
        new_product = Product(
            name=data.name,
            sku=data.sku,
            price=data.price,
            quantity=data.quantity,
            description=data.description,
            company_id=company_id,
            created_by=created_by,
            is_active=True
        )
        self.db.add(new_product)
        try:
            self.db.commit()
            self.db.refresh(new_product)
            
            # REGISTRA O MOVIMENTO (COM IP)
            MovementService(self.db).create_manual(
                company_id=company_id,
                created_by=created_by,
                entity_id=new_product.id,
                entity_type=MovementEntityType.PRODUCT,
                movement_type=MovementType.CREATION,
                description=f"Produto criado: {new_product.name}",
                ip_address=ip_address
            )
            
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Falha ao criar o produto.")
        return new_product

    def update_product(
        self,
        product_id: UUID, 
        company_id: UUID | None,
        updated_by: UUID, 
        data: ProductUpdate,
        ip_address: str | None = None
    ):
        product = self._get_product_by_id_and_company(
            product_id=product_id,
            company_id=company_id
        )

        if data.sku and data.sku != product.sku:

            target_company_id = product.company_id

            sku_exists = self.db.query(Product).filter(
                Product.sku == data.sku,
                Product.company_id == target_company_id,
                Product.id != product_id,
                Product.is_active == True
            ).first()
            if sku_exists:
                raise ValueError("SKU já existe para esta empresa.")

        # Atualiza campos
        product.name = data.name or product.name
        product.sku = data.sku or product.sku
        product.price = data.price if data.price is not None else product.price
        product.quantity = data.quantity if data.quantity is not None else product.quantity
        product.description = data.description or product.description
        product.updated_by = updated_by
        product.updated_at = func.now()

        self.db.commit()
        self.db.refresh(product)

        # Registrar movimento de atualização
        MovementService(self.db).create_manual(
            company_id=company_id,
            created_by=updated_by,
            entity_id=product.id,
            entity_type=MovementEntityType.PRODUCT,
            movement_type=MovementType.UPDATED,
            description=f"Produto atualizado: {product.name}",
            ip_address=ip_address
        )
        
        return product

    def deactivate_product(
        self,
        product_id: UUID, 
        company_id: UUID | None,
        updated_by: UUID,
        ip_address: str | None = None # <--- Recebe IP
    ):
        product = self._get_product_by_id_and_company(
            product_id=product_id,
            company_id=company_id
        )
        if not product:
            raise ValueError("Produto não encontrado.")

        product.is_active = False
        product.updated_by = updated_by
        product.updated_at = func.now()

        self.db.commit()
        self.db.refresh(product)

        # REGISTRA MOVIMENTO
        MovementService(self.db).create_manual(
            company_id=product.company_id,
            created_by=updated_by,
            entity_id=product.id,
            entity_type=MovementEntityType.PRODUCT,
            movement_type=MovementType.DEACTIVATED,
            description=f"Produto desativado: {product.name}",
            ip_address=ip_address
        )

        return product

    def activate_product(
        self,
        product_id: UUID, 
        company_id: UUID | None, 
        updated_by: UUID, 
        ip_address: str | None = None
    ):
        product = self._get_product_by_id_and_company(
            product_id=product_id,
            company_id=company_id
        )
        if not product:
            raise ValueError("Produto não encontrado.")
        
        product.is_active = True
        product.updated_by = updated_by
        product.updated_at = func.now()

        self.db.commit()
        self.db.refresh(product)

        # REGISTRA MOVIMENTO
        MovementService(self.db).create_manual(
            company_id=product.company_id,
            created_by=updated_by,
            entity_id=product.id,
            entity_type=MovementEntityType.PRODUCT,
            movement_type=MovementType.ACTIVATED,
            description=f"Produto ativado: {product.name}",
            ip_address=ip_address
        )

        return product
    
    def delete_product(
        self,
        product_id: UUID, 
        company_id: UUID | None,
        ip_address: str | None = None
    ):
        product = self._get_product_by_id_and_company(
            product_id=product_id,
            company_id=company_id
        )

        if not product:
            raise ValueError("Produto não encontrado.")
        
        self.db.delete(product)
        self.db.commit()

        # REGISTRA MOVIMENTO
        MovementService(self.db).create_manual(
            company_id=product.company_id,
            created_by=None,  # Sistema
            entity_id=product.id,
            entity_type=MovementEntityType.PRODUCT,
            movement_type=MovementType.DELETED,
            description=f"Produto deletado: {product.name}",
            ip_address=ip_address
        )

        return f"Produto {product.name} deletado com sucesso."
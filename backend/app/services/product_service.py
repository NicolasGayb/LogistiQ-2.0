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

    @staticmethod
    def list_products(db: Session, company_id: UUID | None = None):
        query = db.query(Product).options(joinedload(Product.company))
        if company_id:
            query = query.filter(Product.company_id == company_id)
            return query.filter(Product.is_active == True).all() # Apenas ativos
        else:
            return query.all() # Retorna todos para o System Admin ver os inativos também

    @staticmethod
    def get_by_id(db: Session, product_id: UUID, company_id: UUID):
        product = ProductService.get_product_by_id_and_company(db=db, product_id=product_id, company_id=company_id)
        
        if not product:
            raise ValueError("Produto não encontrado.")
        return product
    
    @staticmethod
    def get_product_by_id_and_company(
        db: Session, 
        product_id: UUID, 
        company_id: UUID | None
    ):
        query = db.query(Product).filter(Product.id == product_id)

        # Filtra por company_id se for um usuário que não é SYSTEM_ADMIN
        if company_id:
            query = query.filter(Product.company_id == company_id)

        return query.first()

    @staticmethod
    def create_product(
        db: Session, 
        company_id: UUID, 
        created_by: UUID, 
        data: ProductCreate, 
        ip_address: str | None = None # <--- Recebe IP
    ):
        # Valida SKU
        if data.sku:
            sku_exists = db.query(Product).filter(
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
        db.add(new_product)
        try:
            db.commit()
            db.refresh(new_product)
            
            # REGISTRA O MOVIMENTO (COM IP)
            MovementService.create_manual(
                db=db,
                company_id=company_id,
                created_by=created_by,
                entity_id=new_product.id,
                entity_type=MovementEntityType.PRODUCT,
                movement_type=MovementType.CREATION,
                description=f"Produto criado: {new_product.name}",
                ip_address=ip_address
            )
            
        except IntegrityError:
            db.rollback()
            raise ValueError("Falha ao criar o produto.")
        return new_product

    @staticmethod
    def update_product(
        db: Session, 
        product_id: UUID, 
        company_id: UUID | None,
        updated_by: UUID, 
        data: ProductUpdate,
        ip_address: str | None = None
    ):
        product = ProductService.get_product_by_id_and_company(
            db=db,
            product_id=product_id,
            company_id=company_id
        )

        if data.sku and data.sku != product.sku:

            target_company_id = product.company_id

            sku_exists = db.query(Product).filter(
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

        db.commit()
        db.refresh(product)
        
        # Registrar movimento de atualização
        MovementService.create_manual(
            db=db,
            company_id=company_id,
            created_by=updated_by,
            entity_id=product.id,
            entity_type=MovementEntityType.PRODUCT,
            movement_type=MovementType.UPDATED,
            description=f"Produto atualizado: {product.name}",
            ip_address=ip_address
        )
        
        return product

    @staticmethod
    def deactivate_product(
        db: Session, 
        product_id: UUID, 
        company_id: UUID | None,
        updated_by: UUID,
        ip_address: str | None = None # <--- Recebe IP
    ):
        product = ProductService.get_product_by_id_and_company(
            db=db,
            product_id=product_id,
            company_id=company_id
        )
        if not product:
            raise ValueError("Produto não encontrado.")

        product.is_active = False
        product.updated_by = updated_by
        product.updated_at = func.now()

        db.commit()
        db.refresh(product)

        # REGISTRA MOVIMENTO
        MovementService.create_manual(
            db=db,
            company_id=product.company_id,
            created_by=updated_by,
            entity_id=product.id,
            entity_type=MovementEntityType.PRODUCT,
            movement_type=MovementType.DEACTIVATED,
            description=f"Produto desativado: {product.name}",
            ip_address=ip_address
        )

        return product

    @staticmethod
    def activate_product(
        db: Session, 
        product_id: UUID, 
        company_id: UUID | None, 
        updated_by: UUID, 
        ip_address: str | None = None
    ):
        product = ProductService.get_product_by_id_and_company(
            db=db,
            product_id=product_id,
            company_id=company_id
        )
        if not product:
            raise ValueError("Produto não encontrado.")
        
        product.is_active = True
        product.updated_by = updated_by
        product.updated_at = func.now()

        db.commit()
        db.refresh(product)

        # REGISTRA MOVIMENTO
        MovementService.create_manual(
            db=db,
            company_id=product.company_id,
            created_by=updated_by,
            entity_id=product.id,
            entity_type=MovementEntityType.PRODUCT,
            movement_type=MovementType.ACTIVATED,
            description=f"Produto ativado: {product.name}",
            ip_address=ip_address
        )

        return product
    
    @staticmethod
    def delete_product(
        db: Session, 
        product_id: UUID, 
        company_id: UUID | None,
        ip_address: str | None = None
    ):
        product = ProductService.get_product_by_id_and_company(
            db=db,
            product_id=product_id,
            company_id=company_id
        )

        if not product:
            raise ValueError("Produto não encontrado.")
        
        db.delete(product)
        db.commit()

        # REGISTRA MOVIMENTO
        MovementService.create_manual(
            db=db,
            company_id=product.company_id,
            created_by=None,  # Sistema
            entity_id=product.id,
            entity_type=MovementEntityType.PRODUCT,
            movement_type=MovementType.DELETED,
            description=f"Produto deletado: {product.name}",
            ip_address=ip_address
        )

        return alert(f"Produto {product.name} deletado com sucesso.")
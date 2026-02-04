# Importações externas
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

# Importações internas
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

# Serviço de Produtos
class ProductService:
    '''Serviço para gerenciar produtos
    
    Responsabilidades:
    - Listar produtos
    - Obter produto por ID
    - Criar produto com validação de SKU único por empresa
    - Atualizar produto com validação de SKU único
    - Ativar/Desativar produto (soft delete)
    '''

    @staticmethod
    def list_products(db: Session, company_id: UUID | None = None):
        '''Lista todos os produtos ativos de uma empresa
        
        Args:
            db (Session): Sessão do banco de dados
            company_id (UUID): ID da empresa
        Returns:
            List[Product]: Lista de produtos ativos
        '''
        query = db.query(Product).options(joinedload(Product.company))
        if company_id:
            query = query.filter(Product.company_id == company_id)
        # Lista apenas produtos ativos
        return query.filter(
            Product.is_active == True
        ).all()

    @staticmethod
    def get_by_id(db: Session, product_id: UUID, company_id: UUID):
        '''Retorna um produto por ID e empresa
        
        Args:
            db (Session): Sessão do banco de dados
            product_id (UUID): ID do produto
            company_id (UUID): ID da empresa
        Returns:
            Product: Produto encontrado
        '''
        # Busca o produto pelo ID e empresa
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()

        # Valida se o produto existe
        if not product:
            raise ValueError("Product not found.")
        return product

    @staticmethod
    def create_product(db: Session, company_id: UUID, created_by: UUID, data: ProductCreate):
        '''Cria um novo produto, validando SKU único por empresa
        
        Args:
            db (Session): Sessão do banco de dados
            company_id (UUID): ID da empresa
            created_by (UUID): ID do usuário que criou o produto
            data (ProductCreate): Dados do produto a ser criado
        Returns:
            Product: Produto criado
        '''
        # Valida SKU único
        if data.sku:
            sku_exists = db.query(Product).filter(
                Product.sku == data.sku,
                Product.company_id == company_id
            ).first()
            # Se SKU já existe, lança erro
            if sku_exists:
                raise ValueError("SKU already exists for this company.")

        # Cria o novo produto
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
        # Adiciona e comita o novo produto
        db.add(new_product)
        try:
            db.commit()
            db.refresh(new_product)
        # Trata erros de integridade    
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create product.")
        return new_product

    @staticmethod
    def update_product(db: Session, product_id: UUID, company_id: UUID, updated_by: UUID, data: ProductUpdate):
        '''Atualiza um produto, garantindo SKU único
        Args:
            db (Session): Sessão do banco de dados
            product_id (UUID): ID do produto a ser atualizado
            company_id (UUID): ID da empresa
            updated_by (UUID): ID do usuário que está atualizando o produto
            data (ProductUpdate): Dados para atualização do produto
        Returns:
            Product: Produto atualizado
        '''
        # Busca o produto existente
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()
        # Valida se o produto existe
        if not product:
            raise ValueError("Product not found.")

        # Valida SKU único se for alterado
        if data.sku and data.sku != product.sku:
            sku_exists = db.query(Product).filter(
                Product.sku == data.sku,
                Product.company_id == company_id,
                Product.id != product_id
            ).first()
            if sku_exists:
                raise ValueError("SKU already exists for this company.")

        # Atualiza campos
        product.name = data.name or product.name
        product.sku = data.sku or product.sku
        product.price = data.price if data.price is not None else product.price
        product.quantity = data.quantity if data.quantity is not None else product.quantity
        product.description = data.description or product.description
        product.updated_by = updated_by
        product.updated_at = func.now()

        # Comita as alterações
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def deactivate_product(db: Session, product_id: UUID, company_id: UUID, updated_by: UUID):
        '''Desativa um produto (soft delete)
        
        Args:
            db (Session): Sessão do banco de dados
            product_id (UUID): ID do produto
            company_id (UUID): ID da empresa
            updated_by (UUID): ID do usuário que está desativando o produto
        Returns:
            Product: Produto desativado
        '''
        # Busca o produto existente
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()
        # Valida se o produto existe
        if not product:
            raise ValueError("Product not found.")

        # Desativa o produto
        product.is_active = False
        product.updated_by = updated_by
        product.updated_at = func.now()

        # Comita as alterações
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def activate_product(db: Session, product_id: UUID, company_id: UUID, updated_by: UUID):
        '''Ativa um produto
        
        Args:
            db (Session): Sessão do banco de dados
            product_id (UUID): ID do produto
            company_id (UUID): ID da empresa
            updated_by (UUID): ID do usuário que está ativando o produto
        Returns:
            Product: Produto ativado
        '''
        # Busca o produto existente
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()
        # Valida se o produto existe
        if not product:
            raise ValueError("Product not found.")
        
        # Ativa o produto
        product.is_active = True
        product.updated_by = updated_by
        product.updated_at = func.now()

        # Comita as alterações
        db.commit()
        db.refresh(product)
        return product
# Importação padrão
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timezone

# Importação interna
from app.models.product import Product

# Repositório de Produtos
class ProductRepository:
    '''Repositório para operações relacionadas a Produtos.

    Métodos:
        - create: Cria um novo produto.
        - get_by_id: Obtém um produto por ID.
        - list_by_company: Lista produtos por ID da empresa.
        - update: Atualiza um produto existente.
        - delete: Remove um produto.
    '''

    @staticmethod
    def create(
        db: Session,
        *,
        name: str,
        description: str | None,
        sku: str | None = None,
        price: float,
        company_id: uuid.UUID,
        created_by: uuid.UUID | None = None,
        created_at: datetime | None = None
    ) -> Product:
        '''Cria um novo produto no banco de dados.

        Parâmetros:
            - db: Sessão do banco de dados.
            - name: Nome do produto.
            - description: Descrição do produto (opcional).
            - sku: SKU do produto (opcional).
            - price: Preço do produto.
            - company_id: ID da empresa associada ao produto.
            - created_by: ID do usuário que criou o produto (opcional).
            - created_at: Data e hora de criação do produto (opcional).
        '''
        product = Product(
            name=name,
            description=description,
            sku=sku,
            price=price,
            company_id=company_id,
            created_by=created_by,
            created_at=created_at or datetime.now(timezone.utc)
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def get_by_id(
        db: Session,
        product_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> Product | None:
        '''Obtém um produto por ID e ID da empresa.
        
        Parâmetros:
            - db: Sessão do banco de dados.
            - product_id: ID do produto.
            - company_id: ID da empresa associada ao produto.
        '''
        return (
            db.query(Product)
            .filter(
                Product.id == product_id,
                Product.company_id == company_id,
            )
            .first()
        )

    @staticmethod
    def list_by_company(
        db: Session,
        company_id: uuid.UUID,
    ) -> list[Product]:
        '''Lista produtos por ID da empresa.

        Parâmetros:
            - db: Sessão do banco de dados.
            - company_id: ID da empresa associada aos produtos.
        '''
        return (
            db.query(Product)
            .filter(Product.company_id == company_id)
            .order_by(Product.created_at.desc())
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        *,
        product: Product,
        name: str | None = None,
        description: str | None = None,
    ) -> Product:
        '''Atualiza um produto existente no banco de dados.

        Parâmetros:
            - db: Sessão do banco de dados.
            - product: Instância do produto a ser atualizada.
            - name: Novo nome do produto (opcional).
            - description: Nova descrição do produto (opcional).
        '''
        if name is not None:
            product.name = name

        if description is not None:
            product.description = description

        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def delete(
        db: Session,
        *,
        product: Product,
    ) -> None:
        '''Remove um produto do banco de dados.

        Parâmetros:
            - db: Sessão do banco de dados.
            - product: Instância do produto a ser removida.
        '''
        db.delete(product)
        db.commit()
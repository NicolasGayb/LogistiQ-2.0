from uuid import UUID
from sqlalchemy.orm import Session

from app.models.enum import MovementEntityType, MovementType
from app.repositories.product_repository import ProductRepository
from app.services.movement_service import MovementService
from app.models.product import Product


class ProductService:

    @staticmethod
    def create_product(
        db: Session,
        *,
        name: str,
        description: str | None,
        sku: str | None = None,
        price: float,
        company_id: UUID,
        created_by: UUID | None = None,
        register_movement: bool = True,
    ):
        # Cria o produto via repository
        product = ProductRepository.create(
            db=db,
            name=name,
            description=description,
            sku=sku,
            price=price,
            company_id=company_id,
            created_by=created_by,
        )

        # Registra movimento automaticamente
        if register_movement:
            MovementService.register_event(
                db=db,
                entity_type=MovementEntityType.PRODUCT,
                entity_id=product.id,
                company_id=company_id,
                movement_type=MovementType.PRODUCT_CREATED,
                description="Produto cadastrado",
                created_by=created_by,
            )

        return product

    @staticmethod
    def update_product(
        db: Session,
        *,
        product_id: UUID,
        company_id: UUID,
        name: str | None = None,
        description: str | None = None,
        updated_by: UUID | None = None,
        register_movement: bool = True,
    ):
        # Busca o produto
        product = ProductRepository.get_by_id(
            db=db,
            product_id=product_id,
            company_id=company_id
        )
        if not product:
            raise ValueError("Produto não encontrado")

        # Atualiza via repository
        product = ProductRepository.update(
            db=db,
            product=product,
            name=name,
            description=description,
        )

        # Registra movimento
        if register_movement:
            MovementService.register_event(
                db=db,
                entity_type=MovementEntityType.PRODUCT,
                entity_id=product.id,
                company_id=company_id,
                movement_type=MovementType.PRODUCT_UPDATED,
                description="Produto atualizado",
                created_by=updated_by,
            )

        return product

    @staticmethod
    def delete_product(
        db: Session,
        *,
        product_id: UUID,
        company_id: UUID,
        deleted_by: UUID | None = None,
        register_movement: bool = True,
    ):
        # Busca o produto
        product = ProductRepository.get_by_id(
            db=db,
            product_id=product_id,
            company_id=company_id
        )
        if not product:
            raise ValueError("Produto não encontrado")

        # Deleta via repository
        ProductRepository.delete(db=db, product=product)

        # Registra movimento
        if register_movement:
            MovementService.register_event(
                db=db,
                entity_type=MovementEntityType.PRODUCT,
                entity_id=product.id,
                company_id=company_id,
                movement_type=MovementType.PRODUCT_DELETED,
                description="Produto deletado",
                created_by=deleted_by,
            )

    @staticmethod
    def list_products(
        db: Session,
        *,
        company_id: UUID
    ) -> list[Product]:
        """Lista todos os produtos de uma empresa."""
        return ProductRepository.list_by_company(
            db=db,
            company_id=company_id
        )
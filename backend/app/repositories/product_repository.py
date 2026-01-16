import uuid
from sqlalchemy.orm import Session
from app.models.product import Product
from datetime import datetime, timezone

class ProductRepository:

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
        db.delete(product)
        db.commit()
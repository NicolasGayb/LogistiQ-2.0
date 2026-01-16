from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    @staticmethod
    def list_products(db: Session, company_id: UUID):
        """Lista todos os produtos ativos da empresa"""
        return db.query(Product).filter(
            Product.company_id == company_id,
            Product.is_active == True
        ).all()

    @staticmethod
    def get_by_id(db: Session, product_id: UUID, company_id: UUID):
        """Retorna um produto por ID e empresa"""
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()
        if not product:
            raise ValueError("Product not found.")
        return product

    @staticmethod
    def create_product(db: Session, company_id: UUID, created_by: UUID, data: ProductCreate):
        """Cria um novo produto, validando SKU único por empresa"""
        if data.sku:
            sku_exists = db.query(Product).filter(
                Product.sku == data.sku,
                Product.company_id == company_id
            ).first()
            if sku_exists:
                raise ValueError("SKU already exists for this company.")

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
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create product.")
        return new_product

    @staticmethod
    def update_product(db: Session, product_id: UUID, company_id: UUID, updated_by: UUID, data: ProductUpdate):
        """Atualiza um produto, garantindo SKU único"""
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()
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

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def deactivate_product(db: Session, product_id: UUID, company_id: UUID, updated_by: UUID):
        """Desativa um produto (soft delete)"""
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()
        if not product:
            raise ValueError("Product not found.")

        product.is_active = False
        product.updated_by = updated_by
        product.updated_at = func.now()

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def activate_product(db: Session, product_id: UUID, company_id: UUID, updated_by: UUID):
        """Ativa um produto"""
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.company_id == company_id
        ).first()
        if not product:
            raise ValueError("Product not found.")
        product.is_active = True
        product.updated_by = updated_by
        product.updated_at = func.now()
        db.commit()
        db.refresh(product)
        return product
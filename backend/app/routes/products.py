from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/")
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ProductService.list_products(db=db, company_id=current_user.company_id)


@router.post("/")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_product = ProductService.create_product(
        db=db,
        name=product.name,
        sku=product.sku,
        price=product.price,
        description=product.description,
        company_id=current_user.company_id,
        created_by=current_user.id
    )
    return new_product


@router.put("/{product_id}")
def update_product(
    product_id: str,  # use UUID
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated_product = ProductService.update_product(
            db=db,
            product_id=product_id,
            company_id=current_user.company_id,
            name=product_data.name,
            description=product_data.description,
            sku=product_data.sku,
            price=product_data.price,
            updated_by=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return updated_product


@router.delete("/{product_id}")
def delete_product(
    product_id: str,  # use UUID
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        ProductService.delete_product(
            db=db,
            product_id=product_id,
            company_id=current_user.company_id,
            deleted_by=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"detail": f"Product with id {product_id} has been deleted."}
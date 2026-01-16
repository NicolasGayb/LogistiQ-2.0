from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.enum import UserRole
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get(
    "",
    status_code=status.HTTP_200_OK
)
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProductService.list_products(
        db=db,
        company_id=current_user.company_id
    )


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK
)
def get_product_by_id(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ProductService.get_by_id(
            db=db,
            product_id=product_id,
            company_id=current_user.company_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ProductService.create_product(
            db=db,
            company_id=current_user.company_id,
            created_by=current_user.id,
            data=product
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@router.put(
    "/{product_id}",
    status_code=status.HTTP_200_OK
)
def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ProductService.update_product(
            db=db,
            product_id=product_id,
            company_id=current_user.company_id,
            updated_by=current_user.id,
            data=product_data
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.patch(
    "/{product_id}/deactivate",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))]
)
def deactivate_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        ProductService.deactivate_product(
            db=db,
            product_id=product_id,
            company_id=current_user.company_id,
            deactivated_by=current_user.id
        )
        return {"detail": f"Product {product_id} has been deactivated."}
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
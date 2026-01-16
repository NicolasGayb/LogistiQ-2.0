from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.enum import UserRole
from app.database import get_db
from app.core.dependencies import check_admin_or_manager, get_current_user, require_roles
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


# -------------------- Listagem de produtos --------------------
@router.get("/")
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ProductService.list_products(db=db, company_id=current_user.company_id)


# -------------------- GET por ID --------------------
@router.get("/{product_id}")
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return ProductService.get_by_id(
            db=db, product_id=product_id, company_id=current_user.company_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -------------------- Criação de produto --------------------
@router.post(
        "/",
        status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_product = ProductService.create_product(
            db=db,
            company_id=current_user.company_id,
            created_by=current_user.id,
            data=product
        )
        return new_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------- Atualização de produto --------------------
@router.put("/{product_id}")
def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated_product = ProductService.update_product(
            db=db,
            product_id=product_id,
            company_id=current_user.company_id,
            updated_by=current_user.id,
            data=product_data
        )
        return updated_product
    except ValueError as e:
        msg = str(e)
        if "SKU already exists" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=404, detail=msg)


# -------------------- Toggle de ativação/desativação --------------------
from fastapi import Depends
from app.models.enum import UserRole
from app.core.dependencies import require_roles

@router.patch("/{product_id}/toggle")
def toggle_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_or_manager),
):
    """
    Ativa ou desativa um produto dependendo do seu estado atual.
    Apenas ADMIN e MANAGER podem realizar a ação.
    """
    try:
        # só chega aqui se tiver permissão
        product = ProductService.get_by_id(
            db=db, product_id=product_id, company_id=current_user.company_id
        )

        if product.is_active:
            return ProductService.deactivate_product(
                db=db,
                product_id=product_id,
                company_id=current_user.company_id,
                updated_by=current_user.id
            )
        else:
            return ProductService.activate_product(
                db=db,
                product_id=product_id,
                company_id=current_user.company_id,
                updated_by=current_user.id
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
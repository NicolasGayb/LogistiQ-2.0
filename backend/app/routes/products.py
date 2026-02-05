# Importações externas
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

# Importações internas
from app.models.enum import UserRole
from app.database import get_db
from app.core.dependencies import check_admin_or_manager, get_current_user, require_roles
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.services.product_service import ProductService
from app.core.utils import get_real_ip

router = APIRouter(prefix="/products", tags=["Products"])

# --------------------------------------------------
# GET products
# --------------------------------------------------
@router.get("/", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Lista todos os produtos associados à empresa do usuário autenticado.

    Parâmetros:
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.
    Retorna:
    - Lista de produtos da empresa do usuário autenticado.
    '''
    if current_user.role in [UserRole.SYSTEM_ADMIN]:
        return ProductService.list_products(db=db)
    return ProductService.list_products(db=db, company_id=current_user.company_id)

@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Obtém os detalhes de um produto específico.

    Parâmetros:
    - `product_id`: ID do produto a ser obtido.
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.
    Retorna:
    - Detalhes do produto solicitado.
    '''
    try:
        return ProductService.get_by_id(
            db=db, product_id=product_id, company_id=current_user.company_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --------------------------------------------------
# POST products
# --------------------------------------------------
@router.post(
        "/",
        status_code=status.HTTP_201_CREATED,
        response_model=ProductOut
)
def create_product(
    product: ProductCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Cria um novo produto.

    Parâmetros:
    - `product`: Dados do produto a ser criado.
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.
    Retorna:
    - O produto criado.
    '''
    try:
        new_product = ProductService.create_product(
            db=db,
            company_id=current_user.company_id,
            created_by=current_user.id,
            data=product,
            ip_address=get_real_ip(request)
        )
        return new_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --------------------------------------------------
# PUT products
# --------------------------------------------------
@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Atualiza os detalhes de um produto existente.
    
    Parâmetros:
    - `product_id`: ID do produto a ser atualizado.
    - `product_data`: Dados atualizados do produto.
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.
    Retorna:
    - O produto atualizado.'''
    target_company_id = current_user.company_id
    if current_user.role == UserRole.SYSTEM_ADMIN:
        target_company_id = None  # System Admin pode atualizar qualquer produto
    try:
        updated_product = ProductService.update_product(
            db=db,
            product_id=product_id,
            company_id=target_company_id,
            updated_by=current_user.id,
            data=product_data,
            ip_address=get_real_ip(request)
        )
        return updated_product
    except ValueError as e:
        msg = str(e)
        if "SKU already exists" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=404, detail=msg)

# --------------------------------------------------
# PATCH products
# --------------------------------------------------

@router.patch("/{product_id}/toggle", response_model=ProductOut)
def toggle_product(
    product_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]) or check_admin_or_manager)
):
    """
    Ativa ou desativa um produto dependendo do seu estado atual.
    Apenas ADMIN, MANAGER e SYSTEM_ADMIN podem realizar a ação.

    Parâmetros:
    - `product_id`: ID do produto a ser ativado/desativado.
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.

    Retorna:
    - O produto atualizado com o novo estado de ativação.
    """
    target_company_id = current_user.company_id
    if current_user.role == UserRole.SYSTEM_ADMIN:
        target_company_id = None  # System Admin pode ativar/desativar qualquer produto
    try:
        # só chega aqui se tiver permissão
        product = ProductService.get_by_id(
            db=db, product_id=product_id, company_id=target_company_id
        )

        if product.is_active:
            return ProductService.deactivate_product(
                db=db,
                product_id=product_id,
                company_id=target_company_id,
                updated_by=current_user.id,
                ip_address=get_real_ip(request)
            )
        else:
            return ProductService.activate_product(
                db=db,
                product_id=product_id,
                company_id=target_company_id,
                updated_by=current_user.id,
                ip_address=get_real_ip(request)
            )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
# --------------------------------------------------
# DELETE products
# --------------------------------------------------
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Remove um produto (Logical Delete ou Físico, depende do Service).
    
    Parâmetros:
    - `product_id`: ID do produto a ser removido.
    - `db`: Sessão do banco de dados.
    - `current_user`: Usuário autenticado.
    Retorna:
    - Nenhum conteúdo (204 No Content) se a remoção for bem-sucedida.
    '''
    target_company_id = current_user.company_id
    if current_user.role == UserRole.SYSTEM_ADMIN:
        target_company_id = None  # System Admin pode deletar qualquer produto
    try:
        ProductService.delete_product(
            db=db, 
            product_id=product_id, 
            company_id=target_company_id,
            ip_address=get_real_ip(request)
        )
        return None # 204 não retorna corpo
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
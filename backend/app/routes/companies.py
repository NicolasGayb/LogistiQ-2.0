import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.company import CompanyNameUpdate, CompanyWithAdminCreate, CompanyResponse
from app.models.enum import UserRole
from app.models import Company, User
from app.database import get_db
from app.core.dependencies import require_roles
from app.core.security import hash_password

router = APIRouter(prefix="/companies", tags=["Companies"])

# ------------------------
# POST Companies
# ------------------------
@router.post(
    "/", 
    response_model=CompanyResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_company(
    data: CompanyWithAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    """Cria uma nova empresa com um usuário administrador associado.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Valida se a empresa já existe.
    - Valida se o email do administrador já está em uso.
    - Cria a empresa e o usuário administrador.
    
    Args:
        data (CompanyWithAdminCreate): Dados da empresa e do administrador.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.    
    Returns:
        CompanyResponse: Dados da empresa criada.
    """
    # Valida empresa duplicada pelo nome
    existing_company = db.query(Company).filter(
        Company.name == data.company.name
    ).first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa já cadastrada"
        )
    
    # Valida empresa duplicada pelo cnpj
    if data.company.cnpj:
        existing_company = db.query(Company).filter(
            Company.cnpj == data.company.cnpj
        ).first()

        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado"
            )

    # Valida email do admin
    existing_admin = db.query(User).filter(
        User.email == data.admin_email
    ).first()

    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email do administrador já existe"
        )

    try:
        # Cria empresa
        company = Company(
            name=data.company.name,
            cnpj=data.company.cnpj
        )
        db.add(company)
        db.flush()  # pega company.id sem commit

        # Cria ADMIN da empresa
        admin = User(
            name=data.admin_name,
            email=data.admin_email,
            password_hash=hash_password(data.admin_password),
            role=UserRole.ADMIN,
            company_id=company.id
        )

        db.add(admin)
        db.commit()
        db.refresh(company)

        return company

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar empresa"
        )

# ------------------------
# GET Companies
# ------------------------
@router.get("/me", response_model=CompanyResponse)
def get_my_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER, UserRole.SYSTEM_ADMIN]))
):
    """Recupera os dados da empresa do usuário autenticado.
    
    - Requer permissão de ADMIN, MANAGER ou SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        Company: Instância da empresa.
    """
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    return company

@router.get("/me/users")
def get_my_company_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER, UserRole.SYSTEM_ADMIN])
    )
):
    """"""
    query = db.query(User)

    match current_user.role:
        case UserRole.SYSTEM_ADMIN:
            pass  # system admin vê todos os usuários
        case UserRole.ADMIN:
            query = query.filter(User.company_id == current_user.company_id)
        case UserRole.MANAGER:
            query = query.filter(
                User.company_id == current_user.company_id,
                User.role != UserRole.ADMIN
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )
        
    return query.all()

@router.get("/list", response_model=list[CompanyResponse])
def list_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
) -> list[Company]:
    """Lista todas as empresas.
    
    - Requer permissão de SYSTEM_ADMIN.
    
    Args:
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        list[Company]: Lista de instâncias de empresas.
    """
    companies = db.query(Company).all()
    return companies

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company_by_id(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
) -> Company:
    """Recupera uma empresa pelo ID.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_id (uuid.UUID): ID da empresa.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        Company: Instância da empresa.
    """
        
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    return company

# ------------------------
# PUT Companies
# ------------------------
@router.put("/me", response_model=CompanyResponse)
def update_my_company(
    data: CompanyNameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SYSTEM_ADMIN]))
) -> Company:
    """Atualiza os dados da empresa do usuário autenticado.
    
    - Requer permissão de ADMIN ou SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        data (CompanyNameUpdate): Dados atualizados da empresa.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        Company: Instância da empresa atualizada.
    """
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    if current_user.role == UserRole.ADMIN and company.id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    
    try:
        if data.name is not None:
            company.name = data.name
        
        db.commit()
        db.refresh(company)
        return company
    
    except HTTPException:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar empresa"
        )

@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: uuid.UUID,
    data: CompanyNameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
) -> Company:
    """Atualiza os dados de uma empresa existente.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_id (uuid.UUID): ID da empresa a ser atualizada.
        data (CompanyNameUpdate): Dados atualizados da empresa.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        Company: Instância da empresa atualizada.
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    try:
        if data.name is not None:
            company.name = data.name

        db.commit()
        db.refresh(company)

        return company

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar empresa"
        )
    


# ------------------------
# PATCH Companies
# ------------------------
@router.patch("/{company_id}/deactivate", response_model=CompanyResponse)
def deactivate_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    """Desativa uma empresa pelo ID.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_id (uuid.UUID): ID da empresa a ser desativada.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    """

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )

    company.is_active = not company.is_active
    db.commit()
    db.refresh(company)
    return company

# ------------------------
# DELETE Companies
# ------------------------
@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    """Deleta uma empresa pelo ID.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_id (uuid.UUID): ID da empresa a ser deletada.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    """

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    try:
        db.delete(company)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar empresa"
        )
import uuid
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.company import CompanyNameUpdate, CompanyWithAdminCreate, CompanyResponse, DashboardStatsResponse
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
    summary="Cria uma nova empresa com um usuário administrador.",
    description="Cria uma nova empresa e um usuário administrador associado a ela.",
    responses={
        201: {"model": CompanyResponse, "description": "Empresa criada com sucesso."},
        400: {"description": "Requisição inválida ou empresa já existe."},
        403: {"description": "Permissão negada."},
        500: {"description": "Erro interno do servidor ao criar empresa."}
    },
    response_model=CompanyResponse, 
    status_code=status.HTTP_201_CREATED
)
def create_company(
    data: CompanyWithAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
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
            cnpj=data.company.cnpj,
            token=secrets.token_urlsafe(16)
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
    """
    Recupera os usuários da empresa do usuário autenticado.

    - Requer permissão de ADMIN, MANAGER ou SYSTEM_ADMIN.
    - Lança erro se o usuário não tiver permissão.
    Args:
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        list[User]: Lista de instâncias de usuários.
    """
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

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
) -> DashboardStatsResponse:
    '''Recupera estatísticas do dashboard.
    
    - Requer permissão de SYSTEM_ADMIN.
    
    Args:
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        DashboardStatsResponse: Estatísticas do dashboard.
    '''
    
    # 1. Faz a contagem no banco
    count_companies = db.query(Company).count()
    count_users = db.query(User).count()
    
    # 2. Define o status (pode evoluir essa lógica depois)
    status_msg = "Operacional"

    # 3. Retorna usando os nomes exatos do Schema
    return DashboardStatsResponse(
        companies_count=count_companies,
        users_count=count_users,
        system_status=status_msg
    )

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company_by_id(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
) -> Company:
    '''Recupera uma empresa pelo ID.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_id (uuid.UUID): ID da empresa.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        Company: Instância da empresa.
    '''
        
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    
    return company

@router.get("/cnpj/{company_cnpj}", response_model=CompanyResponse)
def get_company_by_cnpj(
    company_cnpj: str,
    db: Session = Depends(get_db),
) -> Company:
    '''Recupera uma empresa pelo CNPJ.
    
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_cnpj (str): CNPJ da empresa.
        db (Session): Sessão do banco de dados.
    Returns:
        Company: Instância da empresa.
    '''
        
    company = db.query(Company).filter(Company.cnpj == company_cnpj).first()
    
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
    '''Atualiza os dados da empresa do usuário autenticado.
    
    - Requer permissão de ADMIN ou SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        data (CompanyNameUpdate): Dados atualizados da empresa.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        Company: Instância da empresa atualizada.
    '''
    
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
    '''Atualiza os dados de uma empresa existente.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_id (uuid.UUID): ID da empresa a ser atualizada.
        data (CompanyNameUpdate): Dados atualizados da empresa.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        Company: Instância da empresa atualizada.
    '''
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
@router.patch("/toggle-company/{company_id}", response_model=CompanyResponse)
def toggle_company_status(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
) -> Company:
    '''Ativa ou desativa uma empresa pelo ID.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_id (uuid.UUID): ID da empresa a ser ativada/desativada.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    Returns:
        Company: Instância da empresa atualizada.
    '''
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa não encontrada"
        )
    try:
        company.is_active = not company.is_active
        db.commit()
        db.refresh(company)
        return company
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar status da empresa"
        )
    

# ------------------------
# DELETE Companies
# ------------------------
@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SYSTEM_ADMIN]))
):
    '''Deleta uma empresa pelo ID.
    
    - Requer permissão de SYSTEM_ADMIN.
    - Lança erro se a empresa não for encontrada.
    
    Args:
        company_id (uuid.UUID): ID da empresa a ser deletada.
        db (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado.
    '''

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
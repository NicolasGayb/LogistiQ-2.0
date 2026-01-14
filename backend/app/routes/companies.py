from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.company import CompanyWithAdminCreate, CompanyResponse
from app.models.enum import UserRole
from app.models import Company, User
from app.database import get_db
from app.core.dependencies import require_roles
from app.core.security import hash_password

router = APIRouter(prefix="/companies", tags=["Companies"])

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
    # 🔎 Valida empresa duplicada
    existing_company = db.query(Company).filter(
        Company.name == data.company.name
    ).first()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa já cadastrada"
        )

    # 🔎 Valida email do admin
    existing_admin = db.query(User).filter(
        User.email == data.admin_email
    ).first()

    if existing_admin:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Email do administrador já existe"
        )

    try:
        # 🏗️ Cria empresa
        company = Company(
            name=data.company.name,
            cnpj=data.company.cnpj
        )
        db.add(company)
        db.flush()  # pega company.id sem commit

        # 👤 Cria ADMIN da empresa
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

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar empresa"
        )
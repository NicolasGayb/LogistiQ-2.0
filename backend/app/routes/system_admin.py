# app/api/routes/system_admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import SystemAdminCreate
from app.services.system_admin_service import create_system_admin
from app.repositories.user_repository import get_user_by_email

router = APIRouter(prefix="/system-admins", tags=["System Admins"])

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_system_admin_endpoint(
    payload: SystemAdminCreate,
    db: Session = Depends(get_db),
):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado"
        )

    user = create_system_admin(
        db=db,
        name=payload.name,
        email=payload.email,
        password=payload.password
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
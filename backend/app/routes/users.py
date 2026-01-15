from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import require_roles
from app.models.enum import UserRole
from app.models import User
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRole.SYSTEM_ADMIN, 
            UserRole.ADMIN, 
            UserRole.MANAGER]
        )
    )
):
    
    if current_user.role == UserRole.SYSTEM_ADMIN:
        return db.query(User).all()
    
    if current_user.role == UserRole.ADMIN:
        return db.query(User).filter(
            User.company_id == current_user.company_id
        ).all() 
    
    if current_user.role == UserRole.MANAGER:
        return db.query(User).filter(
            User.company_id == current_user.company_id,
            User.role != UserRole.ADMIN
        ).all()

@router.put("/update-user/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRole.SYSTEM_ADMIN, 
            UserRole.ADMIN, 
            UserRole.MANAGER]
        )
    )
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if current_user.role == UserRole.ADMIN:
        if user.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
        
    if data.name:
        user.name = data.name
    if data.role:
        user.role = data.role

    db.commit()
    db.refresh(user)
    return user

@router.delete("/delete-user/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRole.SYSTEM_ADMIN]
        )
    )
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    return f"User with ID {user_id} has been deleted."

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            [UserRole.SYSTEM_ADMIN, 
            UserRole.ADMIN, 
            UserRole.MANAGER]
        )
    )
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if current_user.role == UserRole.ADMIN:
        if user.company_id != current_user.company_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
    
    if current_user.role == UserRole.MANAGER:
        if user.company_id != current_user.company_id or user.role == UserRole.ADMIN:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
        
    return user
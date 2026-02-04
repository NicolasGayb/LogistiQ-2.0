from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.product import Product
from app.schemas.dashboard import AdminDashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/admin-stats", response_model=AdminDashboardStats)
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Dados Reais de Usuários (Da mesma empresa)
    total_users = db.query(User).filter(User.company_id == current_user.company_id).count()
    active_users = db.query(User).filter(
        User.company_id == current_user.company_id, 
        User.is_active == True
    ).count()

    # 2. Dados de Estoque (Lógica)
    # Precisamos saber qual é o limite de alerta da empresa
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    alert_limit = company.stock_alert_limit if company else 10
    
    low_stock_count = db.query(Product).filter(
        Product.company_id == current_user.company_id,
        Product.quantity <= alert_limit
    ).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "stock_alerts": low_stock_count,
        "low_stock_items": low_stock_count
    }
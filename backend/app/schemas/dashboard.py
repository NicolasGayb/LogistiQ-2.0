from pydantic import BaseModel

# Esquema para as estatísticas do dashboard do administrador
class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    stock_alerts: int
    low_stock_items: int
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.database import engine
from app.models.base import Base
from app.routes import auth, products, users, companies, system_admin, operations, movements, dashboard

# =================================================================
# 1. Configuração do Caminho do Frontend (Dist)
# =================================================================
# O base_dir pega a pasta onde este arquivo main.py está (backend/app)
base_dir = os.path.dirname(os.path.abspath(__file__))
# Sobe um nível (..) para achar a dist
dist_dir = os.path.join(base_dir, "../dist")

# =================================================================
# 2. Ciclo de Vida (Lifespan)
# =================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Cria as tabelas do banco
    print("Iniciando tabelas do banco de dados...")
    
    print(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    yield

# =================================================================
# 3. Inicialização do App
# =================================================================
app = FastAPI(
    title="LogistiQ 2.0 API", 
    version="2.0.0", 
    description="API do sistema LogistiQ para gestão logística e controle por empresa.", 
    lifespan=lifespan,

    docs_url= None if os.getenv("ENV") == "production" else "/docs",
    redoc_url= None if os.getenv("ENV") == "production" else "/redoc",
    openapi_url= None if os.getenv("ENV") == "production" else "/openapi.json",
)

# =================================================================
# 4. Configuração CORS
# =================================================================
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://logistiq2-6fb648247d8f.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================================
# 5. Rotas da API (DEVEM vir antes dos arquivos estáticos)
# =================================================================
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(system_admin.router)
app.include_router(movements.router)
app.include_router(operations.router)
app.include_router(dashboard.router)

# =================================================================
# 6. Servindo o Frontend (React/Vite)
# =================================================================

if os.path.exists(dist_dir):
    # A. Monta a pasta de assets (JS, CSS, Imagens do Vite)
    # O Vite coloca tudo em dist/assets, então servimos em /assets
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # B. Rota "Catch-All" para SPA (Single Page Application)
    # Qualquer rota que NÃO for da API, cai aqui.
    # Se o arquivo existir (ex: favicon.ico), entrega ele.
    # Se não, entrega o index.html e deixa o React lidar com a rota.
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = os.path.join(dist_dir, full_path)
        
        # Se for um arquivo físico que existe, retorna ele
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Caso contrário, retorna o index.html (React Router assume)
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    print(f"⚠️ AVISO: Pasta 'dist' não encontrada em: {dist_dir}")
    print("O frontend não será carregado. Verifique se você moveu a pasta build/dist.")
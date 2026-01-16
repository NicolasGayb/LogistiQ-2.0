from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine
from app.models.base import Base
from app.routes import auth, products, users, companies, system_admin
from app.routes import operations
from app.routes import movements

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown code

app = FastAPI(title="LogistiQ 2.0 API", version="1.0.0", description="API do sistema LogistiQ para gestão logística e controle por empresa.", lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(system_admin.router)
app.include_router(movements.router)
app.include_router(operations.router)
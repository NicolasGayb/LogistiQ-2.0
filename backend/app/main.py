from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.models import Base
from app.routes import auth, products, users, companies, system_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown code

app = FastAPI(title="LogistiQ 2.0 API", version="1.0.0", description="API for LogistiQ 2.0 application", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(system_admin.router)
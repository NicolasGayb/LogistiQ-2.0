from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine
from app.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown code

app = FastAPI(title="LogistiQ 2.0 API", version="1.0.0", description="API for LogistiQ 2.0 application", lifespan=lifespan)
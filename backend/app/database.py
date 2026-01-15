from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
from dotenv import load_dotenv
from urllib.parse import quote_plus
import app.models
import os

load_dotenv()

# -------------------------
# Variáveis de ambiente
# -------------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Database environment variables are not properly set")

# -------------------------
# Encode da senha (CRÍTICO)
# -------------------------
DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD_ENCODED}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# -------------------------
# Engine
# -------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True
)

# -------------------------
# Session
# -------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# -------------------------
# Base
# -------------------------
Base = declarative_base()

# -------------------------
# Dependency
# -------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
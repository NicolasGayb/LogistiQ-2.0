from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# URL do banco (Heroku)
# -------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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

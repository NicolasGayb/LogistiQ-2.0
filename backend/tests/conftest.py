from datetime import datetime, timezone
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.base import Base
from app.database import get_db
from app.models.company import Company
from app.models.user import User
from app.models.movement import Movement
from app.core.security import hash_password as get_password_hash
from app.models.enum import MovementType, MovementEntityType, OperationStatus
from app.models.operation import Operation

# -------------------- Banco de teste --------------------
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -------------------- Fixture de criação de tabelas por teste --------------------
@pytest.fixture(autouse=True)
def create_tables():
    """Cria todas as tabelas antes de cada teste e limpa depois"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# -------------------- Fixture de session --------------------
@pytest.fixture()
def session(create_tables):
    db = TestingSessionLocal()
    try:
        # --- Criação de empresas ---
        company_a = Company(id=uuid.uuid4(), name="Company A", cnpj=str(12345678901234))
        company_b = Company(id=uuid.uuid4(), name="Company B", cnpj=str(23456789012345))
        db.add_all([company_a, company_b])
        db.commit()

        # --- Criação de usuários ---
        users = [
            User(
                id=uuid.uuid4(),
                name="Admin Test",
                email="admin@teste.com",
                password_hash=get_password_hash("123456"),
                role="SYSTEM_ADMIN",
                company_id=None
            ),
            User(
                id=uuid.uuid4(),
                name="User System A",
                email="systema@teste.com",
                password_hash=get_password_hash("123456"),
                role="SYSTEM_ADMIN",
                company_id=None
            ),
            User(
                id=uuid.uuid4(),
                name="User Admin A",
                email="a@teste.com",
                password_hash=get_password_hash("123456"),
                role="ADMIN",
                company_id=company_a.id
            ),
            User(
                id=uuid.uuid4(),
                name="User Admin B",
                email="b@teste.com",
                password_hash=get_password_hash("123456"),
                role="ADMIN",
                company_id=company_b.id
            ),
            User(
                id=uuid.uuid4(),
                name="User A",
                email="f@teste.com",
                password_hash=get_password_hash("123456"),
                role="USER",
                company_id=company_b.id
            ),
            User(
                id=uuid.uuid4(),
                name="User B",
                email="c@teste.com",
                password_hash=get_password_hash("123456"),
                role="USER",
                company_id=company_b.id
            ),
            User(
                id=uuid.uuid4(),
                name="Manager A",
                email="d@teste.com",
                password_hash=get_password_hash("123456"),
                role="MANAGER",
                company_id=company_a.id
            ),
            User(
                id=uuid.uuid4(),
                name="Manager B",
                email="e@teste.com",
                password_hash=get_password_hash("123456"),
                role="MANAGER",
                company_id=company_b.id
            ),
        ]
        db.add_all(users)
        db.commit()

        # --- Criação de movimentos ---
        movements = [
            Movement(
                id=uuid.uuid4(),
                company_id=company_a.id,
                entity_type=MovementEntityType.OPERATION,
                entity_id=uuid.uuid4(),
                type=MovementType.IN,
                previous_status=None,
                new_status=OperationStatus.LOADED,
                description="Entrada Company A",
                created_by=users[0].id
            ),
            Movement(
                id=uuid.uuid4(),
                company_id=company_a.id,
                entity_type=MovementEntityType.OPERATION,
                entity_id=uuid.uuid4(),
                type=MovementType.OUT,
                previous_status=None,
                new_status=OperationStatus.COMPLETED,
                description="Saída Company A",
                created_by=users[0].id
            ),
            Movement(
                id=uuid.uuid4(),
                company_id=company_b.id,
                entity_type=MovementEntityType.OPERATION,
                entity_id=uuid.uuid4(),
                type=MovementType.IN,
                previous_status=None,
                new_status=OperationStatus.IN_TRANSIT,
                description="Entrada Company B",
                created_by=users[2].id
            ),
        ]
        db.add_all(movements)
        db.commit()

        yield db
    finally:
        db.close()

# -------------------- Fixture de criação de operação --------------------
@pytest.fixture()
def create_operation(session):
    operation = Operation(
        id=uuid.uuid4(),
        company_id=session.query(Company).filter(Company.name == "Company B").first().id,
        status=OperationStatus.CREATED,
        product_id=uuid.uuid4(),
        updated_at=datetime.utcnow()
    )
    session.add(operation)
    session.commit()
    return operation

@pytest.fixture()
def create_operation_other_company(session):
    operation = Operation(
        id=uuid.uuid4(),
        company_id=session.query(Company).filter(Company.name == "Company A").first().id,
        status=OperationStatus.CREATED,
        product_id=uuid.uuid4(),
        updated_at=datetime.utcnow()
    )
    session.add(operation)
    session.commit()
    return operation

# -------------------- Cliente async para testes --------------------
@pytest.fixture()
def client(session):
    def override_get_db():
        yield session
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

# -------------------- Helper para token --------------------
@pytest.fixture()
def get_token(client):
    def _get_token(email="admin@teste.com", password="123456"):
        response = client.post(
            "/auth/login",
            data={"username": email, "password": password}
        )
        return response.json()["access_token"]
    return _get_token

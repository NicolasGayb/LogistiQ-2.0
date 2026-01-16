import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Product, User, Company
from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.enum import UserRole

# -------------------- Helper para criar payload --------------------
def make_product_payload(name="Produto Teste", sku="SKU123", price=100.0, quantity=10):
    return {
        "name": name,
        "sku": sku,
        "price": price,
        "description": f"Descrição {name}",
        "quantity": quantity,
        "is_active": True
    }

# -------------------- Criação de client --------------------
@pytest.fixture
def client(session):
    def override_get_db():
        yield session
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

# -------------------- Helper para token --------------------
@pytest.fixture
def get_token(client):
    def _get_token(email="admin@teste.com", password="123456"):
        response = client.post(
            "/auth/login",
            data={"username": email, "password": password}
        )
        return response.json()["access_token"]
    return _get_token

# -------------------- Testes de criação --------------------
def test_create_product(client, get_token):
    token = get_token("d@teste.com")  # Manager A

    payload = make_product_payload()
    resp = client.post("/products/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == payload["name"]
    assert data["sku"] == payload["sku"]
    assert data["quantity"] == payload["quantity"]
    assert data["is_active"] is True

# -------------------- Testes de toggle --------------------
def test_toggle_product_permissions(client, get_token):
    token_admin = get_token("d@teste.com")  # Manager A
    token_user = get_token("f@teste.com")   # User da mesma empresa
    payload = make_product_payload(sku="TOGGLESKU")
    
    # Cria produto
    resp = client.post("/products/", json=payload, headers={"Authorization": f"Bearer {token_admin}"})
    product_id = resp.json()["id"]

    # Tenta toggle com USER normal → 403
    resp_user = client.patch(f"/products/{product_id}/toggle", headers={"Authorization": f"Bearer {token_user}"})
    assert resp_user.status_code == 403

    # Toggle com ADMIN → deve desativar
    resp_toggle = client.patch(f"/products/{product_id}/toggle", headers={"Authorization": f"Bearer {token_admin}"})
    assert resp_toggle.status_code == 200
    assert resp_toggle.json()["is_active"] is False

    # Toggle de novo → ativa
    resp_toggle2 = client.patch(f"/products/{product_id}/toggle", headers={"Authorization": f"Bearer {token_admin}"})
    assert resp_toggle2.status_code == 200
    assert resp_toggle2.json()["is_active"] is True

# -------------------- Testes de SKU duplicado --------------------
def test_update_product_duplicate_sku(client, get_token):
    token = get_token("d@teste.com")  # Manager A
    # Cria 2 produtos
    payload1 = make_product_payload(name="Produto 1", sku="SKU1")
    payload2 = make_product_payload(name="Produto 2", sku="SKU2")

    resp1 = client.post("/products/", json=payload1, headers={"Authorization": f"Bearer {token}"})
    resp2 = client.post("/products/", json=payload2, headers={"Authorization": f"Bearer {token}"})

    # Tenta atualizar produto 2 para SKU1 → deve falhar
    update_payload = {"sku": "SKU1"}
    resp_update = client.put(f"/products/{resp2.json()['id']}", json=update_payload,
                             headers={"Authorization": f"Bearer {token}"})
    assert resp_update.status_code == 400
    assert "SKU already exists" in resp_update.json()["detail"]

# -------------------- Testes de multi-tenant --------------------
def test_product_isolation(client, get_token):
    token_a = get_token("d@teste.com")  # Manager A → Company A
    token_b = get_token("e@teste.com")  # Manager B → Company B

    payload_a = make_product_payload(name="Produto A", sku="ISOLATIONA")
    payload_b = make_product_payload(name="Produto B", sku="ISOLATIONB")

    # Cria produtos em empresas diferentes
    resp_a = client.post("/products/", json=payload_a, headers={"Authorization": f"Bearer {token_a}"})
    resp_b = client.post("/products/", json=payload_b, headers={"Authorization": f"Bearer {token_b}"})

    # Usuário A não vê produto B
    list_resp_a = client.get("/products/", headers={"Authorization": f"Bearer {token_a}"})
    assert resp_b.json()["id"] not in [p["id"] for p in list_resp_a.json()]

    # Usuário B não vê produto A
    list_resp_b = client.get("/products/", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_a.json()["id"] not in [p["id"] for p in list_resp_b.json()]

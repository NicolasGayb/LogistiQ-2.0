import pytest
from app.models.user import User

# ----------------------
# Testes de login
# ----------------------

def test_login_success(client):
    """
    Teste de login bem-sucedido com credenciais válidas.
    """
    response = client.post(
        "/auth/login",
        data={"username": "admin@teste.com", "password": "123456"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """
    Teste de login com senha incorreta.
    """
    response = client.post(
        "/auth/login",
        data={"username": "admin@teste.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """
    Teste de login com usuário inexistente.
    """
    response = client.post(
        "/auth/login",
        data={"username": "noone@teste.com", "password": "123456"}
    )
    assert response.status_code == 401


# ----------------------
# Teste de registro
# ----------------------

def test_register_user(client, session):
    """
    Teste de registro de um novo usuário.
    """
    payload = {
        "name": "New User",
        "email": "newuser@teste.com",
        "password": "newpass123",
        "role": "USER",
        "company_cnpj": "23456789012345"
    }

    response = client.post(
        "/auth/register",
        json=payload
    )

    # API deve retornar 201 Created
    assert response.status_code == 201

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verifica no banco de dados se o usuário foi criado
    user_in_db = session.query(User).filter_by(email="newuser@teste.com").first()
    assert user_in_db is not None
    assert user_in_db.name == "New User"
    assert user_in_db.role == "USER"
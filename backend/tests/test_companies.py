import uuid
import pytest
from fastapi import status
from app.models import Company, User
from app.models.enum import UserRole

# =========================================================
# POST /companies
# =========================================================

def test_create_company_success_system_admin(client, session, get_token):
    """Testa a criação de uma empresa com sucesso por um SYSTEM_ADMIN."""
    token = get_token("admin@teste.com")

    payload = {
        "company": {
            "name": "Nova Empresa",
            "cnpj": "11122233000199"
        },
        "admin_name": "Admin Empresa",
        "admin_email": "admin@empresa.com",
        "admin_password": "123456"
    }

    response = client.post(
        "/companies/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Nova Empresa"
    assert data["cnpj"] == "11122233000199"


def test_create_company_duplicate_name(client, session, get_token):
    """Testa a criação de uma empresa com nome duplicado."""
    token = get_token("admin@teste.com")

    payload = {
        "company": {
            "name": "Empresa Duplicada",
            "cnpj": "12345678901234"
        },
        "admin_name": "Admin",
        "admin_email": "admin2@empresa.com",
        "admin_password": "123456"
    }

    response = client.post(
        "/companies/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_company_forbidden_non_system_admin(client, get_token):
    token = get_token("f@teste.com")

    payload = {
        "company": {
            "name": "Empresa X",
            "cnpj": "77777777000199"
        },
        "admin_name": "Admin",
        "admin_email": "admin@x.com",
        "admin_password": "123456"
    }

    response = client.post(
        "/companies/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_company_invalid_cnpj(client, get_token):
    token = get_token("admin@teste.com")

    payload = {
        "company": {
            "name": "Empresa Teste",
            "cnpj": "123"
        },
        "admin_name": "Admin",
        "admin_email": "admin@empresa.com",
        "admin_password": "123456"
    }

    response = client.post(
        "/companies/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422

# =========================================================
# GET /companies/me
# =========================================================

def test_get_my_company_success_admin(client, session, get_token):
    """Testa a obtenção dos dados da própria empresa por um ADMIN."""
    token = get_token("b@teste.com")

    company = session.query(Company).filter(Company.name == "Company B").first()

    response = client.get(
        "/companies/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(company.id)


def test_get_my_company_not_found(client, session, get_token):
    token = get_token("admin@teste.com")

    response = client.get(
        "/companies/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_my_company_forbidden_user_role(client, get_token):
    token = get_token("f@teste.com")

    response = client.get(
        "/companies/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


# =========================================================
# GET /companies/list
# =========================================================

def test_list_companies_success_system_admin(client, session, get_token):
    token = get_token("admin@teste.com")

    response = client.get(
        "/companies/list",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 2


def test_list_companies_forbidden_admin(client, get_token):
    token = get_token("b@teste.com")

    response = client.get(
        "/companies/list",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


# =========================================================
# GET /companies/{company_id}
# =========================================================

def test_get_company_by_id_success(client, session, get_token):
    token = get_token("admin@teste.com")

    company = session.query(Company).filter(Company.name == "Company A").first()
    response = client.get(
        f"/companies/{company.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(company.id)


def test_get_company_by_id_not_found(client, get_token):
    token = get_token("admin@teste.com")

    response = client.get(
        f"/companies/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# =========================================================
# PUT /companies/me
# =========================================================

def test_update_company_success(client, session, get_token):
    token = get_token("admin@teste.com")

    company = session.query(Company).filter(Company.name == "Company A").first()

    payload = {
        "name": "Empresa Atualizada",
    }

    response = client.put(
        f"/companies/{company.id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Empresa Atualizada"


def test_update_company_not_found(client, get_token):
    token = get_token("admin@teste.com")

    response = client.put(
        "/companies/me",
        json={"name": "X"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# =========================================================
# DELETE /companies/{company_id}
# =========================================================

def test_delete_company_success(client, session, get_token):
    company = session.query(Company).filter(Company.name == "Company A").first()
    token = get_token("admin@teste.com")

    response = client.delete(
        f"/companies/{company.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_company_not_found(client, get_token):
    token = get_token("admin@teste.com")

    response = client.delete(
        f"/companies/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
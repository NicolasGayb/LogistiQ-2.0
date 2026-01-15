import pytest
import uuid
from fastapi import HTTPException
from app.schemas.user import UserResponse
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.enum import UserRole

# -------------------- LIST USERS --------------------
def test_list_users_system_admin(client: TestClient, get_token, session):
    token = get_token("admin@teste.com")
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # System admin vê todos os usuários
    assert len(data) == session.query(User).count()


def test_list_users_admin(client: TestClient, get_token, session):
    admin = session.query(User).filter(User.role == UserRole.ADMIN).first()
    token = get_token(admin.email)
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Admin vê só usuários da própria empresa
    users_in_company = session.query(User).filter(User.company_id == admin.company_id).count()
    assert len(data) == users_in_company


def test_list_users_manager(client: TestClient, get_token, session):
    manager = session.query(User).filter(User.role == UserRole.MANAGER).first()
    token = get_token(manager.email)
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Manager vê só usuários da empresa exceto admins
    users_in_company = session.query(User).filter(
        User.company_id == manager.company_id,
        User.role != UserRole.ADMIN
    ).count()
    assert len(data) == users_in_company


# -------------------- GET USER --------------------
def test_get_user_system_admin(client: TestClient, get_token, session):
    user = session.query(User).filter(User.role == UserRole.SYSTEM_ADMIN).first()
    token = get_token("admin@teste.com")
    response = client.get(f"/users/{user.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["role"] == user.role

def test_get_user_admin_forbidden(client: TestClient, get_token, session):
    # Pega admin de uma empresa e tenta acessar usuário de outra
    admin = session.query(User).filter(User.role == UserRole.ADMIN).first()
    other_user = session.query(User).filter(User.company_id != admin.company_id).first()
    token = get_token(admin.email)
    response = client.get(
        f"/users/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_get_user_manager_forbidden(client: TestClient, get_token, session):
    manager = session.query(User).filter(User.role == UserRole.MANAGER).first()
    admin_in_same_company = session.query(User).filter(
        User.role == UserRole.ADMIN,
        User.company_id == manager.company_id
    ).first()
    token = get_token(manager.email)
    response = client.get(
        f"/users/{admin_in_same_company.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_get_nonexistent_user(client: TestClient, get_token):
    token = get_token("admin@teste.com")
    fake_id = uuid.uuid4()
    response = client.get(
        f"/users/{fake_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


# -------------------- UPDATE USER --------------------
def test_update_user_system_admin(client: TestClient, get_token, session):
    user = session.query(User).filter(User.role == UserRole.USER).first()
    token = get_token("admin@teste.com")
    payload = {"name": "Updated Name", "role": "USER"}
    response = client.put(
        f"/users/update-user/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 200
    session.refresh(user)
    assert user.name == "Updated Name"


def test_update_user_admin_forbidden(client: TestClient, get_token, session):
    admin = session.query(User).filter(User.role == UserRole.ADMIN).first()
    other_user = session.query(User).filter(User.company_id != admin.company_id).first()
    token = get_token(admin.email)
    payload = {"name": "Attempted Update"}
    response = client.put(
        f"/users/update-user/{other_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 403


def test_update_nonexistent_user(client: TestClient, get_token):
    token = get_token("admin@teste.com")
    fake_id = uuid.uuid4()
    payload = {"name": "Test"}
    response = client.put(
        f"/users/update-user/{str(fake_id)}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert response.status_code == 404


# -------------------- DELETE USER --------------------
def test_delete_user_system_admin(client: TestClient, get_token, session):
    user = session.query(User).filter(User.role == UserRole.USER).first()
    token = get_token("admin@teste.com")
    response = client.delete(
        f"/users/delete-user/{user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert session.query(User).filter(User.id == user.id).first() is None


def test_delete_user_non_admin_forbidden(client: TestClient, get_token, session):
    user = session.query(User).filter(User.role == UserRole.USER).first()
    admin_user = session.query(User).filter(User.role == UserRole.ADMIN).first()
    token = get_token(admin_user.email)
    response = client.delete(
        f"/users/delete-user/{user.id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_delete_nonexistent_user(client: TestClient, get_token):
    token = get_token("admin@teste.com")
    fake_id = uuid.uuid4()
    response = client.delete(
        f"/users/delete-user/{str(fake_id)}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
import uuid
from fastapi import status
from app.models.enum import MovementType


def test_list_movements_success(client, get_token, create_operation):
    token = get_token("b@teste.com")
    operation = create_operation()

    response = client.get(
        f"/operations/{operation.id}/movements",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_list_movements_other_company_forbidden(
    client, get_token, create_operation_other_company
):
    token = get_token("b@teste.com")
    operation = create_operation_other_company()

    response = client.get(
        f"/operations/{operation.id}/movements",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_create_manual_movement_success(
    client, get_token, create_operation
):
    token = get_token("b@teste.com")
    operation = create_operation()

    payload = {
        "type": MovementType.MANUAL.value,
        "description": "Movimento criado manualmente"
    }

    response = client.post(
        f"/operations/{operation.id}/movements",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["type"] == payload["type"]
    assert data["description"] == payload["description"]
    assert data["operation_id"] == str(operation.id)

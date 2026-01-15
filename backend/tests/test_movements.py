import pytest

def test_create_movement(client, get_token):
    token = get_token(email="a@teste.com")
    payload = {"type": "IN", "description": "Nova entrada teste", "quantity": 7, "company_id": 1}
    response = client.post(
        "/movements",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["quantity"] == 7

def test_list_movements(client, get_token):
    token = get_token(email="a@teste.com")
    response = client.get(
        "/movements",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # Movements de Company A já existentes

def test_movements_isolation(client, get_token):
    token_a = get_token(email="a@teste.com")
    token_b = get_token(email="b@teste.com")

    response_a = client.get(
        "/movements",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    response_b = client.get(
        "/movements",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    data_a = response_a.json()
    data_b = response_b.json()

    # user B não deve ver movements da Company A
    assert all(m["company_id"] != 1 for m in data_b)

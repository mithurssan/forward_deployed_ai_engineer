def test_existing_customer_returns_200(client):

    response = client.get(
        "/customers/1"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["customer_id"] == 1

def test_missing_customer_returns_404(client):

    response = client.get(
        "/customers/999"
    )

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "CUSTOMER_NOT_FOUND"


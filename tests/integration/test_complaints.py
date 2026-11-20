from src.app.models.complaint import Complaint

def test_valid_complaint_creation_returns_201(
    client,
    seeded_db,
):

    response = client.post(
        "/complaints",
        json={
            "customer_id":1,
            "account_id": "A00061",
            "category": "Fees",
            "channel": "Web",
            "priority": "Medium",
            "complaint_text": "Test complaint",
        },
    )

    assert response.status_code == 201

    complaint_id = response.json()["complaint_id"]

    with seeded_db.transaction() as session:

        complaint = session.get(
            Complaint,
            complaint_id,
        )

        assert complaint is not None
        assert complaint.status == "Open"
        assert complaint.customer_id == 1

def test_missing_required_field_returns_422(client):

    response = client.post(
        "/complaints",
        json={
            "customer_id": 1,
        },
    )

    assert response.status_code == 422


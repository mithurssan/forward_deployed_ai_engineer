from src.app.models.complaint import Complaint
from src.app.models.complaint_status_history import ComplaintStatusHistory

def test_valid_status_update_persists_change(
    client,
    seeded_db,
):

    response = client.patch(
        "/complaints/CP00001/status",
        json={
            "status": "In Review",
            "reason": "Picked up for review",
            "role": "Analyst",
        },
    )

    assert response.status_code == 200

    with seeded_db.transaction() as session:

        complaint = session.get(
            Complaint,
            "CP00001",
        )

        assert complaint.status == "In Review"
    
        histories = (
            session.query(ComplaintStatusHistory)
            .filter_by(complaint_id="CP00001")
            .all()
        )

        assert any(
            history.old_status == "Open"
            and history.new_status == "In Review"
            for history in histories
        )

def test_closed_complaint_cannot_transition(
    client,
    seeded_db,
):

    response = client.patch(
        "/complaints/CP00002/status",
        json={
            "status":"In Review",
            "reason":"Attempted reopen",
            "role": "Supervisor",
        },
    )

    assert response.status_code == 409

    assert(
        response.json()["code"] == "INVALID_TRANSITION"
    )

    with seeded_db.transaction() as session:

        complaint = session.get(
            Complaint,
            "CP00002",
        )

        assert complaint.status == "Closed"

        
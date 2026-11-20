import pytest
from src.app.models.complaint import Complaint

from src.services.complaint_service import (
    ComplaintService,
    Repositories,
    make_repositories,
)

class FailingHistoryRepository:
    def add(self, *args, **kwargs):
        raise RuntimeError("forced integration test failure")


def failing_repository_factory(session):
    repos = make_repositories(session)

    return Repositories(
        customers=repos.customers,
        accounts=repos.accounts,
        complaints=repos.complaints,
        history=FailingHistoryRepository(),
        requests=repos.requests,
    )

def test_complaint_creation_rolls_back_when_history_fails(
    seeded_db
):

    service = ComplaintService(
        db=seeded_db,
        repository_factory=failing_repository_factory,
    )

    with pytest.raises(RuntimeError):
        service.create_complaint(
            customer_id=1,
            account_id="A00061",
            category="Fees",
            channel="Web",
            priority="Medium",
            complaint_text="Rollback test",
        )
    
    with seeded_db.transaction() as session:
        complaint = session.get(Complaint, "CP00003")

        assert complaint is None
from datetime import date

import pytest

from src.domain.errors import (
    ComplaintNotFound,
    CustomerNotFound,
    InvalidTransition,
)

from src.services.complaint_service import ComplaintService

from tests.unit.fakes import (
    FakeDB,
    FakeStore,
    fake_repositories
)

def make_service():
    store = FakeStore.sample()

    service = ComplaintService(
        db=FakeDB(store),
        repository_factory=fake_repositories(store),
        today=lambda: date(2026, 9, 1),
    )

    return service, store


def test_missing_customer_raises_customer_not_found():

    service, store = make_service()

    with pytest.raises(CustomerNotFound):
        service.get_customer("C9999")


def test_missing_complaint_raises_complaint_not_found():

    service, store = make_service()

    with pytest.raises(ComplaintNotFound):
        service.get_complaint("CP99999")


def test_valid_status_change_updates_complaint():

    service, store = make_service()

    service.change_status(
        "CP00001",
        "In Review",
        "Picked up for review",
        role="Analyst",
    )

    complaint = store.complaints["CP00001"]

    assert complaint.status == "In Review"


def test_valid_status_change_records_history():

    service, store = make_service()

    number_before = len(store.history)

    service.change_status(
        "CP00001",
        "In Review",
        "Picked up for review",
        role="Analyst"
    )

    assert len(store.history) == number_before + 1

    latest = store.history[-1]

    assert latest["complaint_id"] == "CP00001"
    assert latest["old_status"] == "Open"
    assert latest["new_status"] == "In Review"

def test_invalid_status_change_raises_invalid_transition():

    service, store = make_service()

    with pytest.raises(InvalidTransition):
        service.change_status(
            "CP00004",
            "In Review",
            "Trying to reopen complaint",
            role="Supervisor",
        )

def test_failed_change_does_not_modify_complaint():

    service, store = make_service()

    original_status = store.complaints["CP00004"].status

    with pytest.raises(InvalidTransition):
        service.change_status(
            "CP00004",
            "In Review",
            "Trying to reopen complaint",
            role="Supervisor",
        )
    
    assert store.complaints["CP00004"].status == original_status
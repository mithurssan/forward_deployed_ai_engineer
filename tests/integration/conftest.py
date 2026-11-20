from datetime import date
from contextlib import contextmanager
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.dependencies import get_complaint_service

from src.app.models.base import Base
from src.app.models.customer import Customer
from src.app.models.account import Account
from src.app.models.complaint import Complaint

from src.app.models.complaint_status_history import ComplaintStatusHistory
from src.app.models.service_request import ServiceRequest

from src.services.complaint_service import ComplaintService

class TestDatabaseManager:
    
    def __init__(self, database_url):
        self.engine = create_engine(database_url)

        self.SessionLocal = sessionmaker(
            bind=self.engine
        )

    @contextmanager
    def transaction(self):
        with self.SessionLocal() as session:
            with session.begin():
                yield session
        

@pytest.fixture
def test_db(tmp_path):
    database_file = tmp_path / "test.db"

    db = TestDatabaseManager(
        f"sqlite:///{database_file}"
    )

    Base.metadata.create_all(
        bind=db.engine
    )

    return db

@pytest.fixture
def seeded_db(test_db):

    with test_db.transaction() as session:

        customer = Customer(
            customer_id="1",
            first_name="Taylor",
            last_name="Wilson",
            email="test@example.test",
        )

        account = Account(
            account_id="A00061",
            customer_id="1",
            account_type="Mortgage",
        )

        open_complaint = Complaint(
            complaint_id="CP00001",
            customer_id="1",
            account_id="A00061",
            category="Fees",
            status="Open",
            date_opened=date(2026, 8, 1),
            date_closed=None,
            channel="Web",
            priority="Medium",
            complaint_text="Test complaint",
        )

        closed_complaint = Complaint(
            complaint_id="CP00002",
            customer_id="1",
            account_id="A00061",
            category="Fees",
            status="Closed",
            date_opened=date(2026, 8, 1),
            date_closed=date(2026, 8, 20),
            channel="Web",
            priority="Medium",
            complaint_text="Test closed complaint",
        )

        session.add_all([
            customer,
            account,
            open_complaint,
            closed_complaint,
        ])

    return test_db

@pytest.fixture
def client(seeded_db):

    service = ComplaintService(
        seeded_db,
        today=lambda: date(2026, 9, 1),
    )

    def override_service():
        return service
    
    app.dependency_overrides[
        get_complaint_service
    ] = override_service

    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()



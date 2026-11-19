import copy

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date

from src.services.complaint_service import Repositories


@dataclass
class FakeCustomer:
    customer_id: str
    first_name: str
    last_name: str
    email: str


@dataclass
class FakeAccount:
    account_id: str
    customer_id: str
    account_type: str


@dataclass
class FakeComplaint:
    complaint_id: str
    customer_id: str
    account_id: str | None
    category: str
    status: str
    date_opened: date
    date_closed: date | None
    channel: str
    priority: str
    complaint_text: str | None = None


# Fake in-memory database

class FakeStore:

    def __init__(self):
        self.customers = {}
        self.accounts = {}
        self.complaints = {}
        self.history = []
        self.requests = []

    @classmethod
    def sample(cls):
        store = cls()

        store.customers["C0096"] = FakeCustomer(
            customer_id="C0096",
            first_name="Taylor",
            last_name="Wilson",
            email="taylor@example.test",
        )

        store.accounts["A00061"] = FakeAccount(
            account_id="A00061",
            customer_id="C0096",
            account_type="Mortgage",
        )

        statuses = [
            ("CP00001", "Open"),
            ("CP00002", "In Review"),
            ("CP00003", "Escalated"),
            ("CP00004", "Closed"),
            ("CP00005", "Pending Approval"),
        ]

        for complaint_id, status in statuses:

            complaint = FakeComplaint(
                complaint_id=complaint_id,
                customer_id="C0096",
                account_id="A00061",
                category="Fees",
                status=status,
                date_opened=date(2026, 8, 1),
                date_closed=(
                    date(2026, 8, 20)
                    if status == "Closed"
                    else None
                ),
                channel="Web",
                priority="Medium",
                complaint_text="Test complaint",
            )

            store.complaints[complaint_id] = complaint

            store.history.append({
                "history_id": (
                    f"H{len(store.history) + 1:05d}"
                ),
                "complaint_id": complaint_id,
                "old_status": None,
                "new_status": status,
                "changed_at": date(2026, 8, 1),
                "changed_by_role": "System",
            })

        return store



# Fake DatabaseManager

class FakeDB:

    def __init__(self, store):
        self.store = store

    @contextmanager
    def transaction(self):

        saved = copy.deepcopy(self.store.__dict__)

        try:
            yield None

        except Exception:
            self.store.__dict__.clear()
            self.store.__dict__.update(saved)
            raise



# Fake repositories

class FakeCustomers:

    def __init__(self, store):
        self.store = store

    def get_by_id(self, customer_id):
        return self.store.customers.get(customer_id)


class FakeAccounts:

    def __init__(self, store):
        self.store = store

    def get_by_id(self, account_id):
        return self.store.accounts.get(account_id)

    def get_for_customer(self, customer_id):
        return [
            account
            for account in self.store.accounts.values()
            if account.customer_id == customer_id
        ]


class FakeComplaints:

    def __init__(self, store):
        self.store = store

    def get_by_id(self, complaint_id):
        return self.store.complaints.get(complaint_id)

    def get_for_customer(self, customer_id):
        return [
            complaint
            for complaint in self.store.complaints.values()
            if complaint.customer_id == customer_id
        ]

    def update_status(
        self,
        complaint_id,
        status,
        date_closed=None,
    ):
        complaint = self.store.complaints.get(complaint_id)

        if complaint is None:
            return 0

        complaint.status = status
        complaint.date_closed = date_closed

        return 1


class FakeHistory:

    def __init__(self, store):
        self.store = store

    def get_for_complaint(self, complaint_id):
        return [
            history
            for history in self.store.history
            if history["complaint_id"] == complaint_id
        ]

    def next_id(self):
        number = len(self.store.history) + 1
        return f"H{number:05d}"

    def add(
        self,
        complaint_id,
        old_status,
        new_status,
        changed_at,
        changed_by_role,
    ):
        history_id = self.next_id()

        self.store.history.append({
            "history_id": history_id,
            "complaint_id": complaint_id,
            "old_status": old_status,
            "new_status": new_status,
            "changed_at": changed_at,
            "changed_by_role": changed_by_role,
        })

        return history_id


class FakeRequests:

    def __init__(self, store):
        self.store = store

    def get_for_complaint(self, complaint_id):
        return [
            request
            for request in self.store.requests
            if request.get("complaint_id") == complaint_id
        ]



# Fake repository factory

def fake_repositories(store):

    def factory(_session):
        return Repositories(
            customers=FakeCustomers(store),
            accounts=FakeAccounts(store),
            complaints=FakeComplaints(store),
            history=FakeHistory(store),
            requests=FakeRequests(store),
        )

    return factory
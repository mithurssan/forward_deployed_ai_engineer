"""Complaint service: business rules for complaints."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

from src.data.account_repository import AccountRepository
from src.data.complaint_repository import ComplaintRepository
from src.data.customer_repository import CustomerRepository
from src.data.history_repository import HistoryRepository
from src.data.service_request_repository import ServiceRequestRepository
from src.domain.errors import (
    ApprovalRequired,
    ComplaintNotFound,
    CustomerNotFound,
    ForbiddenRole,
    InvalidTransition,
    AccountNotFound,
)
from src.domain.models import (
    CLOSABLE,
    ComplaintStatus,
    Role,
    needs_approval,
    transition_problem,
)
from src.app.models.complaint import Complaint

@dataclass
class Repositories:
    customers: object
    accounts: object
    complaints: object
    history: object
    requests: object

def make_repositories(session):
    return Repositories(
        CustomerRepository(session),
        AccountRepository(session),
        ComplaintRepository(session),
        HistoryRepository(session),
        ServiceRequestRepository(session),
    )

def audit_event_id_for(history_id):
    return f"AUD-{int(history_id[1:]):06d}"

def _v(value):
    """Enum member or plain string -> plain string."""
    return getattr(value, "value", value)

class ComplaintService:

    def __init__(self, db, repository_factory=make_repositories, today=date.today):
        self.db = db
        self.repository_factory = repository_factory
        self.today = today
    
    def get_customer(self, customer_id):
        with self.db.transaction() as session:
            repos = self.repository_factory(session)

            customer = repos.customers.get_by_id(customer_id)
        
            if customer is None:
                raise CustomerNotFound(
                    f"Customer {customer_id} not found."
            )
            return {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
        }

    def get_accounts(self, customer_id):
        with self.db.transaction() as session:
            repos = self.repository_factory(session)

            customer = repos.customers.get_by_id(customer_id)

            if customer is None:
                raise CustomerNotFound(
                    f"Customer {customer_id} not found."
                )

            accounts = repos.accounts.get_for_customer(
                customer_id
            )

            return {
                "customer_id": customer_id,
                "accounts": accounts,
            }
    
    def get_complaint(self, complaint_id):
        with self.db.transaction() as session:
            repos = self.repository_factory(session)

            complaint = repos.complaints.get_by_id(
                complaint_id
            )

            if complaint is None:
                raise ComplaintNotFound(
                    f"Complaint {complaint_id} not found."
                )
            
            return self._complaint_with_children(
                complaint,
                repos
            )
    
    def _complaint_with_children(self, complaint, repos):
        history = repos.history.get_for_complaint(
            complaint.complaint_id
        )

        requests = repos.requests.get_for_complaint(
            complaint.complaint_id
        )
        history_data = [
        {
            "history_id": item.history_id,
            "old_status": item.old_status,
            "new_status": item.new_status,
            "changed_at": item.changed_at,
            "changed_by_role": item.changed_by_role,
        }
        for item in history
    ]
        request_data = [
        {
            "request_id": item.request_id,
            "request_type": item.request_type,
            "status": item.status,
            "created_date": item.created_date,
        }
        for item in requests
    ]
        return {
            "complaint_id": complaint.complaint_id,
            "customer_id": complaint.customer_id,
            "account_id": complaint.account_id,
            "category": _v(complaint.category),
            "status": _v(complaint.status),
            "date_opened": complaint.date_opened,
            "date_closed": complaint.date_closed,
            "channel": _v(complaint.channel),
            "priority": _v(complaint.priority),
            "history": history_data,
            "linked_service_requests": request_data,
        }

    def get_customer_complaint_history(self, customer_id):
        with self.db.transaction() as session:
            repos = self.repository_factory(session)
        
            customer = repos.customers.get_by_id(customer_id)

            if customer is None:
                raise CustomerNotFound(
                    f"Customer {customer_id} not found."
                )
            
            complaints = repos.complaints.get_for_customer(customer_id)

            return [
            {
                "complaint_id": complaint.complaint_id,
                "customer_id": complaint.customer_id,
                "account_id": complaint.account_id,
                "category": complaint.category,
                "status": complaint.status,
                "date_opened": complaint.date_opened,
                "date_closed": complaint.date_closed,
                "channel": complaint.channel,
                "priority": complaint.priority,
                "complaint_text": complaint.complaint_text,
            }
            for complaint in complaints
        ]

    def create_complaint(
        self,
        customer_id,
        account_id,
        category,
        channel,
        priority,
        complaint_text=None,
    ):
        with self.db.transaction() as session:
            repos = self.repository_factory(session)

            customer = repos.customers.get_by_id(customer_id)

            if customer is None:
                raise CustomerNotFound(
                    f"Customer {customer_id} not found."
                )

            account = repos.accounts.get_by_id(account_id)

            if account is None:
                raise AccountNotFound(
                    f"Account {account_id} not found."
                )
            if account.customer_id != customer_id:
                raise AccountNotFound(
                    f"Account {account_id} does not belong to customer {customer_id}."
                )

            complaint_id = repos.complaints.next_id()

            complaint = Complaint(
                complaint_id=complaint_id,
                customer_id=customer_id,
                account_id=account_id,
                category=category,
                status="Open",
                date_opened=self.today(),
                date_closed=None,
                channel=channel,
                priority=priority,
                complaint_text=complaint_text,
            )

            repos.complaints.create(complaint)

            repos.history.add(
                complaint_id=complaint_id,
                old_status=None,
                new_status="Open",
                changed_at=self.today(),
                changed_by_role="System",
            )

            return complaint_id


    def change_status(
        self,
        complaint_id,
        target_status,
        reason,
        role,
        actor_id=None
    ):
        with self.db.transaction() as session:
            repos = self.repository_factory(session)

            # READ
            complaint = repos.complaints.get_by_id(
                complaint_id
            )

            if complaint is None:
                raise ComplaintNotFound(
                    f"Complaint {complaint_id} not found."
                )
            
            current_status = _v(complaint.status)
            target_status = _v(target_status)
            role = _v(role)

            # DECIDE
            problem = transition_problem(
                current_status,
                target_status,
                role
            )

            #RAISE
            if problem == "INVALID_TRANSITION":
                message = (
                    f"Cannot change complaint from "
                    f"{current_status} to {target_status}"
                )

                if target_status == ComplaintStatus.CLOSED.value:
                    message += "; use close_complaint."

                raise InvalidTransition(message)
            
            if problem == "FORBIDDEN_ROLE":
                raise ForbiddenRole(
                    f"{role} cannot perform this status transition."
                )
            
            # WRITE
            changed_at = datetime.now(timezone.utc)

            repos.complaints.update_status(
                complaint_id,
                target_status,
                date_closed=None
            )

            history_id = repos.history.add(
                complaint_id,
                current_status,
                target_status,
                changed_at,
                role,
            )

            #RETURN
            return {
                "complaint_id": complaint_id,
                "previous_status": current_status,
                "status": target_status,
                "changed_by": actor_id,
                "changed_at": changed_at,
                "audit_event_id": audit_event_id_for(
                    history_id
                ),
            }
    
    def close(
        self,
        complaint_id,
        compensation_cad=Decimal("0"),
        role="Supervisor",
        actor_id=None
    ):
        role = _v(role)

        # Contract states: Only a Supervisor can call close_complaint.
        if role != Role.SUPERVISOR.value:
            raise ForbiddenRole(
                "Only a Supervisor may close a complaint."
            )
        
        with self.db.transaction() as session:
            repos = self.repository_factory(session)

            # READ
            complaint = repos.complaints.get_by_id(
                complaint_id
            )

            if complaint is None:
                raise ComplaintNotFound(
                    f"Complaint {complaint_id} not found."
                )
            
            current_status = _v(complaint.status)

            # DECIDE / RAISE
            if ComplaintStatus(current_status) not in CLOSABLE:
                raise InvalidTransition(
                    f"Complaint in status {current_status} "
                    "cannot be closed."
                )
            
            if needs_approval(compensation_cad):
                raise ApprovalRequired(
                    "Compensation requires approval."
                )

            closed_status = ComplaintStatus.CLOSED.value
            closed_date = self.today()
            changed_at = datetime.now(timezone.utc)

            # WRITE
            repos.complaints.update_status(
                complaint_id,
                closed_status,
                date_closed=closed_date
            )

            history_id = repos.history.add(
                complaint_id,
                current_status,
                closed_status,
                changed_at,
                Role.SUPERVISOR.value,
            )

            # RETURN
            return {
                "complaint_id": complaint_id,
                "previous_status": current_status,
                "status": closed_status,
                "date_closed": closed_date,
                "closed_by": actor_id,
                "approval_id": None,
                "audit_event_id": audit_event_id_for(
                    history_id
                ),
            }
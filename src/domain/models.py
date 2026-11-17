from decimal import Decimal
from enum import Enum

class ComplaintStatus(str, Enum):
    OPEN = "Open"
    IN_REVIEW = "In Review"
    PENDING_APPROVAL = "Pending Approval"
    ESCALATED = "Escalated"
    CLOSED = "Closed"

class Category(str, Enum):
    FEES = "Fees"
    CARD_OR_TRANSACTION_DISPUTE = "Card or Transaction Dispute"
    DIGITAL_BANKING = "Digital Banking"
    SERVICE_QUALITY = "Service Quality"
    MORTGAGE_SERVICING = "Mortgage Servicing"
    ACCOUNT_ACCESS = "Account Access"

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Channel(str, Enum):
    PHONE = "Phone"
    WEB = "Web"
    EMAIL = "Email"
    BRANCH = "Branch"

class Role(str, Enum):
    ANALYST = "Analyst"
    SUPERVISOR = "Supervisor"

ALLOWED_TRANSITIONS = {
    (ComplaintStatus.OPEN, ComplaintStatus.IN_REVIEW): {
        Role.ANALYST,
        Role.SUPERVISOR,
    },

    (ComplaintStatus.IN_REVIEW, ComplaintStatus.ESCALATED): {
        Role.ANALYST,
        Role.SUPERVISOR,
    },

    (ComplaintStatus.ESCALATED, ComplaintStatus.IN_REVIEW): {
        Role.SUPERVISOR,
    },
}

CLOSABLE = {
    ComplaintStatus.IN_REVIEW,
    ComplaintStatus.ESCALATED,
}

APPROVAL_THRESHOLD_CAD = Decimal("1000.00")

def can_transition(current, target, role):
    current = ComplaintStatus(current)
    target = ComplaintStatus(target)
    role = Role(role)

    allowed_roles = ALLOWED_TRANSITIONS.get((current,target))

    if allowed_roles is None:
        return False
    
    return role in allowed_roles

def transition_problem(current, target, role):
    current = ComplaintStatus(current)
    target = ComplaintStatus(target)
    role = Role(role)

    allowed_roles = ALLOWED_TRANSITIONS.get((current,target))

    if allowed_roles is None:
        return "INVALID_TRANSITION"
    
    if role not in allowed_roles:
        return "FORBIDDEN_ROLE"
    
    return None

def needs_approval(compensation_cad):
    amount = Decimal(str(compensation_cad))

    return amount > APPROVAL_THRESHOLD_CAD
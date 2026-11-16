from dataclasses import dataclass

@dataclass
class Complaint:
    complaint_id: int
    customer_id: int
    account_id: int
    category: str
    status: str
    date_opened: str
    date_closed: Optional[str]
    channel: str
    priority: str
    complaint_text: str
    
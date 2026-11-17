from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.complaint import Complaint

class ComplaintRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, complaint_id: int):
        return self.session.get(
            Complaint,
            complaint_id
        )

    def get_for_customer(self, customer_id: int):

        statement = select(Complaint).where(
            Complaint.customer_id == customer_id
        )

        return list(
            self.session.scalars(statement).all()
        )

    def update_status(
        self,
        complaint_id: int,
        status: str,
        date_closed: date | None = None
    ):
        complaint = self.get_by_id(complaint_id)

        if complaint is None:
            return 0

        complaint.status = status
        complaint.date_closed = date_closed

        self.session.flush()

        return 1
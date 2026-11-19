from sqlalchemy.orm import Session
from sqlalchemy import select
from src.app.models.complaint_status_history import ComplaintStatusHistory

class HistoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_for_complaint(self, complaint_id):
        statement = (
            select(ComplaintStatusHistory)
            .where(
                ComplaintStatusHistory.complaint_id == complaint_id
            )
            .order_by(
                ComplaintStatusHistory.changed_at,
                ComplaintStatusHistory.history_id
            )
        )

        return list(self.session.scalars(statement).all())
    
    def next_id(self):
        statement = (
            select(ComplaintStatusHistory.history_id)
            .order_by(ComplaintStatusHistory.history_id.desc())
            .limit(1)
        )

        highest_id = self.session.scalar(statement)

        if highest_id is None:
            return "H00001"
        
        number = int(highest_id[1:]) + 1

        return f"H{number:05d}"
    
    def add(self, complaint_id, old_status, new_status, changed_at, changed_by_role,):
        history = ComplaintStatusHistory(
            history_id=self.next_id(),
            complaint_id=complaint_id,
            old_status=old_status,
            new_status=new_status,
            changed_at=changed_at,
            changed_by_role=changed_by_role,
        )

        self.session.add(history)

        return history.history_id

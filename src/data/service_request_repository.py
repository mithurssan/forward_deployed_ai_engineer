from sqlalchemy.orm import Session
from sqlalchemy import select

class ServiceRequestRepository:
    def __init__(self,session):
        self.session = session

    def get_for_complaint(self, complaint_id):
        statement = (
            select (
                ServiceRequest.request_id,
                ServiceRequest.request_type,
                ServiceRequest.status,
                ServiceRequest.created_date,
            )
            .where(ServiceRequest.complaint_id == complaint_id)
            .order_by(
                ServiceRequest.created_date,
                ServiceRequest.request_id,
            )
        )

        return self.session.execute(statement).all()
      
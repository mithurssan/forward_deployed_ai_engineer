from sqlalchemy.orm import Session
from app.models.customer import Customer

class CustomerRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, customer_id: int):
        return self.session.get(
            Customer,
            customer_id
        )
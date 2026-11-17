from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.account import Account

class AccountRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_for_customer(self, customer_id: int):

        statement = select(Account).where(
            Account.customer_id == customer_id
        )

        return list(
            self.session.scalars(statement).all()
        )
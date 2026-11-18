from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from src.app.models.base import Base


class Account(Base):
    __tablename__ = "account"

    account_id: Mapped[str] = mapped_column(String,primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customer.customer_id"))
    account_type: Mapped[str] = mapped_column(String)
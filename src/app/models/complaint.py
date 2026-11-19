from datetime import date
from sqlalchemy import Date, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.app.models.base import Base

class Complaint(Base):
    __tablename__ = "complaint"

    complaint_id: Mapped[str] = mapped_column(String,primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.customer_id"))
    account_id: Mapped[str] = mapped_column(ForeignKey("account.account_id"))
    category: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    date_opened: Mapped[date] = mapped_column(Date)
    date_closed: Mapped[date | None] = mapped_column(Date,nullable=True)
    channel: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String)
    complaint_text: Mapped[str | None] = mapped_column(Text,nullable=True)
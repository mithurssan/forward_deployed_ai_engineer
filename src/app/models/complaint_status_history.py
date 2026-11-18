from datetime import date
from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ComplaintStatusHistory(Base):
    __tablename__ = "complaint_status_history"

    history_id: Mapped[str] = mapped_column(primary_key=True)
    complaint_id: Mapped[str] = mapped_column(ForeignKey("complaint.complaint_id"))
    old_status: Mapped[str | None] = mapped_column(nullable=True)
    new_status: Mapped[str] = mapped_column()
    changed_at: Mapped[date] = mapped_column(Date)
    changed_by_role: Mapped[str] = mapped_column()
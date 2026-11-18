from datetime import date
from sqlalchemy import Date, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    request_id: Mapped[str] = mapped_column(String, primary_key=True)
    complaint_id: Mapped[str] = mapped_column(ForeignKey("complaint.complaint_id"))
    request_type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    created_date: Mapped[date] = mapped_column(Date)
from pydantic import BaseModel

class ComplaintCreate(BaseModel):
    customer_id: int
    account_id: str
    category: str
    channel: str
    priority: str
    complaint_text: str | None = None

class ComplaintCreated(BaseModel):
    complaint_id: str

class ComplaintStatusUpdate(BaseModel):
    status: str
    reason: str
    role: str
    actor_id: str | None = None

class ErrorResponse(BaseModel):
    code: str
    message: str
    correlation_id: str


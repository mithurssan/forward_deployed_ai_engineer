from fastapi import APIRouter, Depends

from src.dependencies import get_complaint_service
from src.services.complaint_service import ComplaintService
from src.api.schemas import ComplaintCreate, ComplaintCreated, ComplaintStatusUpdate

router = APIRouter()

@router.get("/complaints/{complaint_id}")
def get_complaint(
    complaint_id: str,
    service: ComplaintService = Depends(get_complaint_service),
):
    return service.get_complaint(complaint_id)

@router.post("/complaints", status_code=201, response_model=ComplaintCreated,)
def create_complaint(
    complaint: ComplaintCreate,
    service: ComplaintService = Depends(get_complaint_service),
):
    complaint_id = service.create_complaint(
        customer_id=complaint.customer_id,
        account_id=complaint.account_id,
        category=complaint.category,
        channel=complaint.channel,
        priority=complaint.priority,
        complaint_text=complaint.complaint_text,
    )

    return {
        "complaint_id": complaint_id
    }

@router.patch("/complaints/{complaint_id}/status")
def update_complaint_status(
    complaint_id: str,
    request: ComplaintStatusUpdate,
    service: ComplaintService = Depends(get_complaint_service),
):
    return service.change_status(
        complaint_id=complaint_id,
        target_status=request.status,
        reason=request.reason,
        role=request.role,
        actor_id=request.actor_id,
    )
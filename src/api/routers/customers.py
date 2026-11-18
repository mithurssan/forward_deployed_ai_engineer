from fastapi import APIRouter, Depends

from src.dependencies import get_complaint_service
from src.services.complaint_service import ComplaintService

router = APIRouter()

@router.get("/customers/{customer_id}")
def get_customer(
    customer_id: str,
    service: ComplaintService = Depends(get_complaint_service),
):
    return service.get_customer(customer_id)

@router.get("/customers/{customer_id}/complaints")
def get_customer_complaint_history(
    customer_id: str,
    service: ComplaintService = Depends(get_complaint_service),
):
    return service.get_customer_complaint_history(customer_id)

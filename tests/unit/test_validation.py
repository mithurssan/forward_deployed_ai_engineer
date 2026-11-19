import pytest

from pydantic import ValidationError

from src.api.schemas import ComplaintCreate

@pytest.mark.parametrize(
    "missing_field",
    [
        "customer_id",
        "account_id",
        "category",
        "channel",
        "priority",
    ],
)

def test_missing_required_field_is_rejected(
    missing_field,
):
    data = {
        "customer_id": "C0096",
        "account_id": "A00061",
        "category": "Fees",
        "channel": "Web",
        "priority": "Medium",
    }

    data.pop(missing_field)

    with pytest.raises(ValidationError):
        ComplaintCreate(**data)
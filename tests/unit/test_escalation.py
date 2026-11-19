from decimal import Decimal

import pytest

from src.domain.models import needs_approval

@pytest.mark.parametrize(
    "amount,expected",
    [
        (Decimal("999.99"), False),
        (Decimal("1000.00"), False),
        (Decimal("1000.01"), True),
    ],
)

def test_approval_threshold_boundary(amount, expected):
    assert needs_approval(amount) is expected
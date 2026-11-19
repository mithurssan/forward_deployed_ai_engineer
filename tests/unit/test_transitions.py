import pytest

from src.domain.models import transition_problem, can_transition

@pytest.mark.parametrize(
    "old_status,new_status,role",
    [
        ("Open", "In Review", "Analyst"),
        ("Open", "In Review", "Supervisor"),
        ("In Review", "Escalated", "Analyst"),
        ("In Review", "Escalated", "Supervisor"),
        ("Escalated", "In Review", "Supervisor"),
    ],
)

def test_valid_status_transitions_are_allowed(
    old_status,
    new_status,
    role,
):
    result = transition_problem(
        old_status,
        new_status,
        role,
    )

    assert result is None

@pytest.mark.parametrize(
    "old_status,new_status,role",
    [
        ("Open", "Closed", "Analyst"),
        ("Open", "Escalated", "Analyst"),
        ("Closed", "In Review", "Supervisor"),
        ("Pending Approval", "In Review", "Supervisor"),
    ],
)

def test_invalid_status_transitions_return_invalid_transition(
    old_status,
    new_status,
    role,
):
    result = transition_problem(
        old_status,
        new_status,
        role,
    )

    assert result == "INVALID_TRANSITION"


def test_analyst_cannot_move_escalated_to_in_review():
    result = transition_problem(
        "Escalated",
        "In Review",
        "Analyst",
    )

    assert result == "FORBIDDEN_ROLE"


def test_can_transition_returns_boolean():
    assert can_transition(
        "Open",
        "In Review",
        "Analyst",
    ) is True

    assert can_transition(
        "Open",
        "Closed",
        "Analyst",
    ) is False
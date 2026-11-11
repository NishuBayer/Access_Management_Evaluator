import pytest

from access_management_models import (
    AssignmentRecord,
)

from evaluation.access_evaluator import AccessEvaluator
from evaluation.exceptions import UnknownRoleError


def test_unknown_role():

    assignment = AssignmentRecord(
        pk="",
        sk="",
        entity_type="ASSIGNMENT",
        assignment_id=1,
        principal_type="USER",
        principal_id="123",
        app_id="",
        principal_name="test",
        role_code="unknown_role",
        access_mode="FULL",
        authorization_scopes=[],
        status="ACTIVE",
        valid_from="2026-01-01T00:00:00Z",
        valid_to="2027-01-01T00:00:00Z",
        source="manual",
        created_at="2026-01-01T00:00:00Z",
        created_by="test",
        updated_at="2026-01-01T00:00:00Z",
        updated_by="test",
    )

    with pytest.raises(
        UnknownRoleError
    ):
        AccessEvaluator().evaluate_access(
            [assignment],
            [],
        )
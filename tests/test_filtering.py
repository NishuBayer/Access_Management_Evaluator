from access_management_models import (
    AssignmentRecord,
    RoleRecord,
)

from evaluation.access_evaluator import AccessEvaluator


def role():
    return RoleRecord(
        pk="",
        sk="",
        entity_type="ROLE",
        role_object_id="1",
        role_code="collector",
        display_name="collector",
        description="",
        precedence=20,
        status="ACTIVE",
        created_at="2026-01-01T00:00:00Z",
        created_by="test",
        updated_at="2026-01-01T00:00:00Z",
        updated_by="test",
    )


def test_expired_assignment_ignored():

    expired = AssignmentRecord(
        pk="",
        sk="",
        entity_type="ASSIGNMENT",
        assignment_id=1,
        principal_type="USER",
        principal_id="123",
        app_id="",
        principal_name="test",
        role_code="collector",
        access_mode="FULL",
        authorization_scopes=[],
        status="ACTIVE",
        valid_from="2020-01-01T00:00:00Z",
        valid_to="2020-12-31T00:00:00Z",
        source="manual",
        created_at="2020-01-01T00:00:00Z",
        created_by="test",
        updated_at="2020-01-01T00:00:00Z",
        updated_by="test",
    )

    result = AccessEvaluator().evaluate_access(
        [expired],
        [role()],
    )

    assert result.effective_roles == []


def test_empty_assignments():

    result = AccessEvaluator().evaluate_access(
        [],
        [role()],
    )

    assert result.primary_role is None
    assert result.effective_roles == []
    assert result.effective_authorizations == []
    assert result.full_access_roles == []
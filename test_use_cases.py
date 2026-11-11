from access_management_models import (
    AssignmentRecord,
    RoleRecord,
)

from evaluation.access_evaluator import AccessEvaluator


def build_role(
    role_code: str,
    precedence: int,
    status: str = "ACTIVE",
) -> RoleRecord:
    return RoleRecord(
        pk="",
        sk="",
        entity_type="ROLE",
        role_object_id=f"{role_code}-id",
        role_code=role_code,
        display_name=role_code,
        description="",
        precedence=precedence,
        status=status,
        created_at="2026-01-01T00:00:00Z",
        created_by="test",
        updated_at="2026-01-01T00:00:00Z",
        updated_by="test",
    )


def build_assignment(
    assignment_id: int,
    role_code: str,
    access_mode: str,
    scopes: list[str] | None = None,
):
    return AssignmentRecord(
        pk="",
        sk="",
        entity_type="ASSIGNMENT",
        assignment_id=assignment_id,
        principal_type="USER",
        principal_id="user-1",
        app_id="",
        principal_name="Test User",
        role_code=role_code,
        access_mode=access_mode,
        authorization_scopes=scopes or [],
        status="ACTIVE",
        valid_from="2026-01-01T00:00:00Z",
        valid_to="2027-12-31T23:59:59Z",
        source="manual",
        created_at="2026-01-01T00:00:00Z",
        created_by="tester",
        updated_at="2026-01-01T00:00:00Z",
        updated_by="tester",
    )


def test_use_case_1_admin_full_access():
    result = AccessEvaluator().evaluate_access(
        assignments=[
            build_assignment(
                101,
                "admin",
                "FULL",
            )
        ],
        roles=[
            build_role("admin", 10)
        ],
    )

    assert result.primary_role == "admin"
    assert result.effective_roles == ["admin"]
    assert result.full_access_roles == ["admin"]
    assert result.effective_authorizations == [
        "admin+full_access"
    ]


def test_use_case_2_single_scope():
    result = AccessEvaluator().evaluate_access(
        assignments=[
            build_assignment(
                102,
                "collector",
                "SCOPED",
                ["tr_ph#hcp"],
            )
        ],
        roles=[
            build_role("collector", 20)
        ],
    )

    assert result.primary_role == "collector"
    assert result.effective_authorizations == [
        "collector+tr_ph#hcp"
    ]


def test_use_case_3_merge_scopes():
    result = AccessEvaluator().evaluate_access(
        assignments=[
            build_assignment(
                101,
                "collector",
                "SCOPED",
                ["tr_ph#hcp"],
            ),
            build_assignment(
                102,
                "collector",
                "SCOPED",
                ["au_ph#hcp"],
            ),
        ],
        roles=[
            build_role("collector", 20)
        ],
    )

    assert sorted(
        result.effective_authorizations
    ) == [
        "collector+au_ph#hcp",
        "collector+tr_ph#hcp",
    ]


def test_use_case_4_multiple_roles():
    result = AccessEvaluator().evaluate_access(
        assignments=[
            build_assignment(
                101,
                "collector",
                "SCOPED",
                ["au_ph#hcp"],
            ),
            build_assignment(
                102,
                "config_reader",
                "SCOPED",
                ["tr_ph#hcp"],
            ),
        ],
        roles=[
            build_role("collector", 20),
            build_role("config_reader", 30),
        ],
    )

    assert sorted(result.effective_roles) == [
        "collector",
        "config_reader",
    ]


def test_use_case_5_full_overrides_scoped():
    result = AccessEvaluator().evaluate_access(
        assignments=[
            build_assignment(
                101,
                "collector",
                "FULL",
            ),
            build_assignment(
                102,
                "collector",
                "SCOPED",
                ["tr_ph#hcp"],
            ),
        ],
        roles=[
            build_role("collector", 20)
        ],
    )

    assert result.effective_authorizations == [
        "collector+full_access"
    ]


def test_use_case_6_full_plus_other_role():
    result = AccessEvaluator().evaluate_access(
        assignments=[
            build_assignment(
                101,
                "collector",
                "FULL",
            ),
            build_assignment(
                102,
                "config_reader",
                "SCOPED",
                ["tr_ph#hcp"],
            ),
        ],
        roles=[
            build_role("collector", 20),
            build_role("config_reader", 30),
        ],
    )

    assert sorted(
        result.effective_authorizations
    ) == [
        "collector+full_access",
        "config_reader+tr_ph#hcp",
    ]
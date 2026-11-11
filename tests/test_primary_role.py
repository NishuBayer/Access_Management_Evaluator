from access_management_models import (
    AssignmentRecord,
    RoleRecord,
)

from evaluation.access_evaluator import AccessEvaluator


def test_primary_role_precedence():

    roles = [
        RoleRecord(
            "", "", "ROLE", "1",
            "admin", "", "", 10,
            "ACTIVE",
            "", "", "", ""
        ),
        RoleRecord(
            "", "", "ROLE", "2",
            "collector", "", "", 20,
            "ACTIVE",
            "", "", "", ""
        ),
    ]

    assignments = [
        AssignmentRecord(
            "", "", "ASSIGNMENT",
            1,
            "USER",
            "1",
            "",
            "",
            "collector",
            "FULL",
            [],
            "ACTIVE",
            None,
            None,
            "manual",
            "2026-01-01T00:00:00Z",
            "",
            "",
            ""
        ),
        AssignmentRecord(
            "", "", "ASSIGNMENT",
            2,
            "USER",
            "1",
            "",
            "",
            "admin",
            "FULL",
            [],
            "ACTIVE",
            None,
            None,
            "manual",
            "2026-01-01T00:00:00Z",
            "",
            "",
            ""
        ),
    ]

    result = AccessEvaluator().evaluate_access(
        assignments,
        roles,
    )

    assert result.primary_role == "admin"
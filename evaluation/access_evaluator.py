from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from access_management_models import (
    AssignmentRecord,
    RoleRecord,
)

from .constants import (
    ACTIVE,
    FULL,
    SOURCE_PRIORITY,
)

from .evaluation_result import EvaluationResult
from .exceptions import UnknownRoleError


class AccessEvaluator:
    """
    Shared Access Management evaluator.

    Rules implemented:

    1. ACTIVE assignments only
    2. Assignment validity window enforced
    3. USER > GROUP > APPLICATION
    4. FULL overrides SCOPED within winning source
    5. Scopes merged uniquely
    6. Primary role:
       - lowest precedence
       - USER > GROUP > APPLICATION
       - oldest assignment
    """

    @staticmethod
    def _parse_datetime(
        value: str | None,
    ) -> datetime | None:
        """
        Parse ISO datetime string into timezone-aware datetime.
        """

        if not value:
            return None

        value = value.strip()

        if not value:
            return None

        value = value.replace("Z", "+00:00")

        parsed = datetime.fromisoformat(value)

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    @classmethod
    def _is_assignment_valid(
        cls,
        assignment: AssignmentRecord,
        now: datetime,
    ) -> bool:
        """
        Assignment is valid when:
        - status == ACTIVE
        - valid_from <= now
        - valid_to >= now
        """

        if assignment.status != ACTIVE:
            return False

        valid_from = cls._parse_datetime(
            assignment.valid_from
        )

        valid_to = cls._parse_datetime(
            assignment.valid_to
        )

        if valid_from and now < valid_from:
            return False

        if valid_to and now > valid_to:
            return False

        return True

    @staticmethod
    def _build_role_lookup(
        roles: list[RoleRecord],
    ) -> dict[str, RoleRecord]:

        return {
            role.role_code: role
            for role in roles
        }

    @staticmethod
    def _validate_roles(
        assignments: list[AssignmentRecord],
        role_lookup: dict[str, RoleRecord],
    ) -> None:
        """
        Every assignment role must:
        - exist
        - be ACTIVE
        """

        for assignment in assignments:

            role = role_lookup.get(
                assignment.role_code
            )

            if role is None:
                raise UnknownRoleError(
                    f"Unknown role: {assignment.role_code}"
                )

            if role.status != ACTIVE:
                raise UnknownRoleError(
                    f"Inactive role: {assignment.role_code}"
                )

    @staticmethod
    def _group_by_role(
        assignments: list[AssignmentRecord],
    ) -> dict[str, list[AssignmentRecord]]:

        grouped = defaultdict(list)

        for assignment in assignments:
            grouped[
                assignment.role_code
            ].append(
                assignment
            )

        return grouped

    @staticmethod
    def _select_winning_assignments(
        role_assignments: list[AssignmentRecord],
    ) -> list[AssignmentRecord]:
        """
        USER > GROUP > APPLICATION

        Dedicated USER assignments always take precedence.
        """

        winning_priority = min(
            SOURCE_PRIORITY[
                assignment.principal_type
            ]
            for assignment in role_assignments
        )

        return [
            assignment
            for assignment in role_assignments
            if SOURCE_PRIORITY[
                assignment.principal_type
            ]
            == winning_priority
        ]

    @staticmethod
    def _contains_full_access(
        assignments: list[AssignmentRecord],
    ) -> bool:

        return any(
            assignment.access_mode == FULL
            for assignment in assignments
        )

    @staticmethod
    def _merge_scopes(
        assignments: list[AssignmentRecord],
    ) -> list[str]:

        scopes: set[str] = set()

        for assignment in assignments:

            if assignment.authorization_scopes:
                scopes.update(
                    assignment.authorization_scopes
                )

        return sorted(scopes)

    def _determine_primary_role(
        self,
        assignments: list[AssignmentRecord],
        role_lookup: dict[str, RoleRecord],
    ) -> str | None:
        """
        Determines primary role using:

        1. Lowest precedence
        2. USER > GROUP > APPLICATION
        3. Oldest assignment
        """

        if not assignments:
            return None

        candidates = []

        for assignment in assignments:

            role = role_lookup[
                assignment.role_code
            ]

            candidates.append(
                (
                    role.precedence,
                    SOURCE_PRIORITY[
                        assignment.principal_type
                    ],
                    self._parse_datetime(
                        assignment.created_at
                    ),
                    assignment.role_code,
                )
            )

        candidates.sort()

        return candidates[0][3]

    def evaluate_access(
        self,
        assignments: list[AssignmentRecord],
        roles: list[RoleRecord],
    ) -> EvaluationResult:

        now = datetime.now(
            timezone.utc
        )

        role_lookup = self._build_role_lookup(
            roles
        )

        valid_assignments = [
            assignment
            for assignment in assignments
            if self._is_assignment_valid(
                assignment,
                now,
            )
        ]

        self._validate_roles(
            valid_assignments,
            role_lookup,
        )

        grouped_assignments = self._group_by_role(
            valid_assignments
        )

        effective_roles: list[str] = []

        effective_authorizations: list[str] = []

        full_access_roles: list[str] = []

        for (
            role_code,
            role_assignments,
        ) in grouped_assignments.items():

            winning_assignments = (
                self._select_winning_assignments(
                    role_assignments
                )
            )

            effective_roles.append(
                role_code
            )

            #
            # FULL overrides SCOPED
            # only within winning source.
            #
            if self._contains_full_access(
                winning_assignments
            ):

                full_access_roles.append(
                    role_code
                )

                effective_authorizations.append(
                    f"{role_code}+full_access"
                )

                continue

            scopes = self._merge_scopes(
                winning_assignments
            )

            for scope in scopes:

                effective_authorizations.append(
                    f"{role_code}+{scope}"
                )

        primary_role = (
            self._determine_primary_role(
                valid_assignments,
                role_lookup,
            )
        )

        return EvaluationResult(
            primary_role=primary_role,
            effective_roles=sorted(
                effective_roles
            ),
            effective_authorizations=sorted(
                effective_authorizations
            ),
            full_access_roles=sorted(
                full_access_roles
            ),
            evaluated_at=now,
        )
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class EvaluationResult:
    """
    Result returned by AccessEvaluator.

    Example:

    primary_role:
        collector

    effective_roles:
        [
            "collector",
            "config_reader",
        ]

    effective_authorizations:
        [
            "collector+tr_ph#hcp",
            "collector+au_ph#hcp",
            "config_reader+tr_ph#hcp",
        ]

    full_access_roles:
        [
            "collector",
        ]
    """

    primary_role: str | None

    effective_roles: list[str]

    effective_authorizations: list[str]

    full_access_roles: list[str]

    evaluated_at: datetime
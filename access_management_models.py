"""Dataclass models for the `ng-access-management` DynamoDB single-table design.

Each record type (ROLE, ASSIGNMENT, TOKEN, AUDIT) is modelled as a dataclass.
Every field is annotated; the inline comment lists the possible values (where
constrained) and one sample value taken from the design document.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class RoleRecord:
    """A role definition synced from Azure AD (entity_type = ROLE)."""

    pk: str                       # "ROLE#{role_object_id}"        e.g. "ROLE#fcb2b37b-5da0-166b-9b83-0014b67a7c10"
    sk: str                       # "ROLE#{role_code}"             e.g. "ROLE#role_admin"
    entity_type: str              # constant "ROLE"                e.g. "ROLE"
    role_object_id: str           # Azure AD object id             e.g. "fcb2b37b-5da0-166b-9b83-0014b67a7c10"
    role_code: str                # stable business code           e.g. "role_admin"
    display_name: str             # display only                   e.g. "Admin"
    description: str              # display only                   e.g. "Full administrative access"
    precedence: int               # lower number = higher priority e.g. 10
    status: str                   # ACTIVE | INACTIVE              e.g. "ACTIVE"
    created_at: str               # ISO datetime                   e.g. "2026-01-01T00:00:00Z"
    created_by: str               # actor                          e.g. "devesh yadav"
    updated_at: str               # ISO datetime                   e.g. "2026-02-01T00:00:00Z"
    updated_by: str               # actor                          e.g. "devesh yadav"


@dataclass
class AssignmentRecord:
    """A role assignment granted to a principal (entity_type = ASSIGNMENT)."""

    pk: str                       # "PRINCIPAL#{principal_type}#{principal_id}"  e.g. "PRINCIPAL#USER#933e5c5e-8a9b-40f3-ab8a"
    sk: str                       # "ASSIGNMENT#{assignment_id}"                 e.g. "ASSIGNMENT#1767225600"
    entity_type: str              # constant "ASSIGNMENT"          e.g. "ASSIGNMENT"
    assignment_id: int            # Unix epoch (seconds), unique   e.g. 1767225600
    principal_type: str           # USER | GROUP | APPLICATION     e.g. "USER"
    principal_id: str             # object id / group id / app id  e.g. "933e5c5e-8a9b-40f3-ab8a"
    app_id: str                   # client app id (applications)   e.g. "aba5203b"
    principal_name: str           # display only                   e.g. "devesh yadav"
    role_code: str                # FK to a ROLE                   e.g. "role_admin"
    access_mode: str              # FULL | SCOPED                  e.g. "FULL"
    authorization_scopes: list[str]  # scopes when SCOPED          e.g. ["tr_ph#hcp"]
    status: str                   # ACTIVE | INACTIVE | REVOKED    e.g. "ACTIVE"
    valid_from: str               # ISO datetime (start of window) e.g. "2026-01-01"
    valid_to: str                 # ISO datetime (end of window)   e.g. "2026-12-31"
    source: str                   # manual | import | sync         e.g. "manual"
    created_at: str               # ISO datetime (audit)           e.g. "2026-01-01T00:00:00Z"
    created_by: str               # actor (audit)                  e.g. "devesh yadav"
    updated_at: str               # ISO datetime (audit)           e.g. "2026-02-01T00:00:00Z"
    updated_by: str               # actor (audit)                  e.g. "devesh yadav"


@dataclass
class TokenRecord:
    """An API access token bound to an assignment (entity_type = TOKEN)."""

    pk: str                       # "TOKEN#{token_hash}"           e.g. "TOKEN#e1b0c44298fc1c149afbf4c8996fb"
    sk: str                       # "ASSIGNMENT#{assignment_id}"   e.g. "ASSIGNMENT#1767225600"
    entity_type: str              # constant "TOKEN"               e.g. "TOKEN"
    token_hash: str               # SHA-256 hash of the token      e.g. "e1b0c44298fc1c149afbf4c8996fb"
    assignment_id: int            # Unix epoch; linked assignment  e.g. 1767225600
    principal_type: str           # USER | GROUP | APPLICATION     e.g. "USER"
    principal_id: str             # denormalized principal id      e.g. "933e5c5e-8a9b-40f3-ab8a"
    role_code: str                # FK to a ROLE                   e.g. "role_admin"
    authorization_scopes: list[str]  # scopes granted to token     e.g. ["tr_ph#hcp"]
    issued_at: str                # ISO datetime                   e.g. "2026-01-01T00:00:00Z"
    expires_at: str               # ISO datetime                   e.g. "2026-12-31T23:59:59Z"
    usage_limit: int              # max allowed uses               e.g. 100
    usage_count: int              # uses so far (tracked)          e.g. 0
    status: str                   # ACTIVE | EXPIRED | REVOKED     e.g. "ACTIVE"
    last_used_at: str             # ISO datetime                   e.g. "2026-02-15T10:12:00Z"
    created_at: str               # ISO datetime (audit)           e.g. "2026-01-01T00:00:00Z"
    created_by: str               # actor (audit)                  e.g. "devesh yadav"


@dataclass
class AuditRecord:
    """An immutable audit record of an assignment change (entity_type = AUDIT)."""

    pk: str                       # "AUDIT#{audit_id}"             e.g. "AUDIT#7b2c1f0e-3a11-4c2b-9d44-0f1a2b3c4d5e"
    sk: str                       # "ASSIGNMENT#{assignment_id}"   e.g. "ASSIGNMENT#1767225600"
    entity_type: str              # constant "AUDIT"               e.g. "AUDIT"
    audit_id: str                 # unique audit id (uuid)         e.g. "7b2c1f0e-3a11-4c2b-9d44-0f1a2b3c4d5e"
    assignment_id: int            # Unix epoch; audited assignment e.g. 1767225600
    principal_type: str           # USER | GROUP | APPLICATION     e.g. "USER"
    principal_id: str             # principal object id (context)  e.g. "933e5c5e-8a9b-40f3-ab8a"
    role_code: str                # role on the assignment         e.g. "role_admin"
    change_type: str              # CREATE | UPDATE | REVOKE       e.g. "CREATE"
    changed_fields: list[str]     # names changed; ["*"] on create e.g. ["authorization_scopes"]
    before: dict[str, Any]        # full prior snapshot; null on create  e.g. {"status": "ACTIVE"}
    after: dict[str, Any]         # full new snapshot; null on hard delete  e.g. {"role_code": "role_admin", "status": "ACTIVE"}
    status: str                   # status snapshot after change   e.g. "ACTIVE"
    source: str                   # manual | import | sync         e.g. "manual"
    changed_by: str               # actor who made the change      e.g. "devesh yadav"
    changed_at: str               # ISO datetime of the change     e.g. "2026-01-01T00:00:00Z"

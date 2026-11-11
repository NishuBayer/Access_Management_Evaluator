from dataclasses import dataclass
from typing import Any

@dataclass
class RoleRecord:
    role_code:str
    precedence:int
    status:str='ACTIVE'

@dataclass
class AssignmentRecord:
    assignment_id:int
    principal_type:str
    role_code:str
    access_mode:str
    authorization_scopes:list[str]
    status:str
    valid_from:str
    valid_to:str
    created_at:str

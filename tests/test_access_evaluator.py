from datetime import datetime,timezone
from dataclasses import dataclass
from access_evaluator.access_evaluator import AccessEvaluator

@dataclass
class Role: precedence:int
@dataclass
class Assignment:
    role_name:str
    principal_type:str
    access_mode:str
    scopes:list
    status:bool=True
    valid_from:datetime|None=None
    valid_to:datetime|None=None
    created_at:datetime=datetime.now(timezone.utc)

def test_user_scope_overrides_group_full():
    ev=AccessEvaluator()
    r={'collector':Role(10)}
    result=ev.evaluate([
      Assignment('collector','USER','SCOPED',['tr_ph#hcp']),
      Assignment('collector','GROUP','FULL',[])
    ],r)
    assert result.full_access_roles==[]
    assert 'collector:tr_ph#hcp' in result.effective_authorizations

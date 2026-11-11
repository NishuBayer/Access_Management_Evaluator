from evaluation.models import RoleRecord, AssignmentRecord
from evaluation.access_evaluator import AccessEvaluator

def test_user_beats_group_full():
    r=[RoleRecord('collector',20)]
    a=[
        AssignmentRecord(1,'USER','collector','SCOPED',['tr_ph#hcp'],'ACTIVE','2026-01-01T00:00:00Z','2027-12-31T00:00:00Z','2026-01-01T00:00:00Z'),
        AssignmentRecord(2,'GROUP','collector','FULL',[],'ACTIVE','2026-01-01T00:00:00Z','2027-12-31T00:00:00Z','2026-01-01T00:00:00Z')
    ]
    result=AccessEvaluator().evaluate_access(a,r)
    assert result.full_access_roles==[]

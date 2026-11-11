class EvaluationError(Exception):
    """Base evaluator exception."""


class UnknownRoleError(EvaluationError):
    """Role not found or inactive."""
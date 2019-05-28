#
#
#

class ProfetaException(Exception):
    pass

class NotABeliefException(ProfetaException):
    pass

class NotAProcedureException(ProfetaException):
    pass

class NotAnActionListException(ProfetaException):
    pass

class InvalidContextException(ProfetaException):
    pass

class InvalidContextConditionException(ProfetaException):
    pass

class UnboundVariableException(ProfetaException):
    pass

class NotAGroundTermException(ProfetaException):
    pass

class MethodNotOverriddenException(ProfetaException):
    pass

class InvalidPlanException(ProfetaException):
    pass

class InvalidMethodException(ProfetaException):
    pass

class CannotSuspendACancelPlanException(ProfetaException):
    pass

class InvalidTagException(ProfetaException):
    pass


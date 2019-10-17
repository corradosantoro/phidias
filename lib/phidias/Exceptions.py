#
#
#

class PhidiasException(Exception):
    pass

class NotABeliefException(PhidiasException):
    pass

class NotAProcedureException(PhidiasException):
    pass

class NotAnActionListException(PhidiasException):
    pass

class InvalidContextException(PhidiasException):
    pass

class InvalidContextConditionException(PhidiasException):
    pass

class UnboundVariableException(PhidiasException):
    pass

class NotAGroundTermException(PhidiasException):
    pass

class MethodNotOverriddenException(PhidiasException):
    pass

class InvalidPlanException(PhidiasException):
    pass

class InvalidMethodException(PhidiasException):
    pass

class CannotSuspendACancelPlanException(PhidiasException):
    pass

class InvalidTagException(PhidiasException):
    pass

class InvalidDestinationException(PhidiasException):
    pass


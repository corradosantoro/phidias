#
#
#

class HEPException(Exception):
    pass

class NotABeliefException(HEPException):
    pass

class NotAProcedureException(HEPException):
    pass

class NotAnActionListException(HEPException):
    pass

class InvalidContextException(HEPException):
    pass

class InvalidContextConditionException(HEPException):
    pass

class UnboundVariableException(HEPException):
    pass

class NotAGroundTermException(HEPException):
    pass

class MethodNotOverriddenException(HEPException):
    pass

class InvalidPlanException(HEPException):
    pass

class InvalidMethodException(HEPException):
    pass

class CannotSuspendACancelPlanException(HEPException):
    pass

class InvalidTagException(HEPException):
    pass


#
# Types.py
#

import sys
import types
import threading

from phidias.Globals import *
from phidias.Runtime import *
from phidias.Exceptions import *
from functools import reduce

__all__ = [ 'Belief', 'Reactor', 'SingletonBelief', 'Goal',
            'Action', 'Procedure', 'ActiveBelief',
            'def_vars', 'def_actor',
            'AddBeliefEvent', 'DeleteBeliefEvent',
            'Sensor', 'AsyncSensor',
            'DATA_TYPE_REACTOR' ]

CONSTANT = 0
VARIABLE = 1

DATA_TYPE_BELIEF = 1
DATA_TYPE_REACTOR = 2
DATA_TYPE_SINGLETON_BELIEF = 3

# -----------------------------------------------
class Constant(object):

    def __init__(self, uTerm):
        self.type = CONSTANT
        self.value = uTerm

    def __repr__(self):
       return repr(self.value)

    def __call__(self, *args):
        return self.value

    def bound(self):
        return True

    def clone(self):
        return Constant(self.value)


# -----------------------------------------------
class Variable(object):

    def __init__(self, uTerm):
        self.type = VARIABLE
        self.name = uTerm
        self.value = None

    def __repr__(self):
        if (self.value is None)or(not(GVARS.show_variable_values)):
            return self.name
        else:
            #return repr(self.name) + "(" + repr(self.value) + ")"
            return repr(self.__class__.__name__) + "(" + repr(self.value) + ")"

    def __call__(self, *args):
        if len(args) == 1:
            self.value = args[0]
        return self.value

    def __le__(self, uTerm):
        if not(isinstance(uTerm, Procedure)) and not(isinstance(uTerm, Action)):
            raise NotAProcedureException()
        uTerm.assignment = self
        return uTerm

    def bound(self):
        return self.value is not None

    def clone(self):
        v = Variable(self.name)
        v.value = self.value
        return v


#
# -----------------------------------------------
def def_vars(*vlist):
    if sys.implementation.name == "micropython":
        g = vlist[0]
        vlist = vlist[1:]
    for v in vlist:
        var = Variable(v)
        if sys.implementation.name != "micropython":
            globals()['__builtins__'][v] = var
        else:
            g[v] = var
        GVARS.variables[v] = var

def def_actor(a):
    Runtime.agent(a)

# -----------------------------------------------
class AtomicFormula(object):

    def __init__(self, *args, **kwargs):
        self.make_terms(args)
        self.data_type = None
        self.tag = None
        self.__bindings = {}
        self.iterate = False

    def __repr__(self):
        if len(self.__terms) == 0:
            repr_string = self.__class__.__name__ + "()"
        else:
            repr_string = self.__class__.__name__ + "(" + \
                reduce (lambda x,y : x + ", " + y,
                        map (lambda x: repr(x), self.__terms)) + \
                        ")"
        return repr_string

    def clone(self):
        t = [ ]
        for term in self.__terms:
            if isinstance(term, Variable):
                t.append(term.clone())
            elif isinstance(term, Constant):
                t.append(term.clone())
            else:
                t.append(term)
        af = self.__class__(*t)
        af.data_type = self.data_type
        af.tag = self.tag
        af.__bindings = self.__bindings
        return af

    def name(self):
        return self.__class__.__name__

    def terms(self):
        return self.__terms

    def set_terms(self, t):
        self.__terms = t

    def string_terms(self):
        return [ x.value for x in self.__terms ]

    def bind(self, b):
        self.__bindings = b

    def make_terms(self, args):
        self.__terms = []
        for t in args:
            if isinstance(t, Variable):
                v = t
            elif isinstance(t, Constant):
                v = t
            else:
                v = Constant(t)
            self.__terms.append(v)

    def __eq__(self, uT):
        return self.match_constants(uT)

    def match_constants(self, uT):
        l = len(self.__terms)
        uTerms = uT.terms()
        if l != len(uTerms):
            return False
        for i in range(0, l):
            Lhs = self.__terms[i]
            Rhs = uTerms[i]
            if (Lhs.type == VARIABLE)or(Rhs.type == VARIABLE):
                return True
            if Lhs.value != Rhs.value:
                return False
        return True


    # self --> belief with constant terms
    # uT ----> belief with variables
    def match(self, uT):
        l = len(self.__terms)
        uTerms = uT.terms()
        if l != len(uTerms):
            return False
        for i in range(0, l):
            Lhs = self.__terms[i]
            Rhs = uTerms[i]
            if Lhs.type == VARIABLE:
                raise NotAGroundTermException()
            if Rhs.type == VARIABLE:
                if Rhs.name in self.__bindings:
                    value = self.__bindings[Rhs.name]
                else:
                    value = Lhs.value # var unbound, get the same value of Lhs
                    self.__bindings[Rhs.name] = value
            else:
                value = Rhs.value
            if Lhs.value != value:
                return False
        return True


    # self --> belief with constant terms or varibles
    # uT ----> belief with variables
    def prolog_match(self, uT):
        l = len(self.__terms)
        uTerms = uT.terms()
        if l != len(uTerms):
            return False
        for i in range(0, l):
            Lhs = self.__terms[i]
            Rhs = uTerms[i]
            if Lhs.type == VARIABLE:
                if Lhs.name in self.__bindings:
                    value = self.__bindings[Lhs.name]
                else:
                    if Rhs.type == VARIABLE:
                        continue #var unbound, true in any case
                    else:
                        # lhs variable, but rhs constant... NO!
                        return False
            else:
                if Rhs.type == VARIABLE:
                    if Rhs.name in self.__bindings:
                        value = self.__bindings[Rhs.name]
                    else:
                        value = Lhs.value # var unbound, get the same value of Lhs
                        self.__bindings[Rhs.name] = value
                else:
                    value = Rhs.value
            if Lhs.value != value:
                return False
        return True


    def assign(self, ctx):
        for i in range(len(self.__terms)):
            t = self.__terms[i]
            if t.type == VARIABLE:
                if t.name in ctx:
                    self.__terms[i] = Constant(ctx[t.name])
                else:
                    raise UnboundVariableException()

    def assign_partial(self, ctx):
        for i in range(len(self.__terms)):
            t = self.__terms[i]
            if t.type == VARIABLE:
                if t.name in ctx:
                    self.__terms[i] = Constant(ctx[t.name])

    def assign_vars_from_formula(self, ctx, atomic_formula):
        val_terms = atomic_formula.terms()
        val_terms_length = len(val_terms)
        for i in range(len(self.__terms)):
            t = self.__terms[i]
            if t.type == VARIABLE:
                if i < val_terms_length:
                    value = ctx[val_terms[i].name]
                    del ctx[val_terms[i].name]
                    ctx[t.name] = value
                else:
                    raise UnboundVariableException()


# -------------------------------------------------
class AddDelBeliefEvent:

    ADD = 1
    DEL = 2

    def __init__(self, uBel):
        self.__belief = uBel
        self.event_type = 0
        self.iterate = False

    def __repr__(self):
        return self.sign() + repr(self.__belief)

    def __eq__(self, other):
        return self.__belief == other.get_belief()

    def name(self):
        return self.sign() + self.__belief.name()

    def get_belief(self):
        return self.__belief

    def __rshift__(self, actionList):
        if isinstance(actionList, list):
            p = Plan(self, None, actionList)
            Runtime.add_plan(p)
            return p
        else:
            raise NotAnActionListException()

    def __truediv__(self, uTerm):
        return self.__div_operator(uTerm)

    def __div__(self, uTerm):
        return self.__div_operator(uTerm)

    def __div_operator(self, uTerm):
        if isinstance(uTerm, Belief):
            p = Plan(self, ContextCondition(uTerm))
            Runtime.add_plan(p)
            return p
        elif isinstance(uTerm, ActiveBelief):
            p = Plan(self, ContextCondition(uTerm))
            Runtime.add_plan(p)
            return p
        elif isinstance(uTerm, Goal):
            p = Plan(self, ContextCondition(uTerm))
            Runtime.add_plan(p)
            return p
        elif isinstance(uTerm, ContextCondition):
            p = Plan(self, uTerm)
            Runtime.add_plan(p)
            return p
        else:
            raise InvalidContextException()



# -------------------------------------------------
class AddBeliefEvent(AddDelBeliefEvent):

    def __init__(self, uBel):
        AddDelBeliefEvent.__init__(self, uBel)
        self.event_type = AddDelBeliefEvent.ADD

    def sign(self):
        return '+'

# -------------------------------------------------
class DeleteBeliefEvent(AddDelBeliefEvent):

    def __init__(self, uBel):
        AddDelBeliefEvent.__init__(self, uBel)
        self.event_type = AddDelBeliefEvent.DEL

    def sign(self):
        return '-'

# -----------------------------------------------
class Belief(AtomicFormula):

    def __init__(self, *args, **kwargs):
        AtomicFormula.__init__(self, *args, **kwargs)
        self.data_type = DATA_TYPE_BELIEF
        self.dest = None
        self.source = None
        self.source_agent = None

    def clone(self):
        bf = AtomicFormula.clone(self)
        bf.data_type = self.data_type
        bf.dest = self.dest
        bf.source = self.source
        bf.source_agent = self.source_agent
        return bf

    def __repr__(self):
        s = AtomicFormula.__repr__(self)
        modifs = ""
        if self.dest is not None:
            modifs = "'to':" + repr(self.dest) + ","
        if self.source is not None:
            modifs = "'from':" + repr(self.source) + ","
        if modifs != "":
            modifs = "[{" + modifs[:-1] + "}]"
        return s + modifs

    def name(self):
        return self.__class__.__name__

    def __and__(self, rhs):
        return ContextCondition(self, rhs)

    # +bel generates a Plan that is stored in plan database
    def __pos__(self):
        return AddBeliefEvent(self)

    # -bel generates a Plan that is stored in plan database
    def __neg__(self):
        return DeleteBeliefEvent(self)

    def __getitem__(self, uModifiers):
        if 'to' in uModifiers:
            self.dest = uModifiers['to']
        if 'from' in uModifiers:
            self.source = uModifiers['from']
        return self


# -----------------------------------------------
class Reactor(Belief):

    def __init__(self, *args, **kwargs):
        Belief.__init__(self, *args, **kwargs)
        self.data_type = DATA_TYPE_REACTOR


# -----------------------------------------------
class SingletonBelief(Belief):

    def __init__(self, *args, **kwargs):
        Belief.__init__(self, *args, **kwargs)
        self.data_type = DATA_TYPE_SINGLETON_BELIEF


# -----------------------------------------------
class ActiveBelief(AtomicFormula):

    def __and__(self, rhs):
        return ContextCondition(self, rhs)

    def do_evaluate(self, ctx):
        args = []
        for t in self.terms():
            if t.type == CONSTANT:
                args.append(t) #.value)
            elif t.type == VARIABLE:
                if t.name in ctx:
                    t.value = ctx[t.name]
                args.append(t)
        if self.evaluate(*args):
            for t in args:
                if t.type == VARIABLE:
                    if t.value is not None:
                        ctx[t.name] = t.value
            return True
        else:
            return False


    def evaluate(self, *args):
        raise MethodNotOverriddenException()

# -----------------------------------------------
class Action(AtomicFormula):

    def __init__(self, *args, **kwargs):
        AtomicFormula.__init__(self, *args, **kwargs)
        self.current_agent = Runtime.currentAgent
        self.engine = Runtime.get_engine(self.current_agent)
        self.method = None
        self.assignment = None

    def clone(self):
        ca = super(Action, self).clone()
        ca.current_agent = self.current_agent
        ca.engine = self.engine
        ca.method = self.method
        ca.assignment = self.assignment
        return ca

    #def __getattr__(self, uAttrName):
    #    self.method = getattr(self.__class__,  'on_' + uAttrName )
    #    return self

    def assert_belief(self, uBel):
        self.engine.add_belief(uBel)

    def retract_belief(self, uBel):
        self.engine.remove_belief(uBel)

    def do_execute(self, ctx):
        args = []
        for t in self.terms():
            if t.type == CONSTANT:
                args.append(t)
            elif t.type == VARIABLE:
                if t.name in ctx:
                    t.value = ctx[t.name]
                args.append(t)
        if self.method is None:
            rv = self.execute(*args)
        else:
            #if sys.implementation.name == "micropython":
            args.insert(0, self)
            rv = self.method(*args)
        for t in self.terms():
            if t.type == VARIABLE:
                if t.name in ctx:
                    ctx[t.name] = t.value
        return rv


    def execute(self, *args):
        raise MethodNotOverriddenException()


# ------------------------------------------------
class ContextCondition(object):

    def __init__(self, lhs, rhs = None):
        if rhs is None:
            self.__condition_terms = [ lhs ]
        else:
            self.__condition_terms = [ lhs, rhs ]

    def __repr__(self):
        repr_string = "(" + \
            reduce (lambda x,y : x + " & " + y,
                    map (lambda x: repr(x), self.__condition_terms)) + \
                    ")"
        return repr_string

    def __and__(self, rhs):
        if isinstance(rhs, Belief) or isinstance(rhs, ActiveBelief) or isinstance(rhs, Goal) or type(rhs) == types.LambdaType:
            self.__condition_terms.append(rhs)
            return self
        else:
            raise InvalidContextConditionException()

    def terms(self):
        return self.__condition_terms


# -------------------------------------------------
class Procedure(AtomicFormula):

    PROC = 3
    PROC_CANCEL = 4

    def __init__(self, *args, **kwargs):
        super(Procedure, self).__init__(*args, **kwargs)
        self.event_type = Procedure.PROC
        self.__additional_event = None
        self.assignment = None

    def clone(self):
        cp = super(Procedure, self).clone()
        cp.event_type = self.event_type
        cp.__additional_event = self.__additional_event
        cp.assignment = self.assignment
        return cp

    def additional_event(self):
        return self.__additional_event

    def name(self):
        if self.event_type == Procedure.PROC_CANCEL:
            s = "-"
        else:
            s = ""
        return s + super(Procedure, self).name()

    def basename(self):
        return super(Procedure, self).name()

    def __getitem__(self, uTag):
        if uTag == 'all':
            self.iterate = True
            return self
        else:
            raise InvalidTagException()

    def __neg__(self):
        self.event_type = Procedure.PROC_CANCEL
        return self

    def __repr__(self):
        if self.event_type == Procedure.PROC_CANCEL:
            s = "-" + AtomicFormula.__repr__(self)
        else:
            s = AtomicFormula.__repr__(self)
        if self.iterate:
            s = s + "['all']"
        if self.__additional_event is not None:
            s = s + " / " + repr(self.__additional_event)
        if self.assignment is not None:
            s = self.assignment.name + " <= " + s
        return s

    def __rshift__(self, actionList):
        if isinstance(actionList, list):
            p = Plan(self, None, actionList)
            Runtime.add_plan(p)
            return p
        else:
            raise NotAnActionListException()

    def __truediv__(self, uTerm):
        return self.__div_operator(uTerm)

    def __div__(self, uTerm):
        return self.__div_operator(uTerm)

    def __div_operator(self, uTerm):
        if isinstance(uTerm, AddBeliefEvent):
            if self.event_type == Procedure.PROC_CANCEL:
                raise CannotSuspendACancelPlanException()
            self.__additional_event = uTerm
            return self
        elif isinstance(uTerm, Belief):
            p = Plan(self, ContextCondition(uTerm))
            Runtime.add_plan(p)
            return p
        elif isinstance(uTerm, ActiveBelief):
            p = Plan(self, ContextCondition(uTerm))
            Runtime.add_plan(p)
            return p
        elif isinstance(uTerm, Goal):
            p = Plan(self, ContextCondition(uTerm))
            Runtime.add_plan(p)
            return p
        elif isinstance(uTerm, ContextCondition):
            p = Plan(self, uTerm)
            Runtime.add_plan(p)
            return p
        else:
            raise InvalidContextException()


# -----------------------------------------------
class Goal(AtomicFormula):

    def __init__(self, *args, **kwargs):
        AtomicFormula.__init__(self, *args, **kwargs)
        self.__context_condition = None

    def clone(self):
        gl = AtomicFormula.clone(self)
        return gl

    def __lshift__(self, condition):
        if isinstance(condition, ContextCondition):
            self.__context_condition = condition
            p = Plan(self, self.__context_condition)
            Runtime.add_goal(p)
            return self
        elif isinstance(condition, Belief):
            self.__context_condition = ContextCondition(condition)
            p = Plan(self, self.__context_condition)
            Runtime.add_goal(p)
            return self
        else:
            raise InvalidContextException()

    def __and__(self, rhs):
        return ContextCondition(self, rhs)

    def context_condition(self):
        return self.__context_condition




# -----------------------------------------------
# BASIC SENSOR
# This is the basic sensor class.
# It has a *blocking* semantics, it is executed,
# by the runtine, within a separate thread
# -----------------------------------------------
class SensorStarter(Action):

    def __init__(self, uSensor):
        Action.__init__(self)
        self.sensor = uSensor
        self.set_terms(uSensor.terms())

    def execute(self, *args):
        self.sensor.on_sense_start(*args)


class SensorRestarter(Action):

    def __init__(self, uSensor):
        Action.__init__(self)
        self.sensor = uSensor
        self.set_terms(uSensor.terms())

    def execute(self, *args):
        self.sensor.on_restart(*args)


class SensorStopper(Action):

    def __init__(self, uSensor):
        Action.__init__(self)
        self.sensor = uSensor
        self.set_terms(uSensor.terms())

    def execute(self, *args):
        self.sensor.on_sense_stop(*args)


class Sensor(Action):

    METHODS = [ 'bind', 'unbind', 'start', 'stop' ]

    def __init__(self, *args, **kwargs):
        Action.__init__(self, *args, **kwargs)
        self.thread = None
        self._stopped = False
        #self.start = SensorStarter(*args)
        #self.start.sensor = self
        #self.stop = SensorStopper(*args)
        #self.stop.sensor = self

    def clone(self):
        cs = super(Sensor, self).clone()
        cs.thread = self.thread
        cs._stopped = self.stopped
        #cs.start = self.start
        #cs.start.sensor = cs
        #cs.stop = self.stop
        #cs.stop.sensor = cs
        return cs

    def start(self):
        return SensorStarter(self)

    def restart(self):
        return SensorRestarter(self)

    def stop(self):
        return SensorStopper(self)

    def __getattr__(self, uAttrName):
        return getattr(self.__class__, uAttrName)

    def __setattr__(self, uAttrName, uValue):
        setattr(self.__class__, uAttrName, uValue)

    def on_sense_bind(self, *args):
        pass

    def on_sense_unbind(self, *args):
        pass

    def on_sense_start(self, *args):
        if self.engine.get_sensor(self) is None:
            self.engine.add_sensor(self)
            self._stopped = False
            self.on_start(*args)
            t = threading.Thread(target = self.do_sense)
            t.daemon = True
            t.start()
            self.thread = t
        else:
            self.on_restart(*args)

    def on_sense_stop(self, *args):
        self._stopped = True
        self.engine.del_sensor(self)
        self.on_stop(*args)

    def stopped(self):
        return self._stopped

    def do_sense(self):
        self.sense()
        self.engine.del_sensor(self)

    def execute(self, *args):
        pass

    # callback
    def on_start(self, *args):
        pass

    # callback
    def on_restart(self, *args):
        pass

    # callback
    def on_stop(self, *args):
        pass

    # main method: sense is intended to be blocking
    def sense(self):
        raise MethodNotOverriddenException()


# -----------------------------------------------
# PERIODIC SENSOR
# -----------------------------------------------
class PeriodicSensor(Sensor):

    # sense is intended to be non-blocking
    def sense(self):
        raise MethodNotOverriddenException()


# -----------------------------------------------
# ASYNC SENSOR
# -----------------------------------------------
class AsyncSensor(Sensor):

    # sense is intended to be non-executed
    def sense(self):
        pass

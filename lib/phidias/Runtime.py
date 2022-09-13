#
# Runtime.py
#

import types
import threading
#import copy

from phidias.Types import *
from phidias.Knowledge import *
from phidias.Exceptions import *
from phidias.Messaging import *

DEFAULT_AGENT = "main"

__all__ = [ 'DEFAULT_AGENT', 'Runtime', 'Plan' ]

# ------------------------------------------------
class EventQueue:

    def __init__(self):
        self.__c = threading.Condition()
        self.__data = []
        self.__size = 0
        self.__subscriptions = { }

    def subscribe(self, uEvt):
        self.__c.acquire()
        self.__subscriptions[uEvt.name()] = True
        self.__c.release()

    def unsubscribe(self, uEvt):
        self.__c.acquire()
        if uEvt.name() in self.__subscriptions:
            del self.__subscriptions[uEvt.name()]
        self.__c.release()

    # put the event at queue tail
    def put(self, uEvent):
        self.__c.acquire()
        if uEvent.name() in self.__subscriptions:
            self.__data.append(uEvent)
            self.__size += 1
            self.__c.notify()
        self.__c.release()

    # put the event at queue head (so, this will be the first event to be dequeued)
    def put_top(self, uEvent):
        self.__c.acquire()
        if uEvent.name() in self.__subscriptions:
            self.__data.insert(0, uEvent)
            self.__size += 1
            self.__c.notify()
        self.__c.release()

    def get(self, timeout = None):
        self.__c.acquire()

        while self.__size == 0:
            self.__c.wait(timeout)
            if self.__size == 0:
                self.__c.release()
                return None

        item = self.__data.pop(0)
        self.__size -= 1
        self.__c.release()
        return item

    def wait_item(self):
        self.__c.acquire()
        while self.__size == 0:
            self.__c.wait()
        self.__c.release()

    def empty(self):
        self.__c.acquire()
        retval = self.__size == 0
        self.__c.release()
        return retval

    def find_and_remove_event(self, uType, uBel):
        self.__c.acquire()

        for e in self.__data:
            #print("%d,%d - %s,%s" % (e.event_type, uType, repr(e.get_belief()), uBel))
            if (e.event_type == uType)and(e.get_belief() == uBel):
                #print(type(e))
                self.__data.remove(e)
                self.__size -= 1
                self.__c.release()
                return True

        self.__c.release()
        return False


# ------------------------------------------------
class Plan:

    def __init__(self, uEvent, uContextCondition = None, uActions = []):
        self.__event = uEvent
        self.__context_condition = uContextCondition
        self.__actions = uActions

    def context_condition(self):
        return self.__context_condition

    def event(self):
        return self.__event

    def actions(self):
        return self.__actions

    def __repr__(self):
        if self.__context_condition is None:
            return repr(self.__event) + " >> " + repr(self.__actions)
        else:
            return repr(self.__event) + \
              " / " + repr(self.__context_condition) + " >> " + repr(self.__actions)

    def __rshift__(self, actionList):
        if isinstance(actionList, list):
            self.__actions = actionList
        else:
            raise NotAnActionListException()


# ------------------------------------------------
class PlanBase:

    def __init__(self):
        self.__plans = {}

    def __repr__(self):
        return repr(self.__plans)

    def add_plan(self, p):
        name = p.event().name()
        if name in self.__plans:
            self.__plans[name].append(p)
        else:
            self.__plans[name] = [ p ]

    def get_plans_from_event(self, uEvt):
        name = uEvt.name()
        if name in self.__plans:
            return self.__plans[name]
        else:
            return []

    def list_all_plans(self):
        all_plans = [ ]
        for b in self.__plans:
            for p in self.__plans[b]:
                all_plans.append(p)
        return all_plans

# ------------------------------------------------
class Intention:

    INTENTION_NEXT = 0
    INTENTION_END = 1
    INTENTION_PROC = 2

    def __init__(self, uEngine, uCtx, uPlan):
        self.__engine = uEngine
        self.__context = uCtx
        self.__action_list = uPlan.actions()
        self.__action_index = 0
        self.__action_len = len(self.__action_list)
        self.__return_value = None
        self.__pending_assignment = None

    def get_return_value(self):
        return self.__return_value

    def execute_next(self, last_ret_value):
        if self.__action_index == self.__action_len:
            return (Intention.INTENTION_END, None) # end of execution

        if self.__pending_assignment is not None:
            self.__context[self.__pending_assignment] = last_ret_value

        a = self.__action_list[self.__action_index]
        self.__action_index += 1

        from phidias.Types import Action, AddBeliefEvent, DeleteBeliefEvent, Procedure, Variable

        if isinstance(a, Action):
            ret_val = a.do_execute(self.__context)
            if a.assignment is not None:
                self.__context[a.assignment.name] = ret_val
        elif isinstance(a, AddBeliefEvent):
            # FIXME! Check if the event queue has already a analogous "-" event
            #copied_b = copy.deepcopy(a.get_belief())
            copied_b = a.get_belief().clone()
            copied_b.assign(self.__context)
            if copied_b.dest is None:
                self.__engine.add_belief(copied_b)
            else:
                if isinstance(copied_b.dest, Variable):
                    d = copied_b.dest.value
                else:
                    d = copied_b.dest
                (remote_agent, a_name, site_name) = Messaging.local_or_remote(d)
                if remote_agent:
                    Messaging.send_belief(a_name, site_name, copied_b, self.__engine.agent())
                    #print("Remote messaging to {}@{} is not supported".format(a_name,site_name))
                else:
                    e = Runtime.get_engine(d) #copied_b.dest)
                    copied_b.source_agent = self.__engine.agent()
                    e.add_belief(copied_b)
        elif isinstance(a, DeleteBeliefEvent):
            # FIXME! Check if the event queue has already a analogous "+" event
            #copied_b = copy.deepcopy(a.get_belief())
            copied_b = a.get_belief().clone()
            copied_b.assign(self.__context)
            self.__engine.remove_belief(copied_b)
        elif isinstance(a, Procedure):
            if a.assignment is not None:
                self.__pending_assignment = a.assignment.name # get variable name
            #copied_a = copy.deepcopy(a)
            copied_a = a.clone()
            copied_a.assign(self.__context)
            return (Intention.INTENTION_PROC, copied_a)
        elif isinstance(a, str):
            exec(a, self.__context)
        elif isinstance(a, Variable):
            self.__return_value = self.__context[a.name]

        return (Intention.INTENTION_NEXT, None)

# ------------------------------------------------
class WaitingPlansCollection:

    def __init__(self, uEngine):
        self.__plans_by_proc = { }
        self.__plans_by_event = { }
        self.__engine = uEngine

    def all(self):
        return (self.__plans_by_proc, self.__plans_by_event)

    def add(self, uProcedure, uCtxsPlans):
        n = uProcedure.name()
        if n in self.__plans_by_proc:
            print("plan " + n + " is already in waiting")
            raise InvalidPlanException()
        else:
            self.__plans_by_proc[n] = uCtxsPlans
            for (c, p) in uCtxsPlans:
                e = p.event().additional_event()
                if e is None:
                    print("Procedure plan " + n + " has not the waiting event which is instead expected")
                    raise InvalidPlanException()
                self.__engine.queue().subscribe(e)
                n1 = e.name()
                #print("activating event ", n1)
                if n1 in self.__plans_by_event:
                    self.__plans_by_event[n1].append(p)
                else:
                    self.__plans_by_event[n1] = [ p ]

    def remove(self, uCtxPlan):
        (ctx, plan) = uCtxPlan
        # first find the plan in __plans_by_proc
        n = plan.event().name()
        self.remove_by_name(n)

    def remove_by_name(self, n):
        if n in self.__plans_by_proc:
            plans_to_remove = self.__plans_by_proc[n]
            del self.__plans_by_proc[n]
            for (c, p) in plans_to_remove:
                e = p.event().additional_event()
                if e is not None:
                    self.__engine.queue().unsubscribe(e)
                    n1 = e.name()
                    #print("removing event ", n1)
                    if n1 in self.__plans_by_event:
                        self.__plans_by_event[n1].remove(p)


    def get_plans_from_event(self, uEvt):
        name = uEvt.name()
        if name in self.__plans_by_event:
            return self.__plans_by_event[name]
        else:
            return []

# ------------------------------------------------
class SensorCollection(object):

    def __init__(self, uEngine):
        self.__engine = uEngine
        self.__sensors = { }

    def add_sensor(self, uSensor):
        self.__sensors[uSensor.__class__.__name__] = uSensor

    def get_sensor(self, uSensor):
        name = uSensor.__class__.__name__
        if name in self.__sensors:
            return self.__sensors[name]
        else:
            return None

    def del_sensor(self, uSensor):
        name = uSensor.__class__.__name__
        if name in self.__sensors:
            del self.__sensors[name]

# ------------------------------------------------
class Engine:

    def __init__(self, uAgentName):
        self.__kb = Knowledge()
        self.__plans = PlanBase()
        self.__goals = PlanBase()
        self.__event_queue = EventQueue()
        self.__running = False
        self.__intentions = [ ]
        self.__sensors = SensorCollection(self)
        self.__waiting_plans = WaitingPlansCollection(self)
        self.__agent = uAgentName

    def add_sensor(self, uSensor):
        self.__sensors.add_sensor(uSensor)

    def get_sensor(self, uSensor):
        return self.__sensors.get_sensor(uSensor)

    def del_sensor(self, uSensor):
        self.__sensors.del_sensor(uSensor)

    def queue(self):
        return self.__event_queue

    def agent(self):
        return self.__agent

    def add_plan(self, p):
        self.__plans.add_plan(p)
        self.__event_queue.subscribe(p.event())

    def add_goal(self, g):
        self.__goals.add_plan(g)

    def plans(self):
        return self.__plans

    def goals(self):
        return self.__goals

    def add_belief(self, uB):
        from phidias.Types import AddBeliefEvent, DATA_TYPE_REACTOR
        if uB.data_type != DATA_TYPE_REACTOR:
            r = self.__kb.add_belief(uB)
        else:
            r = True

        if r:
            self.__generate_event(AddBeliefEvent(uB))
        return r

    def remove_belief(self, uB):
        from phidias.Types import DeleteBeliefEvent, DATA_TYPE_REACTOR
        if uB.data_type != DATA_TYPE_REACTOR:
            r = self.__kb.remove_belief(uB)
        else:
            r = False

        if r:
            self.__generate_event(DeleteBeliefEvent(uB))
        return r

    def achieve(self, uG):
        self.__generate_event(uG)

    def achieve_goal(self, uG):
        return self.__plans_from_goal(uG)

    def knowledge(self):
        return self.__kb

    def stop(self):
        self.__running = False

    def waiting_plans(self):
        return self.__waiting_plans

    def __unify(self, uVars, uContext_condition):
        #contexts = [{}]
        contexts = [ uVars ]
        result = True
        #print(uContext_condition)
        from phidias.Types import Belief, ActiveBelief, Goal
        for t in uContext_condition.terms():
            match_result = False
            #print(t, type(t))
            if isinstance(t, Belief):
                matching_beliefs = self.__kb.get_matching_beliefs(t)
                #print (matching_beliefs)
                # "matching_beliefs" contains ground terms
                # "t" contains variables
                #print("Term: ", t, " ----> ", matching_beliefs)
                # here we are sure that "t" and elements in matching_beliefs
                # contains the same number of terms, moreover constants are
                # already matched, so we must only check variables
                new_contexts = []
                for m in matching_beliefs:
                    # each matching belief must be tested with each context
                    for c in contexts:
                        new = c.copy()
                        #print (t, m, new)
                        m.bind(new)
                        if m.match(t):
                            #print(new)
                            new_contexts.append(new)
                            match_result = True
                #print t, new_contexts
                contexts = new_contexts
            elif type(t) == types.LambdaType:
                new_contexts = []
                _bin = globals()['__builtins__']
                for c in contexts:
                    for (key,val) in c.items():
                        _bin[key] = val
                    #print(_bin)
                    if t():
                        new_contexts.append(c)
                        match_result = True
                    for (key,val) in c.items():
                        del _bin[key]
                contexts = new_contexts
            elif isinstance(t, ActiveBelief):
                new_contexts = []
                for c in contexts:
                    if t.do_evaluate(c):
                        new_contexts.append(c)
                        match_result = True
                contexts = new_contexts
            elif isinstance(t, Goal):
                new_contexts = []
                for c in contexts:
                    #print(c, t)
                    #copied_t = copy.deepcopy(t)
                    copied_t = t.clone()
                    copied_t.assign_partial(c)
                    matching_plans = self.__plans_from_goal(copied_t)#, c)
                    #print(copied_t, matching_plans)
                    if matching_plans != []:
                        for (ctx,p) in matching_plans:
                            copied_t.assign_vars_from_formula(ctx,p.event())
                            for (key,val) in c.items():
                                ctx[key] = val
                            new_contexts.append(ctx)
                            #print(ctx, p.event())
                            match_result = True
                    del copied_t
                contexts = new_contexts
            else:
                raise NotABeliefException()
            result = result and match_result
        #print(uContext_condition, contexts, result)
        return (result, contexts)


    # returns the plans matching the triggering event
    def __plans_from_triggering_event(self, uEvt, uPlanBase, uIsWaiting):
        selected_plans = [ ]
        event_belief = uEvt.get_belief()
        for p in uPlanBase:
            context = { }

            if uIsWaiting:
                b = p.event().additional_event().get_belief()
            else:
                b = p.event().get_belief()

            from phidias.Types import Variable, AddBeliefEvent
            if isinstance(uEvt, AddBeliefEvent):
                if isinstance(b.source, Variable):
                    v = b.source
                    v.value = event_belief.source_agent
                    context[v.name] = event_belief.source_agent
                else:
                    if b.source != event_belief.source_agent:
                        continue

            event_belief.bind(context)
            if event_belief.match(b):
                selected_plans.append(  (context, p) )
        return selected_plans


    # returns the plans matching the procedure
    def __plans_from_procedure(self, uP):
        non_event_plans = [ ]
        event_plans = [ ]
        for p in self.__plans.get_plans_from_event(uP):
            context = { }
            b = p.event()
            uP.bind(context)
            if uP.match(b):
                if p.event().additional_event() is None:
                    non_event_plans.append(  (context, p) )
                else:
                    event_plans.append(  (context, p) )
        return (non_event_plans, event_plans)


    # returns the plans matching the goal
    def __plans_from_goal(self, uG, initial_context = {}):
        goal_plans = [ ]
        for p in self.__goals.get_plans_from_event(uG):
            context = initial_context.copy()
            b = p.event()
            uG.bind(context)
            if uG.prolog_match(b):
                ok, ctxs = self.__unify(context, p.context_condition())
                if ok:
                    for c in ctxs:
                        goal_plans.append( (c, p) )
        return goal_plans


    # verify the conditions on plans and returns valid plans
    def find_applicable_plans(self, plans):
        resulting_plans = [ ]
        for (ctx, plan) in plans:
            pred = plan.context_condition()
            if pred is None:
                resulting_plans.append( (ctx, plan) )
            else:
                ok, ctxs = self.__unify(ctx, pred)
                if ok:
                    resulting_plans.append( (ctxs[0], plan) )
        return resulting_plans


    # verify the conditions on plans and returns first valid plan
    def find_first_applicable_plan(self, plans):
        for (ctx, plan) in plans:
            pred = plan.context_condition()
            if pred is None:
                return  ( [ctx], plan)
            else:
                ok, ctxs = self.__unify(ctx, pred)
                if ok:
                    #print(plan.event(), ctxs)
                    return  (ctxs, plan)
        return (None, None)


    # verify the conditions on plans and returns first and second valid plans
    def find_first_and_second_applicable_plans(self, plans):
        ret_plans = [ ]
        for (ctx, plan) in plans:
            pred = plan.context_condition()
            if pred is None:
                ret_plans.append( ([ctx], plan) )
            else:
                ok, ctxs = self.__unify(ctx, pred)
                if ok:
                    #print(plan.event(), ctxs)
                    ret_plans.append ( (ctxs, plan) )
            if len(ret_plans) == 2:
                break
        return ret_plans


    def make_intention(self, pctx):
        (context, plan) = pctx
        self.__intentions.insert( 0, Intention (self, context, plan) )


    def run(self):
        self.__running = True
        self.__last_return_value = None
        # This is the main loop of the PHIDIAS interpreter
        while self.__running:

            evt = None

            # self.__intentions contains the intention stack,
            # as soon as the intention stack contains plans to be executed
            # events are not processed, so first we execute intentions
            while self.__intentions != [ ]:
                top_intention = self.__intentions[0]
                (whats_next, evt) = top_intention.execute_next(self.__last_return_value)
                if whats_next == Intention.INTENTION_END:
                    # end of actions of intentions
                    # retrieve return value
                    v = top_intention.get_return_value()
                    if v is not None:
                        self.__last_return_value = v
                    self.__intentions.pop(0)
                elif whats_next == Intention.INTENTION_PROC:
                    break

            if evt is None:
                evt = self.__event_queue.get(0.5) #500millis
                if evt is None:
                    continue

            #print(self.__agent, evt)

            from_waiting_plans_flag = False

            from phidias.Types import AddBeliefEvent, DeleteBeliefEvent, Procedure
            if isinstance(evt, AddBeliefEvent):
                b = evt.get_belief()
                # ok... here we must first check if there are waiting plans
                plans = self.__plans_from_triggering_event(evt, self.__waiting_plans.get_plans_from_event(evt), True)
                if plans == []:
                    # no waiting plans, let's check "normal" plans
                    plans = self.__plans_from_triggering_event(evt, self.__plans.get_plans_from_event(evt), False)
                else:
                    from_waiting_plans_flag = True
            elif isinstance(evt, DeleteBeliefEvent):
                b = evt.get_belief()
                plans = self.__plans_from_triggering_event(evt, self.__plans.get_plans_from_event(evt), False)
            elif isinstance(evt, Procedure):
                if evt.event_type == Procedure.PROC_CANCEL:
                    self.__waiting_plans.remove_by_name(evt.basename())
                (non_event_plans, event_plans) = self.__plans_from_procedure(evt)
                # now check if plans have also a triggering event
                if (non_event_plans != [])and(event_plans != []):
                    print("Event plans cannot be combined with non-event plans")
                    raise InvalidPlanException()
                if event_plans != [ ]:
                    # the plans relevant to the Procedure call have waiting events,
                    # so we process them by adding to the waiting queue and skip execution
                    self.__waiting_plans.add(evt, event_plans)
                    continue
                else:
                    plans = non_event_plans
            else:
                continue

            #plans = self.find_applicable_plans(plans)
            first_and_second_plans = self.find_first_and_second_applicable_plans(plans)
            if first_and_second_plans == [ ]:
                continue
            (ctxs, plan) = first_and_second_plans[0]
            plan_to_execute = (ctxs[0], plan)
            if len(ctxs) > 1:
                if plan.event().iterate:
                    if len(first_and_second_plans) > 1:
                        # push the second plan first
                        self.make_intention(first_and_second_plans[1])
                    # push the first plan with all contexts in reverse
                    ctxs.reverse()
                    for c in ctxs:
                        self.make_intention( (c, plan) )
                    if from_waiting_plans_flag:
                        self.__waiting_plans.remove(plan_to_execute)
                    continue

            # select first plan and execute it
            self.make_intention(plan_to_execute)
            if from_waiting_plans_flag:
                self.__waiting_plans.remove(plan_to_execute)


    def __generate_event(self, uEvt):
        from phidias.Types import AddDelBeliefEvent, AddBeliefEvent, DeleteBeliefEvent
        if isinstance(uEvt, AddBeliefEvent):
            if self.__event_queue.find_and_remove_event(AddDelBeliefEvent.DEL, uEvt.get_belief()):
                return
        if isinstance(uEvt, DeleteBeliefEvent):
            if self.__event_queue.find_and_remove_event(AddDelBeliefEvent.ADD, uEvt.get_belief()):
                return
        self.__event_queue.put(uEvt)


# ------------------------------------------------
class Runtime:

    engines = { DEFAULT_AGENT : Engine(DEFAULT_AGENT) }
    currentAgent = DEFAULT_AGENT

    @classmethod
    def run_net(cls, _globals, protocol_type, *args, **kwargs):
        SUPPORTED_PROTOCOL_TYPES = {
            'http': start_message_server_http,
            'gateway': start_message_server_gateway,
            'raw': start_message_server_raw }

        protocol_impl = SUPPORTED_PROTOCOL_TYPES[protocol_type]
        protocol_impl(Runtime.engines, _globals, *args, **kwargs)

    @classmethod
    def agent(cls, a):
        cls.currentAgent = a
        if not(cls.currentAgent in cls.engines):
            cls.engines[cls.currentAgent] = Engine(cls.currentAgent)

    @classmethod
    def add_plan(cls, p):
        cls.engines[cls.currentAgent].add_plan(p)

    @classmethod
    def add_goal(cls, p):
        cls.engines[cls.currentAgent].add_goal(p)

    @classmethod
    def run_agent(cls, a):
        e = cls.engines[a]
        t = threading.Thread(target = e.run)
        t.start()

    @classmethod
    def run_agents(cls):
        for ag in cls.engines:
            e = cls.engines[ag]
            t = threading.Thread(target = e.run)
            t.start()

    @classmethod
    def stop_agent(cls, a):
        e = cls.engines[a]
        e.stop()

    @classmethod
    def get_engine(cls, a):
        return cls.engines[a]

    @classmethod
    def agents(cls):
        return cls.engines.keys()

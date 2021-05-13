#
# Lib.py
#

#from __future__ import print_function

import sys
import threading
import time

from phidias.Types  import *
from phidias.Runtime  import *

__all__ = [ 'show', 'show_line', 'show_fmt',
            'eq', 'neq', 'gt', 'geq', 'lt', 'leq',
            'timeout', 'Timer', 'wait' ]

# ------------------------------------------------
# ACTIONS
# ------------------------------------------------

class show(Action):
    def execute(self, *args):
        for a in args:
            print(a(), end='')

class show_line(show):
    def execute(self, *args):
        show.execute(self, *args)
        print("")

class show_fmt(Action):
    def execute(self, *args):
        t_a = tuple(map(lambda x:x(), args[1:]))
        print(args[0]() % t_a, end='')

# ------------------------------------------------
# PREDICATES
# ------------------------------------------------

class eq(ActiveBelief):
    def evaluate(self, x, y):
        return x() == y()

class neq(ActiveBelief):
    def evaluate(self, x, y):
        return x() != y()

class gt(ActiveBelief):
    def evaluate(self, x, y):
        return x() > y()

class geq(ActiveBelief):
    def evaluate(self, x, y):
        return x() >= y()

class lt(ActiveBelief):
    def evaluate(self, x, y):
        return x() < y()

class leq(ActiveBelief):
    def evaluate(self, x, y):
        return x() <= y()

# ------------------------------------------------
# TIMERS
# ------------------------------------------------

# ------------------------------------------------
class timeout(Reactor):
    pass

# ------------------------------------------------
class wait(Action):
    def execute(self, T):
        time.sleep(T() / 1000.0)

# ------------------------------------------------
if sys.implementation.name != "micropython":
    class Timer(Sensor):

        def on_start(self, uTimeout):
            evt = threading.Event()
            self.event = evt
            self.timeout = uTimeout()
            self.do_restart = False

        def on_restart(self):
            self.do_restart = True
            self.event.set()

        def on_stop(self):
            self.do_restart = False
            self.event.set()

        def sense(self):
            while True:
                self.event.wait(self.timeout / 1000.0)
                self.event.clear()
                if self.do_restart:
                    self.do_restart = False
                    continue
                if self.stopped():
                    return
                else:
                    self.assert_belief(timeout(self.__class__.__name__))
                    return

else:
    class Timer(Sensor):

        def on_start(self, uTimeout):
            self.timeout = uTimeout()
            self.do_restart = False

        def on_restart(self):
            self.do_restart = True

        def on_stop(self):
            self.do_restart = False

        def sense(self):
            while True:
                time.sleep(self.timeout / 1000.0)
                if self.do_restart:
                    self.do_restart = False
                    continue
                if self.stopped():
                    return
                else:
                    self.assert_belief(timeout(self.__class__.__name__))
                    return


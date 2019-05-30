#
# Lib.py
#

from __future__ import print_function

import threading
import sys
import time

from phidias.Types  import *
from phidias.Runtime  import *

__all__ = [ 'show', 'show_line',
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
class Timer(Sensor):

    def on_start(self, uTimeout):
        evt = threading.Event()
        self.event = evt
        self.timeout = uTimeout()
        self.do_restart = False

    def on_restart(self, uTimeout):
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
            if self.stopped:
                return
            else:
                self.assert_belief(timeout(self.__class__.__name__))
                return



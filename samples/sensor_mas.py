import sys

import time

import threading
import random

sys.path.insert(0, "../lib")

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *
from phidias.Agent import *

class number(Belief): pass

class solve(Reactor): pass

class sieve(Procedure): pass
class show_all(Procedure): pass
class generate(Procedure): pass

class go(Procedure): pass
class work(Procedure): pass
class TIMEOUT(Reactor): pass
class TASK(Reactor): pass
class DUTY(Belief): pass


class TaskDetect(Sensor):

    def on_start(self):
        # Starting task detection
       self.running = True


    def on_stop(self):
        #Stopping task detection
        self.running = False

    def sense(self):
        while self.running:
           time.sleep(1)
           task = "id_"+str(random.randint(1, 1000))
           self.assert_belief(TASK(task))




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
            self.event.wait(self.timeout)
            self.event.clear()
            if self.do_restart:
                self.do_restart = False
                continue
            if self.stopped:
                return
            else:
                self.assert_belief(TIMEOUT("ON"))
                return




# ---------------------------------------------------------------------
# Variable declaration
# ---------------------------------------------------------------------
def_vars("X","Y")


# ---------------------------------------------------------------------
# Agent 'worker'
# ---------------------------------------------------------------------
class worker(Agent):
    def main(self):
        +TASK(X)[{'from': Y}] >> [show_line("Received task ", X, " from ", Y)]


# ---------------------------------------------------------------------
# Agent 'main'
# ---------------------------------------------------------------------
class main(Agent):
    def main(self):

        go() >> [show_line("Starting task detection...\n"), TaskDetect().start]
        work() >> [show_line("Worker on duty..."), +DUTY("YES"), Timer(10).start]
        +TASK(X) / DUTY(Y) >> [+TASK(X)[{'to':'worker'}]]
        +TIMEOUT("ON") >> [show_line("\nWorker is tired...\n"), -DUTY("YES")]



# start the actors
worker().start()
main().start()
# run the engine shell
PHIDIAS.shell(globals())

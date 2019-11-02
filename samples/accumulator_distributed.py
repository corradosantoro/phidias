import sys

from phidias.Types import *
from phidias.Main import *
from phidias.Lib import *
from phidias.Agent import *

class total(SingletonBelief): pass

class request(Reactor): pass
class reply(Reactor): pass

class inc(Procedure): pass
class send_reply(Procedure): pass


# ---------------------------------------------------------------------
# Variable declaration
# ---------------------------------------------------------------------
def_vars("A", "X", "T")


# ---------------------------------------------------------------------
# Agent 'accumulator'
# ---------------------------------------------------------------------
class accumulator(Agent):
    def init(self):
        self.assert_belief(total(0))

    def main(self):
        +request(X)[{'from': A}] / total(T) >> [ show_line("Increment by ", X, " request from ", A), "X = X + T", +total(X), send_reply(A) ]
        send_reply(A) / total(T) >> [ +reply(T)[{'to': A}] ]


# ---------------------------------------------------------------------
# Agent 'main'
# ---------------------------------------------------------------------
class main(Agent):
    def main(self):
        inc() >> [ inc(1) ]
        inc(X) >> [ show_line("Sending increment by ", X, " request..."), +request(X)[{'to': 'accumulator@127.0.0.1'}] ]
        +reply(T)[{'from': A}] >> [ show_line("New total is ", T) ]


if sys.argv[1] == "--accumulator":
    accumulator().start()
    PHIDIAS.run_net(globals())
elif sys.argv[1] == "--main":
    main().start()
    PHIDIAS.run_net(globals(), 6767)
else:
    exit("Invalid command-line")

# run the engine shell
PHIDIAS.shell(globals())

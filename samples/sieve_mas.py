import sys

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


# ---------------------------------------------------------------------
# Variable declaration
# ---------------------------------------------------------------------
def_vars("X","Y")


# ---------------------------------------------------------------------
# Agent 'solver'
# ---------------------------------------------------------------------
class solver(Agent):
    def main(self):
        +solve()[{'from': X}] >> [ show_line("Request to solve from agent ", X), sieve() ]
        sieve() / (number(X) & number(Y) & neq(X, Y) & (lambda: (X % Y) == 0) ) >> [ -number(X), sieve() ]
        sieve() >> [ show_line("done") , show_all() ]

        show_all() / number(X) >> [ show_all(X) ]
        show_all()  >> [ show_line() ]

        show_all(X) / (number(Y) & lt(Y, X)) >> [ show_line(Y), show_all(Y) ]
        show_all(X) / number(X) >> [ show(X,"\t"), -number(X), show_all() ]


# ---------------------------------------------------------------------
# Agent 'main'
# ---------------------------------------------------------------------
class main(Agent):
    def main(self):
        sieve() >> [ sieve(2) ]
        sieve(X) / gt(X, 100) >> [ show_line("Generation completed, solving..."), +solve()[{'to':'solver'}] ]
        sieve(X) >> [ +number(X)[{'to':'solver'}], "X = X + 1", sieve(X) ]


# start the actors
solver().start()
main().start()
# run the engine shell
PHIDIAS.shell(globals())



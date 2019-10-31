#
#
#

import sys

#sys.path.insert(0, "../lib")

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *
from phidias.Agent import *


class fact(Procedure): pass
class solve(Reactor): pass
class result(Reactor): pass

def_vars("Acc", "N", "Source", "X")

class FactComputer(Agent):
    def main(self):
        +solve(N)[{'from': Source}] >> \
          [
              show_line("Request to computer the factorial of ", N, " from agent ", Source),
              fact(N, Source)
          ]
        fact(N, Source) >> [ fact(N, 1, Source) ]
        fact(1, Acc, Source) >> [ +result(Acc)[{'to':Source}]  ]
        fact(N, Acc, Source) >> \
            [
                "Acc = N * Acc",
                "N = N - 1",
                fact(N, Acc, Source)
            ]


# ---------------------------------------------------------------------
# Agent 'main'
# ---------------------------------------------------------------------
class main(Agent):
    def main(self):
        fact(N) >> [ +solve(N)[{'to':'FactComputer'}] ]
        +result(X)[{'from':Source}] >> [ show_line('Factorial is ', X) ]

# start the actors
FactComputer().start()
main().start()
PHIDIAS.shell(globals())


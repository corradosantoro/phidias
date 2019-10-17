#
#
#

import sys

sys.path.insert(0, "../lib")

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *


class fact(Procedure): pass

def_vars("Acc", "N", "X")
fact(N) >> \
  [
      X <= fact(N, 1),   # assign to "X" the return value of fact(N,1)
      show_line("the resulting factorial is = ", X)
  ]
fact(1, Acc) >> [ Acc ] # Acc is the return value of the procedure
fact(N, Acc) >> \
    [
        "Acc = N * Acc",
        "N = N - 1",
        fact(N, Acc)
    ]

PHIDIAS.run()
PHIDIAS.shell(globals())


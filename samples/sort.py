#
#
#

import sys
import random

sys.path.insert(0, "../lib")

from phidias.Types import *
from phidias.Main import *
from phidias.Lib import *

class item(Belief): pass
class generate(Procedure): pass
class sort(Procedure): pass
class dump(Procedure): pass


class RandomUniform(Action):
    def execute(self, size, x):
        x(random.uniform(0, size()))


def_vars('N', 'V', 'N1', 'N2', 'V1', 'V2', 'Sorted')

generate() >> [ generate(20) ]

generate(0) >> [ ]
generate(N) >> [ "V=0", RandomUniform(100, V), +item(N, V), "N=N-1", generate(N) ]


sort() >> [ sort(1,2,True) ]
sort(N1,N2,Sorted) / (item(N1, V1) & item(N2, V2) & gt(V1,V2)) >> \
  [
      -item(N1, V1), -item(N2, V2),
      +item(N1, V2), +item(N2, V1),
      "N1 = N1+1", "N2=N2+1",
      sort(N1,N2,False)
  ]
sort(N1,N2,Sorted) / (item(N1, V1) & item(N2, V2)) >> \
  [
      "N1 = N1+1", "N2=N2+1",
      sort(N1,N2,Sorted)
  ]
sort(N1,N2,False)  >> [ sort(1,2,True) ]
sort(N1,N2,True)  >> [ show_line("Completed") ]

dump() >> [ dump(1) ]
dump(N) / item(N, V) >> [ show_line(N, " --> ", V), "N = N + 1", dump(N) ]

PHIDIAS.run()
PHIDIAS.shell(globals())

#
# Minimum Cost Path Example
#
# invoke "path('A','G')" to see a run of this code
#

from phidias.Types import *
from phidias.Lib import *
from phidias.Main import *

class link(Belief): pass
class path(Procedure): pass
class select_min(Procedure): pass
class show_min(Procedure): pass
class selected(SingletonBelief): pass

#
def_vars('Src', 'Dest', 'Next', 'Cost', 'P', 'Total', 'CurrentMin', 'CurrentMinCost')

path(Src, Dest) >> \
  [
      path([], 0, Src, Dest),
      show_min()
  ]

path(P, Total, Dest, Dest) >> \
  [ 
      "P.append(Dest)", 
      show_line(P, " ", Total),
      +selected(P, Total)
  ]
path(P, Total, Src,  Dest)['all'] / link(Src,Next,Cost) >> \
  [
      "P = P.copy()",
      "P.append(Src)",
      "Total = Total + Cost",
      select_min(P, Total, Next, Dest)
  ]

select_min(P, Total, Next, Dest) / (selected(CurrentMin, CurrentMinCost) & gt(Total, CurrentMinCost)) >> \
  [
      show_line(P, " ", Next, ", cost ", Total, " [CUT]")
  ]
select_min(P, Total, Next, Dest) >> \
  [
      path(P, Total, Next, Dest)
  ]

show_min() / selected(CurrentMin, CurrentMinCost)  >> \
  [
      show_line("Minimum Cost Path ", CurrentMin, ", cost ", CurrentMinCost)
  ]

PHIDIAS.assert_belief(link('A', 'B', 2))
PHIDIAS.assert_belief(link('A', 'C', 3))
PHIDIAS.assert_belief(link('A', 'D', 1))

PHIDIAS.assert_belief(link('B', 'C', 2))
PHIDIAS.assert_belief(link('B', 'F', 1))

PHIDIAS.assert_belief(link('C', 'F', 1))
PHIDIAS.assert_belief(link('C', 'G', 2))
PHIDIAS.assert_belief(link('C', 'E', 3))

PHIDIAS.assert_belief(link('D', 'C', 2))
PHIDIAS.assert_belief(link('D', 'E', 3))

PHIDIAS.assert_belief(link('E', 'G', 3))

PHIDIAS.assert_belief(link('F', 'G', 2))

PHIDIAS.run()
PHIDIAS.shell(globals())


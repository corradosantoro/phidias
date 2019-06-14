#
#
#

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

class free(Belief): pass

class allocate(Procedure): pass

def_vars('N','Index', 'Side')

allocate(N) >> [ allocate(N, 2, 'A') ]

allocate(0, Index, Side)  >> [ show_line('End of allocation' )]
#
allocate(N, Index, 'A') / free(Index, 'A') >> \
  [
      show_line('Seat ', Index, 'A'),
      -free(Index, 'A'),
      'N = N - 1',
      allocate(N, Index, 'B')
  ]
allocate(N, Index, 'A') >> \
  [
      allocate(N, Index, 'B')
  ]
#
allocate(N, Index, 'B') / free(Index, 'B') >> \
  [
      show_line('Seat ', Index, 'B'),
      -free(Index, 'B'),
      'N = N - 1',
      'Index = Index + 1',
      allocate(N, Index, 'A')
  ]
allocate(N, Index, 'B') >> \
  [
      'Index = Index + 1',
      allocate(N, Index, 'A')
  ]

# populate the KB
for i in range(2,35):
    PHIDIAS.assert_belief(free(i, 'A'))
    PHIDIAS.assert_belief(free(i, 'B'))


# instantiate the engine
PHIDIAS.run()
# run the engine shell
PHIDIAS.shell(globals())

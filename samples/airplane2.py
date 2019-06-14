#
#
#

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

class free(Belief): pass
class seat_map(Belief): pass

class allocate(Procedure): pass
class show_map(Procedure): pass

def_vars('N','Index', 'Side', 'Seat')

allocate(N) >> [ allocate(N, 1, 'A') ]

allocate(0, Index, Side)  >> [ show_line('End of allocation' )]
#
allocate(N, Index, 'A') / (seat_map(Index, Seat) & free(Seat, 'A'))  >> \
  [
      show_line('Seat ', Seat, 'A'),
      -free(Seat, 'A'),
      'N = N - 1',
      allocate(N, Index, 'B')
  ]
allocate(N, Index, 'A') >> \
  [
      allocate(N, Index, 'B')
  ]
#
allocate(N, Index, 'B') / (seat_map(Index, Seat) & free(Seat, 'B')) >> \
  [
      show_line('Seat ', Seat, 'B'),
      -free(Seat, 'B'),
      'N = N - 1',
      'Index = Index + 1',
      allocate(N, Index, 'A')
  ]
allocate(N, Index, 'B') >> \
  [
      'Index = Index + 1',
      allocate(N, Index, 'A')
  ]

show_map() >> [ show_map(1) ]
show_map(Index) / seat_map(Index, Seat) >> \
  [ show_line(Seat), "Index = Index + 1", show_map(Index) ]

# populate the KB
for i in range(2,35):
    PHIDIAS.assert_belief(free(i, 'A'))
    PHIDIAS.assert_belief(free(i, 'B'))

i = 1
for seat in range(17, 35):
    PHIDIAS.assert_belief(seat_map(i, seat))
    i += 2

i = 2
for seat in range(16, 1, -1):
    PHIDIAS.assert_belief(seat_map(i, seat))
    i += 2


# instantiate the engine
PHIDIAS.run()
# run the engine shell
PHIDIAS.shell(globals())

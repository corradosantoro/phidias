#
#
#

from phidias.Types import *
from phidias.Lib import *
from phidias.Main import *

class obj(Belief): pass
class upon(Belief): pass
class owned(Belief): pass

class pick(Procedure): pass
class put(Procedure): pass
class find_bottom(Procedure): pass
class find_tower(Procedure): pass
class go_up(Procedure): pass

def_vars('X', 'Y', 'Z', 'N')

pick(X) / (obj(X) & upon(Y, X)) >> [ show_line("Cannot pick ", X, " since it is under the ", Y) ]
pick(X) / (obj(X) & upon(X, Y)) >> \
         [
           show_line(X, " has been picked"),
           -obj(X), -upon(X, Y), +owned(X)
         ]
pick(X) / obj(X) >>  [
                        show_line(X, " picked"),
                        -obj(X), +owned(X)
                     ]
pick(X) / owned(X) >> [ show_line("you've still got ", X) ]
pick(X) >> [ show_line("cannot pick ", X, " since it is not present") ]

put(X) / owned(X) >> \
       [ show_line(X, " is now on the table"),
         -owned(X), +obj(X) ]
put(X) / obj(X) >> [ show_line(X, " is already on the table") ]
put(X) >> [ show_line(X, " does not exist") ]

put(X, Y) / (owned(X) & obj(Y) & upon(Z, Y) ) \
    >> [ show_line(Y, " has ", Z, " on its top") ]
put(X, Y) / (owned(X) & obj(Y)) >> \
    [ -owned(X), +obj(X), +upon(X, Y), show_line("done") ]
put(X, Y) >> [ show_line(X, " is not owned or does not exist") ]

find_tower(X) >> [ find_bottom(X) ]

find_bottom(X) / upon(X,Y) >> [ find_bottom(Y) ]
find_bottom(X) >> [ go_up(X, 1) ]

go_up(X, N) / upon(Y, X) >> [
	show_line("Level ", N, ":", X), "N = N + 1", go_up(Y, N) ]
go_up(X, N) >> [ show_line("Level ", N, ":", X) ]

class ontable(Procedure): pass
class onrobot(Procedure): pass

ontable()['all'] / obj(X) >> [ show_line(X) ]
onrobot()['all'] / owned(X) >> [ show_line(X) ]


class free_and_pick(Procedure): pass
class free(Procedure): pass

free_and_pick(X) / obj(X) >> [ free(X), pick(X) ]

free(X) / (obj(X) & upon(Y, X)) >> [ free(Y), show_line('unstacking ', X), -upon(Y,X) ]
free(X) / (obj(X) & upon(X, Y)) >> [ show_line('unstacking ', X), -upon(X,Y) ]


# initial KB
PHIDIAS.assert_belief(obj('cube'))
PHIDIAS.assert_belief(obj('prism'))
PHIDIAS.assert_belief(obj('cylinder'))

PHIDIAS.run()
PHIDIAS.shell(globals())

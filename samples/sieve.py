import sys

#sys.path.insert(0, "../lib")

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

class number(Belief): pass

class sieve(Procedure): pass
class show_all(Procedure): pass

def_vars("X","Y")
sieve() / (number(X) & number(Y) & neq(X, Y) & (lambda: (X % Y) == 0) ) >> [ -number(X), sieve() ]
sieve() >> [ show_line("done"), show_all() ]

show_all() / number(X) >> [ show_all(X) ]
show_all()  >> [ show_line() ]
show_all(X) / (number(Y) & lt(Y, X)) >> [ show_line(Y), show_all(Y) ]
show_all(X) / number(X) >> [ show(X,"\t"), -number(X), show_all() ]

# populate the KB
for i in range(2,100):
    PHIDIAS.assert_belief(number(i))

# instantiate the engine
PHIDIAS.run()
# run the engine shell
PHIDIAS.shell(globals())

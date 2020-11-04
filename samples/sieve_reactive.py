
import sys
sys.path.insert(0, "../lib")

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

class number(Belief): pass

def_vars("X","Y")
+number(X) / (number(Y) & neq(X, Y) & (lambda: (X % Y) == 0) ) >> [ -number(X) ]

# instantiate the engine
PHIDIAS.run()

# populate the KB (and run the rules)
for i in range(2,100):
    PHIDIAS.assert_belief(number(i))

# run the engine shell
PHIDIAS.shell(globals())


#
#
#

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

import random

class block(Belief): pass

class pick(Procedure): pass

def_vars('X','Min')

pick() / block(X) >> [ pick(X) ]
pick() >> [ show_line("End!") ]

pick(Min) / (block(X) & lt(X,Min)) >> [ pick(X) ]
pick(Min) >> [ show_line("Picking ", Min), -block(Min), pick() ]

# populate the KB
for i in range(1,50):
    PHIDIAS.assert_belief(block(random.uniform(0,50)))

# instantiate the engine
PHIDIAS.run()
# run the engine shell
PHIDIAS.shell(globals())


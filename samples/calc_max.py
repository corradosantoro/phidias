#
#
#

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

import random

class number(Belief): pass

class compute_max(Procedure): pass

def_vars('X','TempMax')

compute_max() / number(X) >> [ compute_max(X) ]
compute_max(TempMax) / (number(X) & gt(X,TempMax)) >> [ compute_max(X) ]
compute_max(TempMax) >> [ show_line("The maximum is ", TempMax) ]

# populate the KB
for i in range(1,50):
    PHIDIAS.assert_belief(number(random.uniform(0,50)))

# instantiate the engine
PHIDIAS.run()
# run the engine shell
PHIDIAS.shell(globals())

#
#
#

import sys

#sys.path.insert(0, "../lib")

from phidias.Types import *
from phidias.Lib import *
from phidias.Main import *

class student(Belief): pass

class graduated(Belief): pass

def_vars("X")
+graduated(X) / student(X) >> [ show_line(X, " is now graduated! Yeah!!!"), -student(X) ]
+graduated(X) >> [ show_line(X, " is not a student"), -graduated(X) ]
+student(X) / graduated(X) >> [ show_line(X, " is graduated and cannot be a student again"), -student(X) ]

PHIDIAS.run()
PHIDIAS.shell(globals())

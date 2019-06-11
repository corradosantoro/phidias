

# import libraries
from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

class fifty(SingletonBelief): pass
class twenty(SingletonBelief): pass
class ten(SingletonBelief): pass
class five(SingletonBelief): pass

class change(Procedure): pass


def_vars("M", "C")

change(M) / (fifty(C) & geq(M, 50) & gt(C, 0) ) >> \
    [
        show_line("50 cent"),
        "C = C - 1", +fifty(C),
        "M = M - 50", change(M)
    ]

change(M) / (twenty(C) & geq(M, 20) & gt(C, 0) ) >> \
    [
        show_line("20 cent"),
        "C = C - 1", +twenty(C),
        "M = M - 20", change(M)
    ]

change(M) / (ten(C) & geq(M, 10) & gt(C, 0) ) >> \
    [
        show_line("10 cent"),
        "C = C - 1", +ten(C),
        "M = M - 10", change(M)
    ]

change(M) / (five(C) & geq(M, 5) & gt(C, 0) ) >> \
    [
        show_line("5 cent"),
        "C = C - 1", +five(C),
        "M = M - 5", change(M)
    ]

change(M) >> \
    [
        show_line("End of change, remaning ", M, " cents")
    ]


PHIDIAS.assert_belief(fifty(10))
PHIDIAS.assert_belief(twenty(10))
PHIDIAS.assert_belief(ten(10))
PHIDIAS.assert_belief(five(10))

# start PHIDIAS
PHIDIAS.run()

# run the engine shell
PHIDIAS.shell(globals())

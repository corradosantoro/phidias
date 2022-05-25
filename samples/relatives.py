#
#
#

import sys
#sys.path.insert(0, "../lib")

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

class parent(Belief): pass
class male(Belief): pass
class female(Belief): pass

class sibling(Goal): pass
class father(Goal): pass
class mother(Goal): pass
class check_parent(Goal): pass
class sister(Goal): pass
class brother(Goal): pass
class grandpa(Goal): pass
class grandma(Goal): pass

class find(Procedure): pass
class father_of(Procedure): pass
class fathers(Procedure): pass
class parent_line(Procedure): pass

def_vars('X','Y','P')

sibling(X,Y) << ( parent(P,X) & parent(P,Y) & neq(X,Y) )
father(X,Y) << ( parent(X,Y) & male(X) )
mother(X,Y) << ( parent(X,Y) & female(X) )

check_parent(X) << ( parent(Y,X) )

sister(X,Y) << (sibling(X,Y) & female(X))
brother(X,Y) << (sibling(X,Y) & male(X))


PHIDIAS.assert_belief(male('james1')),
PHIDIAS.assert_belief(male('charles1'))
PHIDIAS.assert_belief(male('charles2'))
PHIDIAS.assert_belief(male('james2'))
PHIDIAS.assert_belief(male('george1'))

PHIDIAS.assert_belief(female('catherine'))
PHIDIAS.assert_belief(female('elizabeth'))
PHIDIAS.assert_belief(female('sophia'))

PHIDIAS.assert_belief(parent('james1', 'charles1'))
PHIDIAS.assert_belief(parent('james1', 'elizabeth'))
PHIDIAS.assert_belief(parent('charles1', 'charles2'))
PHIDIAS.assert_belief(parent('charles1', 'catherine'))
PHIDIAS.assert_belief(parent('charles1', 'james2'))
PHIDIAS.assert_belief(parent('elizabeth', 'sophia'))
PHIDIAS.assert_belief(parent('sophia', 'george1'))

PHIDIAS.run()
PHIDIAS.shell(globals())


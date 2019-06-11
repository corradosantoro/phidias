#
#
#

from phidias.Types  import *
from phidias.Main import *
from phidias.Lib import *

import random

class block(Belief): pass

class pick(Procedure): pass

class Distance(ActiveBelief):
  def evaluate(self, Item, Origin, CurrentMin):
    return abs(Item() - Origin()) < CurrentMin()

def_vars('X', 'robot_pos', 'Y', 'temp_min_distance', 'temp_min')

pick(robot_pos) / block(X) >> 			\
	[ 
		"temp_min_distance = abs(X - robot_pos)",
		pick(X, temp_min_distance, robot_pos)
	]
pick(robot_pos) >> [ show_line("End!") ]

# Distance = abs(Y - robot_pos) < temp_min_distance
pick(temp_min, temp_min_distance, robot_pos) /                   \
    (block(Y) & Distance(Y, robot_pos, temp_min_distance)) >>    \
	[ 
		"temp_min_distance = abs(temp_min - robot_pos)", 
		pick(Y, temp_min_distance, robot_pos)
	]
pick(temp_min, temp_min_distance, robot_pos) >> 	\
	[ 
		show_line("Picking ", temp_min), 
		-block(temp_min), pick(temp_min)
	]

# populate the KB
for i in range(1,20):
    PHIDIAS.assert_belief(block(random.uniform(0, 50)))

# instantiate the engine
PHIDIAS.run()
# run the engine shell
PHIDIAS.shell(globals())


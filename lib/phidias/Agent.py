#
# Agent.py
#

from phidias.Types import *
from phidias.Main import *
from phidias.Exceptions import *

# -------------------------------------------------
class Agent:

    def __init__(self, name = None):
        if name is None:
            self.__name = self.__class__.__name__
        else:
            self.__name = name

    def name(self):
        return self.__name

    def assert_belief(self, b):
        PHIDIAS.assert_belief(b, self.__name)

    def retract_belief(self, b):
        PHIDIAS.retract_belief(b, self.__name)

    def start(self):
        def_actor(self.__name)
        self.init()
        self.main()
        PHIDIAS.run_agent(self.__name)

    def init(self):
        pass

    def main(self):
        raise MethodNotOverriddenException()


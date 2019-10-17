#
# Knowledge.py
#


#from __future__ import print_function

import sys


class Knowledge(object):

    def __init__(self):
        self.__kb = {}

    def add_belief(self, bel):
        n = bel.name()
        if n in self.__kb:
            if not(bel in self.__kb[n]):
                from phidias.Types import SingletonBelief
                if isinstance(bel, SingletonBelief):
                    self.__kb[n] = [ bel ]
                else:
                    self.__kb[n].append(bel)
                return True
            else:
                return False
        else:
            self.__kb[n] = [ bel ]
            return True

    def remove_belief(self, bel):
        n = bel.name()
        if n in self.__kb:
            if bel in self.__kb[n]:
                self.__kb[n].remove(bel)
                return True
            else:
                return False
        else:
            return False

    def base(self):
        return self.__kb


    def show(self):
        c = 0
        for k in self.__kb.keys():
            for b in self.__kb[k]:
                print("%-40s" % (str(b)), end='')
                if c == 1:
                    print("")
                    c = 0
                else:
                    c += 1
        print("")


    def get_matching_beliefs(self, uTemplate):
        n = uTemplate.name()
        ret = []
        if not(n in self.__kb):
            return ret
        for b in self.__kb[n]:
            if uTemplate.match_constants(b):
                ret.append(b)
        return ret


from distalgs import *
from networks import *
from algs import *
from tester import *


def LCR_UNIDIR_RING():
    r = Unidirectional_Ring(3)
    LCR(r)

def ASYNC_LCR_UNIDIR_RING():
    r = Unidirectional_Ring(6)
    AsyncLCR(r)

def COMPLETE_GRAPH():
    x = Complete_Graph(4)
    print x
    for p in x:
        print [str(n) for n in p.in_nbrs]


test(LCR_UNIDIR_RING, precision = 1e-7)
test(ASYNC_LCR_UNIDIR_RING, precision = 1e-3)
test(COMPLETE_GRAPH)
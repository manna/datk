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

def LCR_COMPLETE():
    x = Complete_Graph(7)
    LCR(x)

def ASYNC_LCR_COMPLETE():
    x = Complete_Graph(7)
    AsyncLCR(x)

test(ASYNC_LCR_COMPLETE)
test(LCR_UNIDIR_RING, precision = 1e-7)
test(ASYNC_LCR_UNIDIR_RING, precision = 1e-3)
test(LCR_COMPLETE)

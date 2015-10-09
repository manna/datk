from distalgs import *
from networks import *
from algs import *
from tester import *

@test(precision = 1e-7)
def LCR_UNIDIR_RING():
    r = Unidirectional_Ring(3)
    LCR(r)

@test(precision = 1e-3)
def ASYNC_LCR_UNIDIR_RING():
    r = Unidirectional_Ring(6)
    AsyncLCR(r)

@test
def LCR_COMPLETE():
    x = Complete_Graph(7)
    LCR(x)

@test
def ASYNC_LCR_COMPLETE():
    x = Complete_Graph(7)
    AsyncLCR(x)

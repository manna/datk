from distalgs import *
from networks import *
from algs import *
from tester import *

@test(precision = 1e-7)
def LCR_UNIDIR_RING():
    r = Unidirectional_Ring(3)
    LCR(r)

# @test(precision = 1e-3)
def ASYNC_LCR_UNIDIR_RING():
    r = Unidirectional_Ring(6)
    AsyncLCR(r)

# @test
def LCR_COMPLETE():
    x = Complete_Graph(7)
    LCR(x)

# @test
def ASYNC_LCR_COMPLETE():
    x = Complete_Graph(10)
    AsyncLCR(x)


#LCR failed at :
#[P6 -> {P3, P1, P5, P4, P2, P0}, P3 -> {P6, P1, P5, P4, P2, P0}, P1 -> {P6, P3, P5, P4, P2, P0}, P5 -> {P6, P3, P1, P4, P2, P0}, P4 -> {P6, P3, P1, P5, P2, P0}, P2 -> {P6, P3, P1, P5, P4, P0}, P0 -> {P6, P3, P1, P5, P4, P2}]

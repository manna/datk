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
def send_receive_msgs():
    x = Bidirectional_Ring(4, lambda p:p)
    assert x[0].get_msgs() == []
    x[0].send_to_all_neighbors("hi")
    x[0].send_to_all_neighbors("hey")
    x[2].send_to_all_neighbors("yo")
    assert x[1].get_msgs(x[0]) == ["hi", "hey"]
    assert x[1].get_msgs(x[0]) == []
    assert x[1].get_msgs() == ["yo"]
    assert x[1].get_msgs() == []
from distalgs import *
from networks import *
from algs import *
from tester import *

@test(precision = 1e-7)
def LCR_UNI_RING():
    r = Unidirectional_Ring(6)
    lcr = LCR()
    lcr(r, draw=False, silent=True)
    print "Message Complexity: " + str(lcr.message_count)
    testLeaderElection(r)

@test(precision = 1e-7)
def LCR_BI_RING():
    r = Bidirectional_Ring(6)
    LCR(r, silent=True)
    testLeaderElection(r)

@test(precision = 1e-3)
def ASYNC_LCR_UNI_RING():
    r = Unidirectional_Ring(6)
    AsyncLCR(r, silent=True)
    testLeaderElection(r)

@test(precision = 1e-3)
def ASYNC_LCR_BI_RING():
    r = Bidirectional_Ring(6)
    AsyncLCR(r, silent = True)
    testLeaderElection(r)

@test(precision=1e-7)
def FLOODMAX_UNI_RING():
    r = Unidirectional_Ring(4)
    FloodMax(r, silent=True)
    testLeaderElection(r)

@test(precision=1e-7)
def FLOODMAX_BI_RING():
    r = Bidirectional_Ring(4)
    FloodMax(r, silent=True)
    testLeaderElection(r)

@test(precision=1e-7)
def FLOODMAX_BI_LINE():
    l = Bidirectional_Line(4)
    FloodMax(l, silent=True)
    testLeaderElection(l)

@test(precision=1e-7)
def FLOODMAX_COMPLETE_GRAPH():
    g = Complete_Graph(10)
    FloodMax(g, silent=True)
    testLeaderElection(g)

@test
def send_receive_msgs():
    x = Bidirectional_Ring(4, lambda p:p)
    assert x[0].get_msgs() == []
    x[0].send_to_all_neighbors(LCR(),"hi")
    x[0].send_to_all_neighbors(LCR(),"hey")
    x[2].send_to_all_neighbors(LCR(),"yo")
    assert x[1].get_msgs(x[0]) == ["hi", "hey"]
    assert x[1].get_msgs(x[0]) == []
    assert x[1].get_msgs() == ["yo"]
    assert x[1].get_msgs() == []

@test(main_thread=True)
def DRAW_UNI_RING():
    Unidirectional_Ring(4).draw()

@test(main_thread=True)
def DRAW_COMPLETE_GRAPH():
    Complete_Graph(10).draw()

@test(main_thread=True)
def DRAW_UNI_LINE():
    Unidirectional_Line(4).draw()
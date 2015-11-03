from distalgs import *
from networks import *
from algs import *
from tester import *

def configure_ipython():
  """
  Convenient helper function to determine if environment is ipython.
  Note that drawing is only safe in ipython qtconsole with matplotlib inline
  If environment is IPython, returns True and configures IPython.
  Else returns False.
  """
  try:
    __IPYTHON__
    ip = get_ipython()
    ip.magic("%matplotlib inline") 
  except NameError:
    return False
  else:
    return True

in_ipython = configure_ipython()

test_params = {"draw":in_ipython, "silent" : True}


@test(precision = 1e-7)
def LCR_UNI_RING():
    r = Unidirectional_Ring(6)
    LCR(r, test_params)
    testLeaderElection(r)

@test(precision = 1e-7)
def LCR_BI_RING():
    r = Bidirectional_Ring(6)
    LCR(r, params = test_params)
    testLeaderElection(r)

@test(precision = 1e-3)
def ASYNC_LCR_UNI_RING():
    r = Unidirectional_Ring(6)
    AsyncLCR(r, params = test_params)
    testLeaderElection(r)

@test(precision = 1e-3)
def ASYNC_LCR_BI_RING():
    r = Bidirectional_Ring(6)
    AsyncLCR(r, params = test_params)
    testLeaderElection(r)

@test(precision=1e-7)
def FLOODMAX_UNI_RING():
    r = Unidirectional_Ring(4)
    FloodMax(r, params = test_params)
    testLeaderElection(r)

@test(precision=1e-7)
def FLOODMAX_BI_RING():
    r = Bidirectional_Ring(4)
    FloodMax(r, params = test_params)
    testLeaderElection(r)

@test(precision=1e-7)
def FLOODMAX_BI_LINE():
    l = Bidirectional_Line(4)
    FloodMax(l, params = test_params)
    testLeaderElection(l)

@test(precision=1e-7)
def FLOODMAX_COMPLETE_GRAPH():
    g = Complete_Graph(10)
    FloodMax(g, params = test_params)
    testLeaderElection(g)

@test(precision=1e-7)
def FLOODMAX_RANDOM_GRAPH():
    g = Random_Network(16)
    FloodMax(g, params = test_params)
    testLeaderElection(g)

@test(precision=1e-7)
def SYNCH_BFS():
    x = Random_Network(10)
    FloodMax(x, test_params)
    testLeaderElection(x)

    SynchBFS(x, test_params)
    testBFS(x)

@test(precision = 1e-7)
def SYNCH_BFS_ACK():
    x = Bidirectional_Line(6, lambda t:t)

    FloodMax(x, test_params)
    testLeaderElection(x)

    SynchBFSAck(x, test_params)
    testBFSWithChildren(x)

@test(precision=1e-7)
def SYNCH_CONVERGE_HEIGHT():
    x = Random_Network(10)

    FloodMax(x, test_params)
    testLeaderElection(x)

    SynchBFS(x, test_params)
    testBFS(x)

    SynchConvergeHeight(x, test_params)

@test(precision=1e-7)
def SYNCH_BROADCAST_HEIGHT():
    x = Random_Network(10)

    FloodMax(x, test_params)
    testLeaderElection(x)

    SynchBFSAck(x, test_params)
    testBFSWithChildren(x)

    SynchConvergeHeight(x, test_params)

    SynchBroadcast(x, {"attr":"height", "draw":in_ipython, "silent" : True})
    testBroadcast(x, 'height')

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

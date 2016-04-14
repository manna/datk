"""
Algorithm Test Suite

Tests algorithms defined in algs.py
"""

try:
    from datk.core.distalgs import *
    from datk.core.networks import *
    from datk.core.algs import *
    from datk.core.tester import *
except ImportError:
    raise ImportError(
""" Imports failed\n
To run tests, execute the following commands:
$ cd ../..
$ python -m datk.tests.tests """)
from helpers import *

def configure_ipython():
  """
  Convenient helper function to determine if environment is IPython.

  Sets matplotlib inline, if indeed in IPython
  Note that drawing is only safe in IPython qtconsole with matplotlib inline
  
  @return: True iff environment is IPython
  """
  try:
    __IPYTHON__
    ip = get_ipython()
    ip.magic("%matplotlib inline") 
  except NameError:
    return False
  else:
    return True

configure_ipython()

Algorithm.DEFAULT_PARAMS = {"draw":False, "verbosity" : Algorithm.QUIET}

@test
def LCR_UNI_RING():
    r = Unidirectional_Ring(6)
    LCR(r)
    assertLeaderElection(r)

@test
def LCR_BI_RING():
    r = Bidirectional_Ring(6)
    LCR(r)
    assertLeaderElection(r)

@test
def ASYNC_LCR_UNI_RING():
    r = Unidirectional_Ring(6)
    AsyncLCR(r)
    assertLeaderElection(r)

@test
def ASYNC_LCR_BI_RING():
    r = Bidirectional_Ring(6)
    AsyncLCR(r)
    assertLeaderElection(r)

@test
def HS_UNI_RING():
    r = Unidirectional_Ring(6)
    SynchHS(r)
    assertLeaderElection(r)

@test
def HS_BI_RING():
    r = Bidirectional_Ring(6)
    SynchHS(r)
    assertLeaderElection(r)

@test
def FLOODMAX_UNI_RING():
    r = Unidirectional_Ring(4)
    SynchFloodMax(r)
    assertLeaderElection(r)

@test
def FLOODMAX_BI_RING():
    r = Bidirectional_Ring(4)
    SynchFloodMax(r)
    assertLeaderElection(r)

@test
def FLOODMAX_BI_LINE():
    l = Bidirectional_Line(4)
    SynchFloodMax(l)
    assertLeaderElection(l)

@test
def FLOODMAX_COMPLETE_GRAPH():
    g = Complete_Graph(10)
    SynchFloodMax(g)
    assertLeaderElection(g)

@test
def FLOODMAX_RANDOM_GRAPH():
    g = Random_Line_Network(16)
    SynchFloodMax(g)
    assertLeaderElection(g)

@test
def SYNCH_BFS():
    x = Random_Line_Network(10)
    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFS(x)
    assertBFS(x)

@test
def SYNCH_BFS_ACK():
    x = Bidirectional_Line(6, lambda t:t)

    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFSAck(x)
    assertBFSWithChildren(x)

@test
def SYNCH_CONVERGE_HEIGHT():
    x = Random_Line_Network(10)

    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFS(x)
    assertBFS(x)

    SynchConvergeHeight(x)

@test
def SYNCH_BROADCAST_HEIGHT():
    x = Random_Line_Network(10)

    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFSAck(x)
    assertBFSWithChildren(x)

    SynchConvergeHeight(x)

    SynchBroadcast(x, {"attr":"height", "draw":False, "verbosity" : Algorithm.QUIET})
    assertBroadcast(x, 'height')

@test
def ASYNCH_BROADCAST_HEIGHT():
    x = Random_Line_Network(10)

    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFSAck(x)
    assertBFSWithChildren(x)

    AsynchConvergeHeight(x)

    SynchBroadcast(x, {"attr":"height", "draw":False, "verbosity" : Algorithm.QUIET})
    assertBroadcast(x, 'height')

@test
def send_receive_msgs():
    A = LCR()
    a1 = Message(A)
    a2 = Message(A)
    a3 = Message(A)

    B = LCR()
    b1 = Message(B)
    b2 = Message(B)

    x = Bidirectional_Ring(4, lambda p:p)
    assert x[0].get_msgs(A) == []
    x[0].send_msg(a1)
    x[0].send_msg(a2)
    assert a1.author == x[0] and a2.author == x[0]
    x[2].send_msg(a3)
    assert a3.author == x[2]
    x[0].send_msg(b1)
    assert b1.author == x[0]
    x[2].send_msg(b2)
    assert b2.author == x[2]

    assert x[1].get_msgs(B) == [b1,b2]
    assert x[1].get_msgs(A, x[0]) == [a1, a2]
    assert x[1].get_msgs(A, x[0]) == []
    assert x[1].get_msgs(A) == [a3]
    assert x[1].get_msgs(A) == []

@test
def SYNCH_DO_NOTHING():
    x = Random_Line_Network(5)
    state = x.state()
    assert Do_Nothing(x).message_count == 0
    assert state == x.state()

@test
def COMPOSE_SYNCH_LCR_AND_DO_NOTHING():
    x = Unidirectional_Ring(5)
    x1 = x.clone()

    A = LCR()
    A(x)
    assertLeaderElection(x)

    C = Compose(LCR(), Do_Nothing())
    C(x1)
    assertLeaderElection(x1)

    assert C.message_count == A.message_count, "Wrong message count"

@test
def COMPOSE_SYNCH_LCR():
    x = Unidirectional_Ring(10)
    x1 = x.clone()
    x2 = x.clone()

    A = LCR()
    A(x)
    assertLeaderElection(x)

    B = Compose(LCR(name="B1"), LCR(name="B2"))
    B(x1)
    assertLeaderElection(x1)

    C = Compose(Compose(LCR(), LCR()), LCR())
    C(x2)
    assertLeaderElection(x2)

    assert B.message_count == 2*A.message_count, "Compose LCR LCR wrong message count"
    assert C.message_count == 3*A.message_count, "Compose LCR LCR LCR wrong message count"

@test
def CHAIN_BROADCAST_HEIGHT():
    fm = SynchFloodMax()
    bfs = SynchBFSAck()
    converge = SynchConvergeHeight()
    broadcast = SynchBroadcast(params ={"attr":"height"})

    A = Chain(Chain(fm, bfs), Chain(converge, broadcast))
    x = Random_Line_Network(10)
    A(x)
    assertLeaderElection(x)
    assertBFSWithChildren(x)
    assertBroadcast(x, 'height')

@test
def SYNCH_LUBY_MIS_BI_RING():
    x = Bidirectional_Ring(10, lambda t:t)
    SynchLubyMIS(x)
    assertLubyMIS(x)

@test
def SYNCH_LUBY_MIS():
    x = Random_Line_Network(10)
    SynchLubyMIS(x)
    assertLubyMIS(x)

summarize()

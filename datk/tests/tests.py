"""
Algorithm Test Suite

Tests algorithms defined in algs.py.

From project root, can run:
$ nosetests datk.tests.tests
OR
$ python -m datk.tests.tests
"""

try:
    from datk.core.distalgs import *
    from datk.core.networks import *
    from datk.core.algs import *
    from datk.core.tester import Tester
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
tester = Tester(DEFAULT_TIMEOUT = 10, TEST_BY_DEFAULT = True, MAIN_THREAD_BY_DEFAULT = False)
test=tester.test

@test
def test_LCR_UNI_RING():
    r = Unidirectional_Ring(6)
    LCR(r)
    assertLeaderElection(r)

@test
def test_LCR_BI_RING():
    r = Bidirectional_Ring(6)
    LCR(r)
    assertLeaderElection(r)

@test
def test_ASYNC_LCR_UNI_RING():
    r = Unidirectional_Ring(6)
    AsyncLCR(r)
    assertLeaderElection(r)

@test
def test_ASYNC_LCR_BI_RING():
    r = Bidirectional_Ring(6)
    AsyncLCR(r)
    assertLeaderElection(r)

@test
def test_HS_BI_RING():
    r = Bidirectional_Ring(6)
    SynchHS(r)
    assertLeaderElection(r)

@test
def test_TS_UNI_RING():
    r = Unidirectional_Ring(6)
    SynchTimeSlice(r)
    assertLeaderElection(r)

@test
def test_TS_BI_RING():
    r = Bidirectional_Ring(6)
    SynchTimeSlice(r)
    assertLeaderElection(r)

@test
def test_VS_UNI_RING():
    r = Unidirectional_Ring(6)
    SynchVariableSpeeds(r)
    assertLeaderElection(r)

@test
def test_VS_BI_RING():
    r = Bidirectional_Ring(6)
    SynchVariableSpeeds(r)
    assertLeaderElection(r)

@test
def test_FLOODMAX_UNI_RING():
    r = Unidirectional_Ring(4)
    SynchFloodMax(r)
    assertLeaderElection(r)

@test
def test_FLOODMAX_BI_RING():
    r = Bidirectional_Ring(4)
    SynchFloodMax(r)
    assertLeaderElection(r)

@test
def test_FLOODMAX_BI_LINE():
    l = Bidirectional_Line(4)
    SynchFloodMax(l)
    assertLeaderElection(l)

@test
def test_FLOODMAX_COMPLETE_GRAPH():
    g = Complete_Graph(10)
    SynchFloodMax(g)
    assertLeaderElection(g)

@test
def test_FLOODMAX_RANDOM_GRAPH():
    g = Random_Line_Network(16)
    SynchFloodMax(g)
    assertLeaderElection(g)

@test
def test_SYNCH_BFS():
    x = Random_Line_Network(10)
    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFS(x)
    assertBFS(x)

@test
def test_SYNCH_BFS_ACK():
    x = Bidirectional_Line(6, lambda t:t)

    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFSAck(x)
    assertBFSWithChildren(x)

@test
def test_SYNCH_CONVERGE_HEIGHT():
    x = Random_Line_Network(10)

    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFS(x)
    assertBFS(x)

    SynchConvergeHeight(x)

@test
def test_SYNCH_BROADCAST_HEIGHT():
    x = Random_Line_Network(10)

    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFSAck(x)
    assertBFSWithChildren(x)

    SynchConvergeHeight(x)

    SynchBroadcast(x, {"attr":"height", "draw":False, "verbosity" : Algorithm.QUIET})
    assertBroadcast(x, 'height')

@test
def test_ASYNCH_BROADCAST_HEIGHT():
    x = Random_Line_Network(10)

    SynchFloodMax(x)
    assertLeaderElection(x)

    SynchBFSAck(x)
    assertBFSWithChildren(x)

    AsynchConvergeHeight(x)

    SynchBroadcast(x, {"attr":"height", "draw":False, "verbosity" : Algorithm.QUIET})
    assertBroadcast(x, 'height')

@test
def test_BELLMAN_FORD():
    def assertAPSP(network):
        weights = {}
        for p in network:
            for q in network:
                if p == q:
                    continue
                w = p.state['SP'][q.UID]
                weights[(p,q)] = w
                if (q,p) in weights:
                    if weights[(q,p)] != w:
                        raise Exception('FAILED APSP!')
    def add_random_undirected_edge_weights(network, lower_bound= 0, upper_bound=None):
        #Generate random (undirected) weights for all edges.
        import random
        if upper_bound == None:
            upper_bound = len(network)

        weights = {}
        for p in network:
            for q in network:
                if q in p.out_nbrs:
                    if (q,p) in weights:
                        w = weights[(q,p)]
                    else:
                        w = random.randint(lower_bound, upper_bound)
                    weights[(p, q)] = w

        #Apply them to the network. Updating p.state['APSP'][q.UID] with weight(p,q)
        for process in network:
            p.state['nbr_dist'] = {}
        for edge, weight in weights.items():
            p, q = edge
            p.state['nbr_dist'][q.UID] = weight

    r = Bidirectional_Line(5, lambda n: n)
    add_random_undirected_edge_weights(r)
    SynchBellmanFord(r)

    assertAPSP(r)

@test
def test_send_receive_msgs():
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
def test_network_snapshots():
    x = Unidirectional_Ring(5)

    assert len(x._snapshots) == 1, "Network initial snapshot not saved"

    snap_0 = x.get_snapshot()
    lcr = LCR(x)
    snap_1 = x.get_snapshot()
    assert len(x._snapshots) == lcr.r+2, "Algorithm doesn't append 1 snapshot per round"
    assert snap_0 != snap_1, "Current snapshot unchanged after algo"

    snapshots_before_restore = x._snapshots[:]
    x.restore_snapshot(0)
    assert snapshots_before_restore == x._snapshots, "restore_snapshots modified self.snapshots"

@test
def test_SYNCH_DO_NOTHING():
    x = Random_Line_Network(5)
    state = x.state()
    assert Do_Nothing(x).message_count == 0
    assert state == x.state()

@test
def test_COMPOSE_SYNCH_LCR_AND_DO_NOTHING():
    x = Unidirectional_Ring(5)

    A = LCR()
    A(x)
    assertLeaderElection(x)

    x.restore_snapshot(0)

    C = Compose(LCR(), Do_Nothing())
    C(x)
    assertLeaderElection(x)

    assert C.message_count == A.message_count, "Wrong message count"

@test
def test_COMPOSE_SYNCH_LCR():
    x = Unidirectional_Ring(10)

    A = LCR()
    A(x)
    assertLeaderElection(x)

    x.restore_snapshot(0)

    B = Compose(LCR(name="B1"), LCR(name="B2"))
    B(x)
    assertLeaderElection(x)

    x.restore_snapshot(0)

    C = Compose(Compose(LCR(), LCR()), LCR())
    C(x)
    assertLeaderElection(x)

    assert B.message_count == 2*A.message_count, "Compose LCR LCR wrong message count"
    assert C.message_count == 3*A.message_count, "Compose LCR LCR LCR wrong message count"

@test
def test_CHAIN_BROADCAST_HEIGHT():
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
def test_SYNCH_LUBY_MIS_BI_RING():
    x = Bidirectional_Ring(10, lambda t:t)
    SynchLubyMIS(x)
    assertLubyMIS(x)

@test
def test_SYNCH_LUBY_MIS():
    x = Random_Line_Network(10)
    SynchLubyMIS(x)
    assertLubyMIS(x)
    
tester.summarize()

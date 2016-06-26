"""
Helper functions for tests in tests.py
"""
from datk.core.distalgs import Process
from datk.core.networks import Random_Line_Network

def assertLeaderElection(
    network,
    isLeader = lambda p: "status" in p.state and p.state["status"]=="leader",
    isNonleader = lambda p: "status" in p.state and p.state["status"]=="non-leader"
    ):
    """Asserts that exactly one Process is Leader, and all other processes are Non-Leader"""

    assert sum([isLeader(p) for p in network]) == 1 , "Leader Election Failed"
    assert sum([isNonleader(p) for p in network]) == len(network)-1, "Leader Election Failed"

def assertBroadcast(network, attr):
    """Asserts that p.state[attr] is identical for all processes p"""
    for p in network:
        assert attr in p.state
    assert len(set([p.state[attr] for p in network])) == 1, "Broadcasting " + attr + " failed."

def assertBFS(network):
    """Asserts that every Process, p, knows 'parent', and there 
     exists exactly one Process where 'parent' is None"""
    found_root = False
    for p in network:
        assert 'parent' in p.state, "BFS Failed. state['parent'] not found."
        if p.state['parent'] is None:
            if found_root:
                assert False, "BFS failed. No unique root node"
            else:
                found_root = True
        else:
            assert isinstance(p.state['parent'], Process), "BFS FAILED"

def assertBFSWithChildren(network):
    """Asserts that every Process, p, knows 'parent' and 'children', and there
    exists exactly one Process where 'parent' is None"""
    found_root = False
    for p in network:
        assert 'parent' in p.state, "BFS Failed. state['parent'] not found."
        if p.state['parent'] is None:
            if found_root:
                assert False, "BFS failed. No unique root node"
            else:
                found_root = True
        else:
            assert isinstance(p.state['parent'], Process), "BFS FAILED"
            assert p in p.state['parent'].state['children'], "BFS FAILED"

def assertLubyMIS(network):
    """Asserts that every process knows a boolean value, 'MIS', and that the Processes
    where 'MIS' is True form a set that is both independent and maximal."""
    for process in network:
        assert 'MIS' in process.state, "'MIS' not in Process state"
        assert isinstance(process.state['MIS'], bool)
        if process.state['MIS'] == True:
            assert not any([nbr.state['MIS'] for nbr in process.out_nbrs]), 'MIS not independent'
        if process.state['MIS'] == False:
            assert any([nbr.state['MIS'] for nbr in process.out_nbrs]), 'MIS not maximal'

def Artificial_LE_Network(n):
    x = Random_Line_Network(n)
    for p in x:
        if p.UID == n-1:
            p.state['status'] = 'leader'
    return x

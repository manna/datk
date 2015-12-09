from threading import Thread, Lock
from time import sleep, time
from distalgs import Process

TIMEOUT = 5
lock = Lock()
num_tests = 0
failed_tests = set()

def test(f=None, timeout=TIMEOUT, main_thread=False, test=True):
    if not test: return lambda f: f

    #If main_thread = True, timeout and precision are ignored.
    def test_decorator(f):
        global lock

        def test_f():
            global num_tests
            global failed_tests
            try:
                f()
            except Exception, e:
                failed_tests.add(f.__name__)
                print_with_underline("TEST "+f.__name__+" FAILED.")
                raise e
            finally:
                num_tests+=1
        with lock:
            if main_thread:
                status = "Running test "+f.__name__+" on main thread."
                print status
                test_f()
                print "#"*len(status)
            else:
                t = Thread(target = test_f)
                t.daemon = True
                
                start_time = time()
                t.start()
                t.join(timeout)
                end_time = time()
                if end_time - start_time >= timeout:
                    failed_tests.add(f.__name__)
                    print_with_underline(f.__name__ + " TIMED OUT AFTER " + str(timeout) + "s")
                else:
                    print_with_underline(f.__name__ + " RAN IN " +str(end_time-start_time) + "s")
    if f is None:
        return test_decorator
    else:
        test_decorator(f)
        return f

def print_with_underline(text):
    print text
    print "#"*len(text)

def testLeaderElection(network, isLeader = lambda p: "status" in p.state and p.state["status"]=="leader", isNonleader = lambda p: "status" in p.state and p.state["status"]=="non-leader"):
    assert sum([isLeader(p) for p in network]) == 1 , "Leader Election Failed"
    assert sum([isNonleader(p) for p in network]) == len(network)-1, "Leader Election Failed"

def testBroadcast(network, attr):
    """p.state[attr] is identical for all processes p"""
    for p in network:
        assert attr in p.state
    assert len(set([p.state[attr] for p in network])) == 1, "Broadcasting " + attr + " failed."

def testBFS(network):
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

def testBFSWithChildren(network):
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

def testLubyMIS(network):
    for process in network:
        assert 'MIS' in process.state, "'MIS' not in Process state"
        assert isinstance(process.state['MIS'], bool)
        if process.state['MIS'] == True:
            assert not any([nbr.state['MIS'] for nbr in process.out_nbrs]), 'MIS not independent'
        if process.state['MIS'] == False:
            assert any([nbr.state['MIS'] for nbr in process.out_nbrs]), 'MIS not maximal'

def summarize():
    global num_tests
    global failed_tests
    
    print num_tests, "tests ran with", len(failed_tests), "failures:", sorted(list(failed_tests))

    num_tests = 0
    failed_tests = set()

from threading import Thread, Lock
from time import sleep
from distalgs import Process

TIMEOUT = 5
PRECISION = 0.1

lock = Lock()
num_tests = 0
failed_tests = set()

def test(f=None, timeout=TIMEOUT, precision = PRECISION, main_thread=False):
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
                raise e
                print "TEST", f.__name__, "FAILED."
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
                t.start()

                timer = 0.
                while timer < timeout:
                    sleep(precision)
                    if not t.isAlive():
                        result = f.__name__ + " RAN IN " +str(timer) + "s"
                        print result
                        print "#"*len(result)
                        break
                    timer+=precision

                if t.isAlive():
                    result = f.__name__ + " TIMED OUT AFTER " + str(timeout) + "s"
                    print result
                    print "#"*len(result)
    if f is None:
        return test_decorator
    else:
        test_decorator(f)

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
        assert 'parent' in p.state
        if p.state['parent'] is None:
            if found_root:
                assert False, "BFS failed. No unique root node"
            else:
                found_root = True
        else:
            assert isinstance(p.state['parent'], Process)

def testBFSWithChildren(network):
    found_root = False
    for p in network:
        assert 'parent' in p.state
        if p.state['parent'] is None:
            if found_root:
                assert False, "BFS failed. No unique root node"
            else:
                found_root = True
        else:
            assert isinstance(p.state['parent'], Process)
            assert p in p.state['parent'].state['children']

def begin_testing():
    global num_tests
    global failed_tests
    num_tests = 0
    failed_tests = set()

def summarize():
    print num_tests, "tests ran with", len(failed_tests), "failures:", sorted(list(failed_tests))
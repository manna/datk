from threading import Thread, Lock
from time import sleep

TIMEOUT = 5
PRECISION = 0.1

lock = Lock()

def test(f=None, timeout=TIMEOUT, precision = PRECISION, main_thread=False):
    global lock
    #If main_thread = True, timeout and precision are ignored.
    def test_decorator(f):
        with lock:
            if main_thread:
                print "Running test "+f.__name__+" on main thread."
                f()
                print "#"*len("Running test "+f.__name__+" on main thread.")

            else:
                t = Thread(target = f)
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

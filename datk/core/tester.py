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

def summarize():
    global num_tests
    global failed_tests
    
    print num_tests, "tests ran with", len(failed_tests), "failures:", sorted(list(failed_tests))

    num_tests = 0
    failed_tests = set()

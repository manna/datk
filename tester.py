from threading import Thread
from time import sleep

TIMEOUT = 5
PRECISION = 0.1
def test(f=None, timeout=TIMEOUT, precision = PRECISION, main_thread=False):
    #If main_thread = True, timeout and precision are ignored.
    def test_decorator(f):
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
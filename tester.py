from threading import Thread
from time import sleep

TIMEOUT = 5
PRECISION = 0.1
def test(f=None, timeout=TIMEOUT, precision = PRECISION):
    def test_decorator(f):
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
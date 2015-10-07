from threading import Thread
from time import sleep

TIMEOUT = 10
PRECISION = 0.1
def test(f, timeout=TIMEOUT, precision = PRECISION):
    t = Thread(target = f)
    t.daemon = True
    t.start()

    timer = 0.
    while timer < timeout:
        sleep(precision)
        if not t.isAlive():
            print f.__name__ + " RAN IN " +str(timer) + "s"
            break
        timer+=precision

    if t.isAlive():
        print f.__name__ + " TIMED OUT AFTER " + str(timeout) + "s"
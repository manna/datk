from distalgs import *
from networks import *
from algs import *

import sys



TIMEOUT = 5

def main():
    x = Unidirectional_Ring(3)
    LCR(x)

    y = Unidirectional_Ring(6)
    AsyncLCR(y)


t = Thread(target = main)
t.daemon = True
t.start()

sleep(TIMEOUT)
if t.isAlive():
    sys.exit("TIMED OUT AFTER " + str(TIMEOUT) + " seconds.")
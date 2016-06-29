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
$ python -m datk.tests.gui_tests """)

from helpers import Artificial_LE_Network
from mock import patch

Algorithm.DEFAULT_PARAMS = {"draw":False, "verbosity" : Algorithm.QUIET}

def test_network_draw_tk():
    from datk.core.simulator_tk import draw
    from Tkinter import Tk
    with patch.object(Tk, 'mainloop'):
        x = Unidirectional_Ring(6)
        LCR(x)
        draw(x)

def test_network_simulate_tk():
    from datk.core.simulator_tk import simulate
    from Tkinter import Tk
    with patch.object(Tk, 'mainloop'):
        x = Unidirectional_Ring(6)
        LCR(x)
        simulate(x)
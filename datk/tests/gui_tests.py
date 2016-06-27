import matplotlib.pyplot as plt
plt.switch_backend('Agg')

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

def test_network_draw():
    Random_Line_Network(5).draw() #Spectral draw
    Bidirectional_Ring(7).draw() #Circular draw

def test_LE_network_draw():
    x = Bidirectional_Ring(8)
    A = LCR(x)
    node_colors, edge_colors = A.get_draw_args(x)
    assert edge_colors is None
    assert len(node_colors) == len(x)
    x.draw()

def test_BFS_network_draw():
    x = Artificial_LE_Network(8)
    A = SynchBFS(x)
    node_colors, edge_colors = A.get_draw_args(x)
    assert node_colors is None
    assert edge_colors is not None
    x.draw()

def test_network_draw_qt():
    from datk.core.simulator_qt import draw
    from PyQt4.QtGui import QApplication
    with patch.object(QApplication, 'exec_', return_value=0):
        x = Unidirectional_Ring(6)
        LCR(x)
        draw(x)

def test_network_simulate_qt():
    from datk.core.simulator_qt import simulate
    from PyQt4.QtGui import QApplication
    with patch.object(QApplication, 'exec_', return_value=0):
        x = Unidirectional_Ring(6)
        LCR(x)
        simulate(x)
        
#TODO figure out how to correctly mock Tkinter
# def test_network_draw_tk():
#     from datk.core.simulator_tk import draw
#     from Tkinter import Tk
#     with patch.object(Tk, 'mainloop'):
#         x = Unidirectional_Ring(6)
#         LCR(x)
#         draw(x)
"""
Network Test Suite

Tests Netwoks defined in networks.py by visual inspection
"""
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
from nose.tools import timed

from datk.core.networks import *

@timed(2)
def test_draw_random():
    Random_Line_Network(25).draw()

@timed(2)
def test_draw_uni_ring():
    Unidirectional_Ring(25).draw()

@timed(2)
def test_draw_bi_ring():
    Bidirectional_Ring(25).draw()

@timed(2)
def test_draw_complete_graph():
    Complete_Graph(25).draw()

@timed(2)
def test_draw_uni_line():
    Unidirectional_Line(25).draw()

@timed(2)
def test_draw_bi_line():
    Bidirectional_Line(25).draw()

@timed(20)
def test_draw_huge_random():
    x = Random_Line_Network(50, sparsity=0.2)
    x.draw()

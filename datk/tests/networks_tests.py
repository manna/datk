"""
Network Test Suite

Tests Netwoks defined in networks.py by visual inspection
"""
import matplotlib.pyplot as plt
plt.switch_backend('Agg')

from datk.core.networks import *

def test_draw_random():
    Random_Line_Network(25).draw()

# def test_draw_huge_random():
#     Random_Line_Network(100, sparsity=0.2).draw()

def test_draw_uni_ring():
    Unidirectional_Ring(4).draw()

def test_draw_bi_ring():
    Bidirectional_Ring(7).draw()

def test_draw_complete_graph():
    Complete_Graph(10).draw()

def test_draw_uni_line():
    Unidirectional_Line(4).draw()

def test_draw_bi_line():
    Bidirectional_Line(5).draw()
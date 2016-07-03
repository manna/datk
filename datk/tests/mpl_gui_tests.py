import matplotlib.pyplot as plt
plt.switch_backend('Agg')

from datk.core.networks import Unidirectional_Ring, Bidirectional_Ring
from datk.core.algs import LCR, SynchBFS

from helpers import Artificial_LE_Network, assertLeaderElection

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

def test_benchmark_LCR_Unidirectional_Ring():
    from datk.core.benchmark import benchmark
    benchmark(LCR, Unidirectional_Ring, assertLeaderElection)

def test_network_draw_mpl():
    from datk.core.simulator_mpl import draw
    x = Unidirectional_Ring(6)
    LCR(x)
    draw(x)
from distalgs import *
from networks import *
from algs import *
from tester import *
import math

# @test(precision = 1e-7)
def LCR_UNIDIR_RING():
    r = Unidirectional_Ring(3)
    LCR(r)

# @test(precision = 1e-3)
def ASYNC_LCR_UNIDIR_RING():
    r = Unidirectional_Ring(6)
    AsyncLCR(r)

# @test
def send_receive_msgs():
    x = Bidirectional_Ring(4, lambda p:p)
    assert x[0].get_msgs() == []
    x[0].send_to_all_neighbors("hi")
    x[0].send_to_all_neighbors("hey")
    x[2].send_to_all_neighbors("yo")
    assert x[1].get_msgs(x[0]) == ["hi", "hey"]
    assert x[1].get_msgs(x[0]) == []
    assert x[1].get_msgs() == ["yo"]
    assert x[1].get_msgs() == []

from matplotlib import pyplot as plt

def draw(network):
    n = len(network)

    vals = []

    for k in range(n):
        vals.append( (math.cos(2*k*math.pi/n), math.sin(2*k*math.pi/n) ) )
        
        plt.xlim([-1.2, 1.2]) 
        plt.ylim([-1.2, 1.2]) 
    plt.plot( [v[0] for v in vals], [v[1] for v in vals], 'ro' )

    for i in range(n):

        n[i].out_nbrs

# draw(Unidirectional_Ring(10))

x = Unidirectional_Ring(4)
print x.index(x[3])
plt.plot([0,0], [0,1])
plt.show()

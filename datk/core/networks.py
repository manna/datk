from distalgs import Network
import math
import random
import pdb

class Unidirectional_Ring(Network):
    """A Network of n Processes arranged in a ring. Each edge is directed
        from a Process to its clockwise neighbor, that is, messages can
        only be sent in a clockwise direction."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n):
            self[i].link_to(self[(i+1)%n])

class Bidirectional_Ring(Network):
    """A Network of n Processes arranged in a ring. Each edge between a Process
        and its neighbor is undirected, that is, messages can be sent in both
        the clockwise and the counterclockwise directions."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n):
            self[i].link_to(self[(i+1)%n])
            self[i].link_to(self[(i-1)%n])

class Unidirectional_Line(Network):
    """A Network of n Processes arranged in a line. Each edge is directed
        from a Process to its clockwise neighbor, that is, messages can
        only be sent in a clockwise direction."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n-1):
            self[i].link_to(self[(i+1)])

class Bidirectional_Line(Network):
    """A Network of n Processes arranged in a line. Each edge between a Process
        and its neighbor is undirected, that is, messages can be sent in both
        the clockwise and the counterclockwise directions."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n-1):
            self[i].bi_link(self[(i+1)])

class Complete_Graph(Network):
    """A Network of n Processes arranged at the vertices of a Complete undirected
    graph of size n."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n-1):
            for j in range(i+1,n):
                self[i].bi_link(self[j])
    def draw(self, style='circular'):
        Network.draw(self, style=style)

class Random_Line_Network(Network):
    """A Network of n processes arranged randomly at the vertices of a connected
    undirected line graph of size n. Additional pairs of vertices are connected
    at random with a probability that is inversely proportional to the difference
    in their positions on the line.

    For example, the Process at index 3 is guaranteed to be connected to the Process
    at index 4, and is more likely to be connected to the Process at index 5 than to
    the Process at index 8. """
    def __init__(self, n, sparsity = 1):
        """
        sparsity = 0 --> a Complete_Graph(n)
        sparsity = infinity --> a Bidirectional_Line(n)
        """
        Network.__init__(self, n)
        def sigmoid(t):
            if t > 100: return 1.
            if t < -100: return 0.
            return 1./(1.+math.exp(-t))

        for i in range(n-1):
            self[i].bi_link(self[(i+1)])
            for j in range(i+2, n):
                if random.random() < sigmoid( -((i-j)**2)/(float(n)**0.5)*sparsity)  *2.:
                    self[i].bi_link(self[j])

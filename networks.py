from distalgs import Network
import pdb

class Unidirectional_Ring(Network):
    """A Network of n Processes arranged in a ring. Each edge is directed
        from a Process to its clockwise neighbor, that is, messages can
        only be sent in a clockwise direction."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n):
            self[i].linkTo(self[(i+1)%n])

class Bidirectional_Ring(Network):
    """A Network of n Processes arranged in a ring. Each edge between a Process
        and its neighbor is undirected, that is, messages can be sent in both
        the clockwise and the counterclockwise directions."""
    def __init__(self, n, index_to_UID= None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n):
            self[i].linkTo(self[(i+1)%n])
            self[i].linkTo(self[(i-1)%n])

class Unidirectional_Line(Network):
    """A Network of n Processes arranged in a line. Each edge is directed
        from a Process to its clockwise neighbor, that is, messages can
        only be sent in a clockwise direction."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n-1):
            self[i].linkTo(self[(i+1)])

class Bidirectional_Line(Network):
    """A Network of n Processes arranged in a line. Each edge between a Process
        and its neighbor is undirected, that is, messages can be sent in both
        the clockwise and the counterclockwise directions."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n-1):
            self[i].linkTo(self[(i+1)])
            self[i+1].linkTo(self[i])

class Complete_Graph(Network):
    """A Network of n Processes arranged at the vertices of a Complete undirected
    graph of size n."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n-1):
            for j in range(i+1,n):
                self[i].linkTo(self[j])
                self[j].linkTo(self[i])
from distalgs import Network
import pdb

class Unidirectional_Ring(Network):
    """A Network of n Processes arranged in a ring. Each edge is directed
        from a Process to its clockwise neighbor, that is, messages can
        only be sent in a clockwise direction."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n):
            self[i].in_nbrs.append(self[(i-1)%n])
            self[i].out_nbrs.append(self[(i+1)%n])

class Bidirectional_Ring(Network):
    """A Network of n Processes arranged in a ring. Each edge between a Process
        and its neighbor is undirected, that is, messages can be sent in both
        the clockwise and the counterclockwise directions."""
    def __init__(self, n, index_to_UID= None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n):
            self[i].in_nbrs.append(self[(i-1)%n])
            self[i].in_nbrs.append(self[(i+1)%n])
            self[i].out_nbrs.append(self[(i-1)%n])
            self[i].out_nbrs.append(self[(i+1)%n])

class Unidirectional_Line(Network):
    """A Network of n Processes arranged in a line. Each edge is directed
        from a Process to its clockwise neighbor, that is, messages can
        only be sent in a clockwise direction."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        self[0].out_nbrs.append(self[1])
        for i in range(1, n-1):
            self[i].in_nbrs.append(self[i-1])
            self[i].out_nbrs.append(self[i+1])
        self[n-1].in_nbrs.append(self[n-2])

class Bidirectional_Line(Network):
    """A Network of n Processes arranged in a line. Each edge between a Process
        and its neighbor is undirected, that is, messages can be sent in both
        the clockwise and the counterclockwise directions."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        self[0].out_nbrs.append(self[1])
        self[0].in_nbrs.append(self[1])
        for i in range(1, n-1):
            self[i].in_nbrs.append(self[i-1])
            self[i].in_nbrs.append(self[i+1])
            self[i].out_nbrs.append(self[i+1])
            self[i].out_nbrs.append(self[i-1])
        self[n-1].in_nbrs.append(self[n-2])
        self[n-1].out_nbrs.append(self[n-2])


from distalgs import Network

class Unidirectional_Ring(Network):
    """A Network of n Processes arranged in a ring. Each edge is directed
        from a Process to its clockwise neighbor, that is, messages can
        only be sent in a clockwise direction."""
    def __init__(self, n, index_to_UID = None):
        Network.__init__(self, n, index_to_UID)
        for i in range(n):
            self.processes[i].in_nbrs.append(self.processes[(i-1)%n])
            self.processes[i].out_nbrs.append(self.processes[(i+1)%n])

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
from enum import Enum, unique

@unique
class Color(Enum):
    red = 'red'
    blue = 'blue'
    green = 'green'
    black = 'black'
    yellow = 'yellow'

    def toQt(self):
        return self.value

    def toMpl(self):
        mpl = {
            'red': 'r',
            'blue': 'b',
            'green': 'g',
            'black': 'k',
            'yellow': 'y'
        }
        return mpl[self.value]

    def toTk(self):
        return self.value


def Colorizer(algorithm, network, algorithm_type):
    """
    algorithm_type can have following values thus far:
    leader_election
    BFS
    """
    if algorithm_type == "leader_election":
        node_colors = {}
        edge_colors = None
        for p in network.processes:
            if p.state['status'] == "leader":
                node_colors[p.UID] = Color.red

            elif p.state['status'] == "non-leader": # non-leader
                node_colors[p.UID] = Color.blue
            else:
                node_colors[p.UID] = Color.yellow

        return node_colors, edge_colors

    elif algorithm_type == "BFS":
        node_colors = None
        edge_colors = dict()
        for p in network.processes:
            if p.state['parent']:
                parent_UID = p.state['parent'].UID

                edge_colors[(p.UID,parent_UID)] = Color.green

        return node_colors, edge_colors

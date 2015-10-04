"""A Python Toolkit for Distributed Algorithms

Author: Amin Manna <manna@mit.edu>

"""
#Generate documentation by running pydoc -w distalgs

import random
from random import shuffle
from threading import Thread
from time import sleep
import pdb


#toolkit.py
class Message():
    def __init__(self, content= None):
        self.content = content

class Process:
    """A computing element located at a node of a directed network graph.
    Processes are identical except for their UID"""
    def __init__(self, UID, state = None, in_nbrs = [], out_nbrs = []):
        self.UID = UID
        self.state = state or {"send" : self.UID, "sends": [self.UID], "halted" : False} #TODO generalize
        
        self.in_nbrs = in_nbrs or []   # Don't remove or []
        self.out_nbrs = out_nbrs or [] # Don't remove or []

        self.in_channel = {}
        
    def output(self, status):
        if "status" in self.state.keys():
            return
        self.state["status"] =  status
        print str(self) + " is " +status

    def send_to_all_neighbors(self, msg):
        for nbr in self.out_nbrs:
            if nbr.in_nbrs.index(self) in nbr.in_channel:
                nbr.in_channel[nbr.in_nbrs.index(self)].append(msg)
            else:
                nbr.in_channel[nbr.in_nbrs.index(self)] = [msg]

    def __str__(self):
        return "P"+str(self.UID)
    def __repr__(self):
        return "P" + str(self.UID) + " -> {"+", ".join([str(process) for process in self.out_nbrs]) + "}" 

class Network:
    """ A collection of Processes.
    Known subclasses: Unidirectional_Ring, Bidirectional_Ring """
    def __init__(self, processes):
        self.processes = processes
    def __init__(self, n, index_to_UID = None):
        """
        Creates a network of n disconnected Processes,
        with random distinct UIDs, or as specified by
        the index_to_UID function
        """
        if index_to_UID is None:
            self.processes = [Process(i) for i in range(n)]
            shuffle(self.processes)
        else:
            self.processes = [Process(index_to_UID(i)) for i in range(n)]
    def __getitem__(self, i):
        return self.processes[i]
    def __len__(self):
        return len(self.processes)
    def __repr__(self):
        return str(self.processes)
    def run(self, algorithm):
        algorithm(self)

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

class Algorithm():
    """
    Abstract superclass for a distributed algorithm.
    """
    def __init__(self, msgs_i, trans_i, halt_i, network = None, name = None):
        self.msgs_i = msgs_i
        self.trans_i = trans_i
        self.halt_i = halt_i

        #Algorithm name defaults to X for class X(Algorithm).
        self.name = name
        if name is None:
            self.name = self.__class__.__name__

        #If the network is specified, run the algorithm.
        if network is not None:
            self(network)
    def __call__(self, network, *args):
        self.run(network, *args)
    def run(self, network, *args):
        raise NotImplementedError

class Synchronous_Algorithm(Algorithm):
    """
    We assume that Processes take steps simultaneously,
    that is, that execution proceeds in synchronous rounds.
    """
    def run(self, network, *args):
        self.halted = False
        header = "Running " + self.name + " on"
        print len(header)*"-"
        print header
        print str(network)
        self.network = network
        round_number = 1
        while not self.halted:
            print "Round "+str(round_number)
            self.round()
            round_number+=1
    def round(self):
        self.msgs()
        self.trans()
        self.halt()
    def msgs(self):
        for process in self.network:
            self.msgs_i(process)
    def trans(self):
        for process in self.network:
            self.trans_i(process)
    def halt(self):
        if sum([self.halt_i(process) for process in self.network]) == len(self.network):
            self.halted = True
            print "Algorithm Terminated"
            print "--------------------"

class Asynchronous_Algorithm(Algorithm):
    """
    We assume that the separate Processes take steps
    in an arbitrary order, at arbitrary relative speeds.
    """
    def run(self, network, *args):
        header = "Running " + self.name + " on"
        print len(header)*"-"
        print header
        print str(network)

        self.network = network
        round_number = 1

        def run_process(process):
            while True:
                sleep(random.random())
                self.msgs_i(process)
                if self.halt_i(process):
                    break
                self.trans_i(process)
                if self.halt_i(process):
                    break

        threads = []
        for process in network.processes:
            thread = Thread(target = run_process, args = (process,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        print "Algorithm Terminated"
        print "--------------------"

#algos.py
class LCR(Synchronous_Algorithm):
    """
    The LeLann, Chang and Roberts algorithm for Leader Election in a Synchronous Unidirectional_Ring. 
    
    Each Process sends its identifier around the ring.
    When a Process receives an incoming identifier, it compares that identifier to its own.
    If the incoming identifier is greater than its own, it keeps passing the identifier;
    if it is less than its own, it discards the incoming identifier;
    if it is equal to its own, the Process declares itself the leader.
    """
    def __init__(self, network = None):
        def LCR_msgs(p):
            msg = p.state["send"]
            if msg is None:
                return
            p.state["send"] = None
            for nbr in p.out_nbrs:
                nbr.in_channel[nbr.in_nbrs.index(p)] = msg
        def LCR_trans(p, verbose=False):
            for pos in p.in_channel.keys():
                if p.in_channel[pos] == p.UID:
                    p.output("leader")
                elif p.in_channel[pos] > p.UID:
                    p.state["send"] = p.in_channel[pos]
                    p.output("non-leader")
                else:
                    p.state["send"] = None
            if verbose:
                print str(p) + " received " + str(p.in_channel)
                print "state: " + str(p.state)
        Synchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, lambda p : "status" in p.state, network = network )

# x = Unidirectional_Ring(6)
# LCR(x)

class AsyncLCR(Asynchronous_Algorithm):
    class Leader_Declaration(Message):
        pass
    def __init__(self, network = None):
        def LCR_msgs(p):
            if "status" in p.state and p.state["status"] == "leader":
                msg = AsyncLCR.Leader_Declaration()
                p.send_to_all_neighbors(msg)
                p.state["halted"] = True
                return
            while len(p.state["sends"]) > 0:
                #This block of code should be simply p.broadcast(msg)
                msg = p.state["sends"].pop()
                p.send_to_all_neighbors(msg)

        def LCR_trans(p, verbose=False):
            if verbose:
                print str(p) + " received " + str(p.in_channel)
            for pos in p.in_channel.keys():
                while len(p.in_channel[pos]) > 0:
                    msg = p.in_channel[pos].pop()
                    if isinstance(msg, AsyncLCR.Leader_Declaration):
                        p.state["halted"] = True
                        return
                    if msg == p.UID:
                        p.output("leader")
                    elif msg > p.UID:
                        p.state["sends"].append(msg)
                        p.output("non-leader")
            if verbose:
                print "state: " + str(p.state)

        Asynchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, lambda p : p.state["halted"]==True, network = network )

x = Unidirectional_Ring(6)
LCR(x)

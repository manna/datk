"""
A Python Toolkit for Distributed Algorithms

Author: Amin Manna <manna@mit.edu>
        Mayuri Sridhar <mayuri@mit.edu>
"""
#Generate documentation by running pydoc -w distalgs

import random
from random import shuffle
from threading import Thread
from time import sleep
import pdb

class Message:
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
        self.algs = set()

    def output(self, status):
        if "status" in self.state.keys():
            return
        self.state["status"] =  status
        print str(self) +  " is " +status

    def send_to_all_neighbors(self, msg):
        for nbr in self.out_nbrs:
            if nbr.in_nbrs.index(self) in nbr.in_channel:
                nbr.in_channel[nbr.in_nbrs.index(self)].append(msg)
            else:
                nbr.in_channel[nbr.in_nbrs.index(self)] = [msg]

    def add(self, algorithm):
        self.algs.add(algorithm)

    def terminate(self, algorithm):
        if algorithm in self.algs:
            self.algs.remove(algorithm)

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
    def add(self, algorithm):
        for process in self.processes:
            process.add(algorithm)
    def run(self, algorithm):
        algorithm(self)

class Algorithm:

    """
    Abstract superclass for a distributed algorithm.
    """
    def __init__(self, msgs_i, trans_i, halt_i = None, network = None, name = None):
        self.msgs_i = msgs_i
        self.trans_i = trans_i
        
        self.halt_i_ = halt_i

        #Algorithm name defaults to X for class X(Algorithm).
        self.name = name
        if name is None:
            self.name = self.__class__.__name__

        #If the network is specified, run the algorithm.
        if network is not None:
            self(network)

    def halt_i(self, p):
        if self.halt_i_ is not None:
            return self.halt_i_(p)
        return self not in p.algs

    def __call__(self, network, *args):
        self.run(network, *args)
    def run(self, network, *args):
        raise NotImplementedError

    def halt(self):
        if sum([self.halt_i(process) for process in self.network]) == len(self.network):
            self.halted = True
            print "Algorithm Terminated"
            print "--------------------"

class Synchronous_Algorithm(Algorithm):
    """
    We assume that Processes take steps simultaneously,
    that is, that execution proceeds in synchronous rounds.
    """
    def run(self, network, *args):
        header = "Running " + self.name + " on"
        print len(header)*"-"
        print header
        print str(network)
        self.network = network

        self.halted = False
        network.add(self)

        round_number = 1
        while not self.halted:
            print "Round "+str(round_number)
            self.round()
            self.halt()
            round_number+=1
    def round(self):
        self.msgs()
        self.trans()
    def msgs(self):
        for process in self.network:
            self.msgs_i(process)
    def trans(self):
        for process in self.network:
            self.trans_i(process)

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
        network.add(self)
        round_number = 1

        threads = []
        for process in network.processes:
            thread = Thread(target = self.run_process, args = (process,))
            threads.append(thread)
            thread.start()

        for thread in threads: thread.join()
        self.halt()
    
    def run_process(self, process):
        while True:
            sleep((random.random()+1.)/5.)
            self.msgs_i(process)
            if self.halt_i(process):
                break
            self.trans_i(process)
            if self.halt_i(process):
                break
    
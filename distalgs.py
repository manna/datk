"""
A Python Toolkit for Distributed Algorithms

Author: Amin Manna <manna@mit.edu>
        Mayuri Sridhar <mayuri@mit.edu>
"""
#Generate documentation by running pydoc -w distalgs

import random
from random import shuffle
import threading
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
        self.state = state or {
                                "diam" : 10
                                                    } #TODO generalize
        
        self.in_nbrs = in_nbrs or []   # Don't remove or []
        self.out_nbrs = out_nbrs or [] # Don't remove or []

        self.in_channel = {}
        self.algs = set()

    def link_to(self, new_out_nbr):
        if new_out_nbr not in self.out_nbrs:
            self.out_nbrs.append(new_out_nbr)
        if self not in new_out_nbr.in_nbrs:
            new_out_nbr.in_nbrs.append(self)
    def bi_link(self, nbr):
        self.link_to(nbr)
        nbr.link_to(self)

    def output(self, status, silent=False):
        if "status" in self.state.keys():
            return
        self.state["status"] =  status
        if not silent:
            print str(self) +  " is " +status

    def send_to_all_neighbors(self, algorithm, msg):
        self.send_msg(algorithm, msg)

    def send_msg(self, algorithm, msg, out_nbrs=None):
        if out_nbrs is None:
            out_nbrs = self.out_nbrs
        elif isinstance(out_nbrs, Process):
            out_nbrs = [out_nbrs]
        if isinstance(out_nbrs, list):
            algorithm.count_msg(len(out_nbrs))
            for nbr in out_nbrs:
                if nbr.in_nbrs.index(self) in nbr.in_channel:
                    nbr.in_channel[nbr.in_nbrs.index(self)].append(msg)
                else:
                    nbr.in_channel[nbr.in_nbrs.index(self)] = [msg]
        else:
            raise Exception("incorrect type for out_nbrs argument of Process.send_msg()")

    def get_msgs(self, in_nbrs = None):
        if in_nbrs is None:
            in_nbrs = self.in_nbrs[:]
        elif isinstance(in_nbrs, Process):
            in_nbrs = [in_nbrs]
        if isinstance(in_nbrs, list):
            msgs = []
            for in_nbr in in_nbrs:
                idx = self.in_nbrs.index(in_nbr)
                if idx in self.in_channel:
                    msgs.extend(self.in_channel[idx])
                    self.in_channel[self.in_nbrs.index(in_nbr)] = []
            return msgs
        else:
            raise Exception("incorrect type for in_nbrs argument of Process.get_msgs()")

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
    def __iter__(self):
        return iter(self.processes)
    def index(self, p):
        return self.processes.index(p)    
    def add(self, algorithm):
        for process in self:
            process.add(algorithm)
    def run(self, algorithm):
        algorithm(self)
    def draw(self):
        import math
        from matplotlib import pyplot as plt
        n = len(self)

        vals = []

        for k in range(n):
            vals.append( [math.cos(2*k*math.pi/n), math.sin(2*k*math.pi/n) ] )
            
            plt.xlim([-1.2, 1.2]) 
            plt.ylim([-1.2, 1.2]) 
        plt.plot( [v[0] for v in vals], [v[1] for v in vals], 'ro' )

        def line(v1, v2):
            plt.plot( (v1[0], v2[0]), (v1[1], v2[1] ))
        for i in range(n):
            for nbr in self[i].out_nbrs:
                line(vals[i], vals[self.index(nbr)])
        frame = plt.gca()
        frame.axes.get_xaxis().set_visible(False)
        frame.axes.get_yaxis().set_visible(False)
        plt.show()
    def print_state(self):
        for process in self:
            print process, process.state
class Algorithm:

    """
    Abstract superclass for a distributed algorithm.

    @param params: Optional run() parameters.
    """
    def __init__(self, 
                 msgs_i, trans_i, halt_i = None, cleanup_i = None,
                 network = None,
                 params = {"draw": False, "silent": False},
                 name = None):

        self.msgs_i = msgs_i
        self.trans_i = trans_i
        
        self.halt_i_ = halt_i
        self.cleanup_i = cleanup_i

        #Algorithm name defaults to X for class X(Algorithm).
        self.name = name
        if name is None:
            self.name = self.__class__.__name__
        if network is not None:
            self(network, params)

        self.message_count = 0

    def halt_i(self, p):
        if self.halt_i_ is not None:
            return self.halt_i_(p)
        return self not in p.algs

    def cleanup(self):
        if self.cleanup_i is not None:
            for process in self.network:
                self.cleanup_i(process)


    def __call__(self, network, params = {}):
        self.run(network, params)

    def run(self, network, params = {"draw":False, "silent":False}):
        self.message_count = 0
        header = "Running " + self.name + " on"
        print len(header)*"-"
        print header
        if params['draw']:
            network.draw()
        print str(network)

    def halt(self):
        if all([self.halt_i(process) for process in self.network]):
            self.halted = True
            print "Algorithm Terminated"
            msg_complexity = "Message Complexity: " + str(self.message_count)
            print msg_complexity
            print "-"*len(msg_complexity)

            self.cleanup()


    def count_msg(self, message_count):
        self.message_count += message_count

class Synchronous_Algorithm(Algorithm):
    """
    We assume that Processes take steps simultaneously,
    that is, that execution proceeds in synchronous rounds.
    """
    def run(self, network, params = {}):
        Algorithm.run(self, network, params)

        self.network = network
        network.add(self)

        self.halted = False
        self.r = 1
        while not self.halted:
            if not params['silent']:
                print "Round "+str(self.r)
            self.round()
            self.halt()
            self.r+=1
    def round(self):
        self.msgs()
        self.trans()
    def msgs(self):
        for process in self.network:
            self.msgs_i(process)
    def trans(self):
        for process in self.network:
            if False:
                print str(process) + " received " + str(process.in_channel)
            self.trans_i(process)

class Asynchronous_Algorithm(Algorithm):
    """
    We assume that the separate Processes take steps
    in an arbitrary order, at arbitrary relative speeds.
    """
    def run(self, network, params = {"draw" : False, "silent" : False}):
        Algorithm.run(self, network, params)

        self.network = network
        network.add(self)

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
    
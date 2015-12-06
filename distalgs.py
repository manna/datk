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
import collections
from collections import defaultdict
from copy import deepcopy

class Message:
    def __init__(self, algorithm, content= None):
        assert isinstance(algorithm, Algorithm), "Message algorithm must be an instance of Algorithm"
        self.content = content
        self.algorithm = algorithm
    def __str__(self):
        return self.__class__.__name__+"("+str(self.content)+")"
    
class Process:
    """A computing element located at a node of a directed network graph.
    Processes are identical except for their UID"""
    def __init__(self, UID, state = None, in_nbrs = [], out_nbrs = []):
        self.UID = UID
        self.state = defaultdict(dict) # algorithm : state dict
        
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

    def output(self, key, val, silent=False):
        self.state[key] =  val
        if not silent:
            print self,"is",val

    def send_to_all_neighbors(self, msg):
        self.send_msg(msg)

    def send_msg(self, msg, out_nbrs=None):
        if out_nbrs is None:
            out_nbrs = self.out_nbrs
        elif isinstance(out_nbrs, Process):
            out_nbrs = [out_nbrs]
        if isinstance(out_nbrs, list):
            msg.algorithm.count_msg(len(out_nbrs))
            for nbr in out_nbrs:
                if nbr.in_nbrs.index(self) in nbr.in_channel:
                    nbr.in_channel[nbr.in_nbrs.index(self)].append(msg)
                else:
                    nbr.in_channel[nbr.in_nbrs.index(self)] = [msg]
        else:
            raise Exception("incorrect type for out_nbrs argument of Process.send_msg()")

    def get_msgs(self, algorithm, in_nbrs = None):
        if in_nbrs is None:
            in_nbrs = self.in_nbrs[:]
        elif isinstance(in_nbrs, Process):
            in_nbrs = [in_nbrs]

        if isinstance(in_nbrs, list):
            msgs = []
            for in_nbr in in_nbrs:
                idx = self.in_nbrs.index(in_nbr)
                if idx in self.in_channel:
                    i = 0
                    while i < len(self.in_channel[idx]):
                        msg = self.in_channel[idx][i]
                        if msg.algorithm == algorithm:
                            self.in_channel[idx].pop(i)
                            msgs.append(msg)
                        else:
                            i+=1
            return msgs
        else:
            raise Exception("incorrect type for in_nbrs argument of Process.get_msgs()")

    def add(self, algorithm):
        self.algs.add(algorithm)
        self.state[algorithm]["diam"] = 10 #TODO Generalize

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
    def state(self):
        return [(str(process), str(process.state)) for process in self]
    def clone(self):
        return deepcopy(self)

class Algorithm:
    """
    Abstract superclass for a distributed algorithm.

    @param params: Optional run() parameters.
    """
    def __init__(self, 
                 network = None,
                 params = {"draw": False, "silent": False},
                 name = None):

        self.params = params
        self.message_count = 0
        #Algorithm name defaults to X for class X(Algorithm).
        self.name = name
        if name is None:
            self.name = self.__class__.__name__
        if network is not None:
            self(network, self.params)

    def msgs_i(self, p): pass
    def trans_i(self, p, msgs): pass
    def halt_i(self, p): return self not in p.algs
    def cleanup_i(self,p): pass

    def cleanup(self):
        for process in self.network:
            self.cleanup_i(process)
            if self in process.state:
                del process.state[self]

    def __call__(self, network, params = {}):
        self.run(network, params)

    def run(self, network, params = {}):
        for param,value in params.items():
            self.params[param] = value

        self.message_count = 0
        header = "Running " + self.name + " on"
        print len(header)*"-"
        print header
        if 'draw' in self.params and self.params['draw']:
            network.draw()
        print str(network)

        self.network = network
        network.add(self)

    def halt(self):
        if all([self.halt_i(process) for process in self.network]):
            self.halted = True
            self.cleanup()

            print "Algorithm Terminated"
            msg_complexity = "Message Complexity: " + str(self.message_count)
            print msg_complexity
            print "-"*len(msg_complexity)

    def count_msg(self, message_count):
        self.message_count += message_count

    def set(self, process, state, value):
        process.state[self][state] = value
    def has(self, process, state):
        return state in process.state[self]
    def get(self, process, state):
        if self.has(process, state):
            return process.state[self][state]
    def delete(self, process, state):
        if self.has(process, state):
            del process.state[self][state]

class Synchronous_Algorithm(Algorithm):
    """
    We assume that Processes take steps simultaneously,
    that is, that execution proceeds in synchronous rounds.
    """
    def run(self, network, params = {}):
        Algorithm.run(self, network, params)
        self.execute()

    def execute(self):
        self.halted = False
        self.r = 0
        while not self.halted:
            self.r+=1
            if not self.params['silent']:
                print "Round",self.r
            self.round()
            self.halt()

    def round(self):
        self.msgs()
        self.trans()
    def msgs(self):
        for process in self.network:
            self.msgs_i(process)
    def trans(self):
        for process in self.network:
            if False: #if maximum verbosity setting
                print process,"received",process.in_channel
            messages = process.get_msgs(self)
            self.trans_i(process, messages)

class Do_Nothing(Synchronous_Algorithm):
    def trans_i(self, p, messages): p.terminate(self)
    
class Asynchronous_Algorithm(Algorithm):
    """
    We assume that the separate Processes take steps
    in an arbitrary order, at arbitrary relative speeds.
    """
    def run(self, network, params = {}):
        Algorithm.run(self, network, params=params)

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
    
class Compose(Synchronous_Algorithm):
    """
    A Synchonous_Algorithm that is the composition of two synchronous algorithms
    running in parallel.
    """
    def __init__(self, A, B, name = None, params = {"draw": False, "silent": False}):
        assert isinstance(A,Synchronous_Algorithm), "Not a Synchronous_Algorithm"
        assert isinstance(B,Synchronous_Algorithm), "Not a Synchronous_Algorithm"
        self.A=A
        self.B=B
        self.message_count = 0
        self.params = params
        if name is None:
            name = self.name="Compose("+self.A.name+","+self.B.name+")"

    def msgs_i(self, p):
        self.A.msgs_i(p)
        self.B.msgs_i(p)

    def trans_i(self, p, msgs):
        self.A.trans_i(p, p.get_msgs(self.A))
        self.B.trans_i(p, p.get_msgs(self.B))

    def halt_i(self, p):
        self.message_count = self.A.message_count + self.B.message_count

        return self.A.halt_i(p) and self.B.halt_i(p)

    def cleanup_i(self, p):
        self.message_count = self.A.message_count + self.B.message_count
        self.A.cleanup_i(p)
        self.B.cleanup_i(p)
        p.terminate(self)

    def run(self, network, params = {}):
        Algorithm.run(self, network, params)
        self.network.add(self.A)
        self.network.add(self.B)
        self.execute()
    
    def __repr__(self): return self.name

class Chain(Algorithm):
    """
    An Algorithm that is the result of sequentially running two algorithms
    """
    def __init__(self, A, B, name = None, params = {"draw": False, "silent": False}):
        assert isinstance(A,Algorithm), "Not an Algorithm"
        assert isinstance(B,Algorithm), "Not an Algorithm"
        self.params = params
        self.A = A
        self.B = B
        
        self.name = name or "Chain(" + A.name+","+B.name+")"

    def run(self, network, params = {}):
        Algorithm.run(self, network, params)
        self.A.run(network, params=params)
        self.B.run(network, params=params)
        self.message_count = self.A.message_count + self.B.message_count
        self.halt()

    def __repr__(self): return self.name

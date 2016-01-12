import random
from random import shuffle
from time import sleep
import pdb
import collections
from collections import defaultdict
from copy import deepcopy
import numpy as np
from scipy.linalg import eig
import math
from matplotlib import pyplot as plt

from helpers import memoize

class Message:
    """
    A Message

    Attributes:
        - content: The content of this Message
        - algorithm: The Algorithm that required the sending of this Message
        - author: The Process that sent it
    """
    def __init__(self, algorithm, content= None):
        """
        @param algorithm: the Algorithm that required the sending of this Message
        @param content: The content of this Message. Can be any type, including None.
        """
        assert isinstance(algorithm, Algorithm), "Message algorithm must be an instance of Algorithm"
        self.content = content
        self.algorithm = algorithm
        self.author = None

    def __str__(self):
        return self.__class__.__name__+"("+str(self.content)+")"
    

class Process:
    """A computing element located at a node of a network graph.
    Processes are identical except for their UID"""
    def __init__(self, UID, state = None, in_nbrs = [], out_nbrs = []):
        self.UID = UID
        self.state = defaultdict(dict) # algorithm : state dict
        
        self.in_nbrs = in_nbrs or []   # Don't remove or []
        self.out_nbrs = out_nbrs or [] # Don't remove or []

        self.in_channel = {}
        self.algs = set()

    def link_to(self, new_out_nbr):
        """Adds a new outgoing neighbor of the Process"""
        if new_out_nbr not in self.out_nbrs:
            self.out_nbrs.append(new_out_nbr)
        if self not in new_out_nbr.in_nbrs:
            new_out_nbr.in_nbrs.append(self)

    def bi_link(self, nbr):
        """Adds a new out_nbr of the Process, and adds the
        Process as an out_nbr of that neighbor"""
        self.link_to(nbr)
        nbr.link_to(self)

    def output(self, key, val, verbose=True):
        """
        Sets the publicly visible value of self.state[key] to val

        @param key: The state variable to set
        @param val: The value to assign to it
        @param verbose: Dictates whether or not to print this event to STDOUT
        """
        self.state[key] =  val
        if verbose:
            if isinstance(val, list):
                print str(self)+"."+str(key), "are", [str(v) for v in val]
            else: 
                print str(self)+"."+str(key),"is", val

    def send_to_all_neighbors(self, msg):
        """Sends a message to all out_nbrs

        @param msg: the message to send
        """
        self.send_msg(msg)

    def send_msg(self, msg, out_nbrs=None):
        """
        Sends a Message from Process to some subset of out_nbrs

        @param msg: The message to send.
        @param out_nbrs: The out_nbrs to send the message to. This may be a
        subset of the Process's out_nbrs, or None, in which case the message
        will be sent to all out_nbrs

        Effects:
            - Sets msg.author = self
        """
        msg.author = self
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
        """Removes all Messages that relate to a particular Algorithm from the Process'
        incoming channels (or from some subset of incoming channels). Returns them.

        @param algorithm: the algorithm whose messages this returns
        @param in_nbrs: the in_nbrs of the Process from whose channels we are getting
        messages. If None, fetches messages from all channels
        @return: A list of Messages, msgs, such that every message in msgs has Algorithm
        algorithm, and author in in_nbrs
        """
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
        """Causes the Process to wake up with respect to algorithm"""
        self.algs.add(algorithm)
        self.state[algorithm]["diam"] = self.state['n']

    def terminate(self, algorithm):
        """Causes the Process to halt execution of algorithm"""
        if algorithm in self.algs:
            self.algs.remove(algorithm)

    def __str__(self):
        return "P"+str(self.UID)

    def __repr__(self):
        return "P" + str(self.UID) + " -> {"+", ".join([str(process) for process in self.out_nbrs]) + "}" 


class Network:
    """ A collection of Processes that know n, the # of processes in the network."""
    
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
        for process in self:
            process.state['n'] = n
    
    def add(self, algorithm):
        """Awakens all Processes in the Network with respect to algorithm"""
        for process in self:
            process.add(algorithm)
    
    def run(self, algorithm):
        """Runs algorithm on the Network"""
        algorithm(self)
    
    def draw(self, style='spectral'):
        """
        Draws the network

        @param style:
            - 'spectral' draws graph in a spectral graph layout
                - http://www.math.ucsd.edu/~fan/research/cb/ch1.pdf
                - http://www.research.att.com/export/sites/att_labs/groups/infovis/res/legacy_papers/DBLP-journals-camwa-Koren05.pdf
            - 'circular' draws graph in a circular layout
        """
        if style == 'spectral':
            n = len(self)
            L = self._laplacian()
            D = np.diag(self.degrees())
            w, v = eig(L, D)
            v = v.T

            idx = w.argsort()
            v = v[idx]
            x_vals, y_vals = v[1], v[2]
            vals = zip(x_vals, y_vals)

        if style == 'circular':
            n = len(self)
            vals = []
            for k in range(n):
                vals.append( [math.cos(2*k*math.pi/n), math.sin(2*k*math.pi/n) ] )

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
        """
        @return: A text representation of the state of all the Processes in the Network 
        """
        return [(str(process), dict(process.state)) for process in self]
    
    def clone(self):
        return deepcopy(self)

    # @memoize
    def adjacency_matrix(self):
        """
        Returns the (symmetric) n,n adjacency matrix of the undirected graph that
        has a vertex for every Process of this network, and an edge between
        vertices i and j, if Process self[i] is an in_nbr or out_nbr of Process
        self[j].

        Memoized because Networks are assumed to be static.

        @return: Matrix, A, such that A[i][j] = 1
        if self[i] is an in_nbr or out_nbr of self[j], else 0.
        """
        A = np.zeros(shape=(len(self), len(self)))
        for i in xrange(len(self)):
            i_nbrs = set(self[i].in_nbrs+self[i].out_nbrs)
            for j in xrange(len(self)):
                if self[j] in i_nbrs:
                    A[i][j] = 1.
        return A

    def adjacent(self, i, j):
        """
        Checks whether the processes at index i and j are linked

        Alternately, checks if Processes i and j are linked.

        @return: True iff Processes self[i] (or i) and self[j] (or j) are adjacent
        """
        if isinstance(i, Process) and isinstance(j, Process):
            i, j = self.index(i), self.index(j)
        assert isinstance(i, int) and isinstance(j, int), "i and j must be integer Process indices"

        return self.adjacency_matrix()[i][j]==1
    
    # @memoize
    def degrees(self):
        """
        @return: the size n array containing the degree of each process, ordered by index.
        """
        A = self.adjacency_matrix()
        D = np.zeros(shape=(len(self),))

        for i in xrange(len(self)):
            D[i] = sum(A[i])

        return D

    def degree(self, p):
        """Returns the number of other Processes Process p is connected to.

        Alternately, if p is an integer in 0..n-1, returns the degree of Process self[p]
        """
        if isinstance(p, Process):
            p = self.index(p)
        assert isinstance(p, int) and p>=0 and p<len(self), "p must be a Process or an integer Process index"
        return self.degrees()[p]

    # @memoize
    def _laplacian(self):
        """
        @return: the Laplacian, L. A symmetric n,n matrix associated with the graph,
        where L[i][j] = deg(i) if i = j, -1 if adjacent(i,j), and 0 otherwise
        """
        D = np.diag(self.degrees())
        L = np.zeros(shape=(len(self), len(self)))
        
        for i in xrange(len(self)):
            for j in xrange(len(self)):
                if i == j:
                    L[i][j] = D[i][i]
                elif self.adjacent(i,j):
                    L[i][j] = -1. #-w_{i,j}/ in a weighted graph
        
        return L

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
    

class Algorithm:
    """Abstract superclass for a distributed algorithm."""

    """Verbosity levels
    
    Random updates >= VERBOSE
    Process outputs >= DEFAULT
    Algorithm results >= QUIET
    SILENT : No output whatsoever
    """
    SILENT, QUIET, DEFAULT, VERBOSE = 0, 1, 2, 3

    """Default initialization of self.params"""
    DEFAULT_PARAMS = {'draw' : False, 'verbosity': DEFAULT}

    def __init__(self, network = None, params = {}, name = None):
        """
        @param network: [Optional] network. If specified, algorithm is immediately executed on network.
        @param params: [Optional] runtime parameters.
        @param name: [Optional] name of the Algorithm instance. Defaults to class name.
        """
        self.params = deepcopy(Algorithm.DEFAULT_PARAMS)
        self.params.update(params)
        self.message_count = 0

        self.name = name
        if name is None:
            self.name = self.__class__.__name__
        if network is not None:
            self(network, self.params)

    def msgs_i(self, p):
        """Determines what messages a Process, p, will send."""
        pass
    
    def trans_i(self, p, msgs):
        """Determines what state transition a Process, p, will perform,
        having received messages, msgs"""
        pass
    
    def halt_i(self, p):
        """Returns True iff Process p has halted execution of the algorithm"""
        return self not in p.algs
    
    def cleanup_i(self,p):
        """Determines what final state transition a Process, p, will perform,
        after the algorithm terminates."""
        pass

    def cleanup(self):
        """Calls cleanup_i on all processes"""
        for process in self.network:
            self.cleanup_i(process)
            if self in process.state:
                del process.state[self]

    def __call__(self, network, params = {}):
        """Same as run, allows an algorithm, A, to be executed like this: A()"""
        self.run(network, params)

    def run(self, network, params = {}):
        """
        Executes the algorithm on the network

        @param network: the parameter to run in
        @param params: runtime parameters
        """
        for param,value in params.items():
            self.params[param] = value

        self.message_count = 0
        if self.params['verbosity'] >= Algorithm.DEFAULT:
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
            if self.params['verbosity'] >= Algorithm.QUIET:
                self.print_algorithm_terminated()

    def print_algorithm_terminated(self):
        print self.name+" Terminated"
        msg_complexity = "Message Complexity: " + str(self.message_count)
        print msg_complexity
        print "-"*len(msg_complexity)

    def count_msg(self, message_count):
        self.message_count += message_count

    def set(self, process, state, value):
        process.state[self][state] = value
    
    def increment(self, process, state, inc=1):
        process.state[self][state] += inc
    
    def has(self, process, state):
        return state in process.state[self]
    
    def get(self, process, state):
        if self.has(process, state):
            return process.state[self][state]
    
    def delete(self, process, state):
        if self.has(process, state):
            del process.state[self][state]
    
    def output(self, process, key, val):
        """
        Sets the publicly visible value of process.state[key] to val

        This command is verbose if Algorithm's verbosity is >= DEFAULT

        @param key: The state variable to set
        @param val: The value to assign to it
        """
        process.output(key, val, self.params['verbosity'] >= Algorithm.DEFAULT)


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
            if self.params['verbosity'] >= Algorithm.DEFAULT:
                print "Round",self.r
            self.round()
            self.halt()

    def round(self):
        """Executes a single round of the Synchronous Algorithm"""
        self.msgs()
        self.trans()
    
    def msgs(self):
        for process in self.network:
            if self.halt_i(process): continue
            self.msgs_i(process)
    
    def trans(self):
        for process in self.network:
            if self.halt_i(process): continue
            try: #Checks if function trans_i(self, p) is defined
                self.trans_i(process)
            except TypeError: #Otherwise, tries function trans_i(self, p, msgs)
                self.trans_i(process, process.get_msgs(self))
    
    def print_algorithm_terminated(self):
        print self.name+" Terminated"
        msg_complexity = "Message Complexity: " + str(self.message_count)
        print msg_complexity
        time_complexity = "Time Complexity: " + str(self.r)
        print time_complexity
        print "-"*len(time_complexity)


class Do_Nothing(Synchronous_Algorithm):
    def trans_i(self, p, messages): p.terminate(self)

    
class Asynchronous_Algorithm(Algorithm):
    """
    We assume that the separate Processes take steps
    in an arbitrary order, at arbitrary relative speeds.
    """

    def run(self, network, params = {}):
        Algorithm.run(self, network, params=params)
        self.execute()

    def execute(self):
        halted_processes = set()
        msg_enabled = set(self.network.processes)
        trans_enabled = set()

        def halt_process(process):
            halted_processes.add(process)
            try:
                msg_enabled.remove(process)
            except KeyError:
                pass
            try:
                trans_enabled.remove(process)
            except KeyError:
                pass

        def trans_process(process, self):
            if process not in halted_processes:
                try: #Checks if function trans_i(self, p) is defined
                    self.trans_i(process)
                except TypeError: #Otherwise, tries function trans_i(self, p, msgs)
                    self.trans_i(process, process.get_msgs(self))

                trans_enabled.remove(process)
                msg_enabled.add(process)

                # Uncomment this to allow message sending during self.trans_i
                # Warning: Causes significant slowdown
                # for nbr in process.out_nbrs:
                #     if nbr not in halted_processes:
                #         trans_enabled.add(nbr)

                if self.halt_i(process):
                    halt_process(process)            

        def msg_process(process, self):
            if process not in halted_processes:
                self.msgs_i(process)

                msg_enabled.remove(process)                
                for nbr in process.out_nbrs:
                    if nbr not in halted_processes:
                        trans_enabled.add(nbr)

                if self.halt_i(process):
                    halt_process(process)

        self.halted=False
        # while len(halted_processes) < len(self.network.processes):
        while not self.halted:
            if msg_enabled or trans_enabled:
                r = random.randrange(len(msg_enabled) + len(trans_enabled))
                if r < len(msg_enabled):
                    msg_process(list(msg_enabled)[r], self)
                else:
                    trans_process(list(trans_enabled)[r-len(msg_enabled)], self)
            else:
                raise Exception("No enabled actions, but not all processes halted")
            self.halt()
        
    
class Compose(Synchronous_Algorithm):
    """
    A Synchonous_Algorithm that is the composition of two synchronous algorithms
    running in parallel.
    """
    
    def __init__(self, A, B, name = None, params = None):
        """
        @param A: an instance of Synchronous_Algorithm
        @param B: an instance of Synchronous_Algorithm
        @param name: [Optional] name of the Algorithm. Defaults to Compose(name of A, name of B)
        @param params: [Optional] Runtime parameters
        """
        assert isinstance(A,Synchronous_Algorithm), "Not a Synchronous_Algorithm"
        assert isinstance(B,Synchronous_Algorithm), "Not a Synchronous_Algorithm"
        self.A=A
        self.B=B
        self.message_count = 0
        self.params = params or deepcopy(Algorithm.DEFAULT_PARAMS)
        if name is None:
            name = self.name="Compose("+self.A.name+","+self.B.name+")"

    def msgs_i(self, p):
        self.A.r, self.B.r = self.r, self.r
        self.A.msgs_i(p)
        self.B.msgs_i(p)

    def trans_i(self, p, msgs):
        self.A.r, self.B.r = self.r, self.r
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

    def __init__(self, A, B, name = None, params = None):
        """
        @param A: an instance of Algorithm
        @param B: an instance of Algorithm
        @param name: [Optional] name of the Algorithm. Defaults to Chain(A.name, B.name)
        @param params: [Optional] Runtime parameters
        """
        assert isinstance(A,Algorithm), "Not an Algorithm"
        assert isinstance(B,Algorithm), "Not an Algorithm"
        self.params = params or deepcopy(Algorithm.DEFAULT_PARAMS)
        self.A = A
        self.B = B
        
        self.name = name or "Chain(" + A.name+","+B.name+")"

    def run(self, network, params = {}):
        Algorithm.run(self, network, params)
        self.A.run(network, params=self.params)
        self.B.run(network, params=self.params)
        self.message_count = self.A.message_count + self.B.message_count
        self.halt()
        Algorithm.cleanup(self)

    def __repr__(self): return self.name

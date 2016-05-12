from distalgs import *

#Leader Election Algorithms for Ring networks:

class LCR(Synchronous_Algorithm):
    """The LeLann, Chang and Roberts algorithm for Leader Election in a Synchronous Ring Network 
    
    Each Process sends its identifier around the ring.
    When a Process receives an incoming identifier, it compares that identifier to its own.
    If the incoming identifier is greater than its own, it keeps passing the identifier;
    if it is less than its own, it discards the incoming identifier;
    if it is equal to its own, the Process declares itself the leader.

    Requires:
        - Every process knows state['n'], the size of the network
    Effects:
        - Every process has state['status'] is 'leader' or 'non-leader'.
        - Exactly one process has state['status'] is 'leader'
    """
    def msgs_i(self, p):
        if not self.has(p, "send"):
            self.set(p, 'send', Message(self, p.UID))

        msg = self.get(p, "send")
        if msg is None:
            return
        self.set(p,"send", None)
        p.send_msg(msg, p.out_nbrs[-1])

    def trans_i(self, p, msgs):
        if len(msgs) == 0:
            self.set(p,"send", None)
        else:
            msg = msgs.pop()
            if msg.content == p.UID:
                self.output(p,"status", "leader")
            elif msg.content > p.UID:
                self.set(p,"send", msg)
                if not self.has(p, "decided"):
                    self.set(p, "decided", None)
                    self.output(p,"status", "non-leader")
            else:
                self.set(p, "send",  None)
        if self.r == p.state['n']: p.terminate(self)

class AsyncLCR(Asynchronous_Algorithm):
    """The LeLann, Chang and Roberts algorithm for Leader Election in an Asynchronous Ring Network 
    
    Each Process sends its identifier around the ring.
    When a Process receives incoming identifier(s), it compares their largest to its own.
    If that incoming identifier is greater than its own, it keeps passing that identifier;
    if it is less than its own, it discards all the incoming identifiers;
    if it is equal to its own, the Process declares itself the leader.
    When a Process has declared itself Leader, it sends a Leader Declaration message around the ring, and halts
    As it goes around the ring, each other Process outputs 'non-leader', and halts.

    Requires:
        - Every process knows state['n'], the size of the network
    Effects:
        - Every process has state['status'] is 'leader' or 'non-leader'.
        - Exactly one process has state['status'] is 'leader'
    """
    class Leader_Declaration(Message): pass
    def msgs_i(self, p, verbose=False):
        if not self.has(p, "sends"):
            self.set(p, "sends",  [Message(self, p.UID)])

        if p.state["status"] == "leader":
            msg = AsyncLCR.Leader_Declaration(self)
            p.send_msg(msg, p.out_nbrs[-1])
            if verbose:
                print p,"sends",msg
            p.terminate(self)
            return
        while len(self.get(p, "sends")) > 0:
            msg = self.get(p, "sends").pop()
            p.send_msg(msg, p.out_nbrs[-1])
            if verbose:
                print p,"sends",msg
            if self.has(p, "terminate_after_send"):
                p.terminate(self)

    def trans_i(self, p, verbose=False):
        msgs = p.get_msgs(self)
        if self.get(p, 'sends') is None:
            self.set(p, 'sends', [Message(self, p.UID)])
        
        if verbose:
            print str(p) + " received " + str(p.in_channel)
        while len(msgs) > 0:
            msg = msgs.pop()
            if isinstance(msg, AsyncLCR.Leader_Declaration):
                self.get(p, "sends").append(msg)
                self.set(p, "terminate_after_send", None)
                return
            elif msg.content == p.UID:
                self.output(p,"status", "leader")
            elif msg.content > p.UID:
                self.get(p, "sends").append(msg)
                if not self.has(p, 'decided'):
                    self.set(p, 'decided', None)
                    self.output(p,"status", "non-leader")

#Leader Election Algorithms for general Networks:

class FloodMax(Synchronous_Algorithm):
    """
    UID flooding algorithm for Leader Election in a general network

    Every process maintains a record of the maximum UID it has seen so far
    (initially its own). At each round, each process propagates this maximum
    on all of its outgoing edges. After diam rounds, if the maximum value seen
    is the process's own UID, the process elects itself the leader; otherwise,
    it is a non-leader.

    Requires:
        - Every process, p, has p.state["diam"] >= dist( p, q ), forall q.
        - Alternatively, a process that does not know state["diam"] will use 
        state["n"], the size of the network, as a fallback upper bound on diam.
    """
    def msgs_i(self,p):
        if self.r < self.get(p, "diam"):
            if not self.has(p, "send"):
                self.set(p, "send",  Message(self, p.UID))
            p.send_msg(self.get(p, "send"))

    def trans_i(self, p, msgs, verbose=False):
        if verbose:
            print p, "received", p.in_channel
        seen_uids = msgs + [self.get(p, "send")]
        self.set(p, "send",  max(seen_uids, key = lambda m: m.content))

        if self.r == self.get(p, 'diam'):
            if self.get(p, "send").content == p.UID:
                self.output(p,"status", "leader")
                p.terminate(self)
            else:
                self.output(p,"status", "non-leader")
                p.terminate(self)
   
#Construct BFS Tree

class SynchBFS(Synchronous_Algorithm):
    """Constructs a BFS tree with the 'leader' Process at its root

    At any point during execution, there is some set of processes that is
    "marked," initially just i0. Process i0 sends out a search message at
    round 1, to all of its outgoing neighbors. At any round, if an unmarked
    process receives a search message, it marks itself and chooses one of the
    processes from which the search has arrived as its parent. At the first
    round after a process gets marked, it sends a search message to all of its
    outgoing neighbors.

    Requires:
        - testLeaderElection
    Effects:
        - every Process has state['parent']. Leader has state['parent'] = None
    """
    class Search(Message):
        """Search for children"""
        pass
    
    def is_i0(self, p): return p.state["status"] == "leader"

    def msgs_i(self, p):
        if self.is_i0(p) and self.r == 1:
            self.output(p,"parent",  None)
            p.send_msg(SynchBFS.Search(self, p))
        if self.has(p, "recently_marked"):
            p.send_msg(SynchBFS.Search(self, p))
            self.delete(p, "recently_marked")
    def trans_i(self, p, msgs):
        if len(msgs)> 0:
            if "parent" not in p.state:
                self.output(p,"parent",  msgs[0].content)
                self.set(p, "recently_marked",  True)
                return
        if "parent" in p.state:
            if self.has(p, "recently_marked"): self.delete(p, "recently_marked")
            p.terminate(self)

class SynchBFSAck(Synchronous_Algorithm):
    """Constructs a BFS tree with children pointers and the 'leader' Process at its root

    Algorithm (Informal):
    At any point during execution, there is some set of processes that is
    "marked," initially just i0. Process i0 sends out a search message at
    round 1, to all of its outgoing neighbors. At any round, if an unmarked
    process receives a search message, it marks itself and chooses one of the
    processes from which the search arrived as its parent. At the first
    round after a process gets marked, it sends a search message to all of its
    outgoing neighbors, and an acknowledgement to its parent, so that nodes
    will also know their children.

    Requires:
        - testLeaderElection
    Effects: 
        - Every process knows:
            - state['parent']. Leader has state['parent'] = None
            - state['childen']. Leaves have state['children'] = []
    """
    class Search(Message):
        """Search for children"""
        pass
    class AckParent(Message):
        """Acknowledge Parent"""
        pass

    def is_i0(self, p): return p.state["status"] == "leader"

    def msgs_i(self, p):
        if self.is_i0(p) and self.r == 1:
            self.output(p, "parent",  None)
            self.set(p, "recently_marked",  True)
            p.send_msg(SynchBFSAck.Search(self, p))
        elif self.has(p, "recently_marked"):
            p.send_msg(SynchBFSAck.Search(self, p))
            p.send_msg(SynchBFSAck.AckParent(self, p), p.state['parent'] )
            if self.params["verbosity"]>=Algorithm.VERBOSE:
                print p,"ack", p.state['parent']
    def trans_i(self, p, msgs):
        search_msgs = [m.content for m in msgs if isinstance(m, SynchBFSAck.Search)]
        ack_msgs = [m.content for m in msgs if isinstance(m, SynchBFSAck.AckParent)]

        if 'parent' not in p.state:
            if len(search_msgs)> 0:
                self.output(p, "parent",  search_msgs[0])
                self.set(p, "recently_marked",  True)
                if self.params["verbosity"]>=Algorithm.VERBOSE:
                    print str(p), "chooses parent"
        else:
            if self.has(p, "recently_marked"):
                self.delete(p, "recently_marked")
            elif "children" not in p.state:
                self.output(p,"children",  ack_msgs)
                p.terminate(self)
                if self.params["verbosity"]>=Algorithm.VERBOSE:
                    print p,"knows children"

#Convergecast

class SynchConvergecast(Synchronous_Algorithm):
    """The abstract superclass of a class of Synchronous Algorithms that
    propagate information from the leaves of a BFS tree to its root.

    Requires:
        - Every Process knows state['parent']
    """
    #TODO If Processes also know state['children'] ==> Reduced Communication Complexity.
    def is_root(self, p): return p.state['parent'] is None
    def msgs_i(self, p):
        if not self.is_root(p):
            if self.r == 1:
                self.set(p, 'send',  self.initial_msg_to_parent(p))
            if self.get(p, 'send') is not None:
                p.send_msg(self.get(p, 'send'), p.state['parent'])
                self.set(p, 'send',  None)
    def trans_i(self, p, msgs):
        msgs = [m.content for m in msgs]
        if self.is_root(p):
            if len (msgs) > 0:
                self.trans_root(p, msgs) 
            else:
                self.output_root(p)
                p.terminate(self)
        else:
            if len (msgs) > 0:
                self.set(p, 'send', self.trans_msg_to_parent(p, msgs) )
            else:
                p.terminate(self)
    def trans_root(self, p, msgs):          pass
    def output_root(self, p):               pass
    def initial_msg_to_parent(self, p):     return
    def trans_msg_to_parent(self, p, msgs): return

class AsynchConvergecast(Asynchronous_Algorithm):
    """The abstract superclass of a class of Asynchronous Algorithms that
    propagate information from the leaves of a BFS tree to its root.

    Requires:
        - Every Process knows state['parent'] and state['children']"""
    def is_root(self, p): return p.state['parent'] is None
    def msgs_i(self, p):
        if not self.has(p, 'reports'):
            self.set(p, 'reports', [])
        if len(p.state['children']) == 0:
            p.send_msg(self.initial_msg_to_parent(p), p.state['parent'])
            p.terminate(self)
        elif self.has(p, 'send'):
            p.send_msg(self.get(p, 'send'), p.state['parent'])
            p.terminate(self)

    def trans_i(self, p, msgs):
        msgs = [m.content for m in msgs]
        if not self.has(p, 'reports'):
            self.set(p, 'reports', [])
        self.increment(p,'reports', msgs)
        if len(p.state['children']) == len(self.get(p, 'reports')):
            if self.is_root(p):
                self.trans_root(p, self.get(p, 'reports'))
                self.output_root(p)
                p.terminate(self)
            elif len(p.state['children']) != 0:
                trans_msg = self.trans_msg_to_parent(p, self.get(p, 'reports'))
                self.set(p, 'send', trans_msg)

    def trans_root(self, p, msgs):
        """Determines the state transition the root node should undergo
        when it receives messages

        @param p: the root Process
        @param msgs: the messages received by the root Process, from its BFS children
        """
        pass
    def output_root(self, p):
        """Determines the output action, if any, that the root should perform
        at the end of the Convergecast.
        """
        pass
    def initial_msg_to_parent(self, p):
        """Defines the initial message sent from a leaf process to its parent at the
        beginning of the Convergecast

        @param p: A Process at a leaf of the BFS tree
        @return: the Message p should send to its state['parent']
        """
        return
    def trans_msg_to_parent(self, p, msgs):
        """Defines the message a non-leaf, non-root Process should send to its parent
        when it has received all its children's messages

        @param p: a Process that has both p.state['parent'] != null, and p.state['children'] not empty
        @param msgs: A list of messages from every child of p (in p.state['children']) 
        @return: the Message p should send to its state['parent']
        """
        return

def _converge_height(Convergecast, name):
    class _ConvergeHeight(Convergecast):
        """
        A Convergecast Algorithm that results in the root node, p, knowing
        p.state['height'], the height of the tree rooted at p.

        Requires:
            - BFS Tree
        Effects:
            - Root Process knows height of tree in state["height"]
        """
        def trans_root(self, p, msgs):      #Updates height
            self.set(p, 'height', max(msgs))
        def output_root(self, p):           #Decides height
            self.output(p,'height', self.get(p, 'height')) 
        def initial_msg_to_parent(self, p):
            return Message(self, 1)
        def trans_msg_to_parent(self, p, msgs):
            return Message(self, 1 + max(msgs))
    _ConvergeHeight.__name__ = name
    return _ConvergeHeight

SynchConvergeHeight = _converge_height(SynchConvergecast, "SynchConvergeHeight")
AsynchConvergeHeight = _converge_height(AsynchConvergecast, "AsynchConvergeHeight")

#Broadcast
class SynchBroadcast(Synchronous_Algorithm):
    """Broadcasts a value stored in Process, p, to the BFS tree rooted at p

    Requires:
        - The attribute to be broadcasted must be specified in self.params['attr']
        - BFS Tree with children pointers, where root node has state[self.params['attr']]
    Effects:
        - All Processes have state[self.params['attr']] := the original value of in
        state[self.params['attr']] of the root Process.

    For example: If the root Process, p, knows p.state['min_UID'] = 4. Then after the
    execution, all Processes q in the Network know q.state['min_UID'].
    """
    def msgs_i(self, p):
        attr = self.params['attr']
        if p.state['parent'] is None:
            if self.r == 1:
                p.send_msg(Message(self, p.state[attr]), p.state['children']) 
        if p.state['parent'] is not None:
            if self.get(p, 'send') is not None:
                p.send_msg(Message(self,self.get(p, 'send')), p.state['children'])
                self.set(p, 'send',  None)
                p.terminate(self)
    def trans_i(self, p, msgs):
        msgs = [m.content for m in msgs]
        attr = self.params['attr']
        if p.state['parent'] is None:
            p.terminate(self)
        else:
            if len (msgs) == 1:
                self.output(p,attr,  msgs[0])
                if len(p.state['children']) > 0:
                    self.set(p, 'send',  msgs[0])
                else:
                    p.terminate(self)

#Maximal Independent Set
class SynchLubyMIS(Synchronous_Algorithm):
    """A randomized algorithm that constructs a Maximal Independent Set
    
    The algorithm works in stages, each consisting of three rounds.
    
        - Round 1: In the first round of a stage, the processes choose their
        respective vals and send them to their neighbors. By the end of round
        1, when all the val messages have been received, the winners--that is,
        the processes in F--know who they are.
        - Round 2: In the second round, the winners notify their neighbors. By
        the end of round 2, the losers--that is, the processes having neighbors
        in F--know who they are.
        - Round 3: In the third round, each loser notifies its neighbors. Then
        all the involved processes--the winners, the losers, and the losers'
        neighbors-- remove the appropriate nodes and edges from the graph. More
        precisely, this means the winners and losers discontinue participation
        after this stage, and the losers' neighbors remove all the edges that
        are incident on the newly removed nodes.

    Requires:
        - Every process knows state['n'], the size of the network
    Effect:
        - Every process knows state['MIS']. A boolean representing whether it
        is a member of the Maximal Independent Set found by Luby's algorithm.
    """
    def msgs_i(self, p):
        if self.r == 1:
            self.set(p, 'rem_nbrs', p.out_nbrs[:])
            self.set(p, 'status', 'unknown')

        if self.r%3 == 1: 
            self.set(p, 'val', random.randint(0,p.state['n'] **4 ))
            p.send_msg( Message(self, self.get(p, 'val')), self.get(p, 'rem_nbrs') )
        if self.r%3 == 2:
            if self.get(p, 'status') == 'winner':
                p.send_msg( Message(self, 'winner') , self.get(p, 'rem_nbrs') )
        if self.r%3 == 0:
             if self.get(p, 'status') == 'loser':
                p.send_msg( Message(self, 'loser') , self.get(p, 'rem_nbrs') )           
    def trans_i(self, p, msgs):
        values = [m.content for m in msgs]
        if self.r%3 ==1:
            if len(values) == 0 or self.get(p, 'val') > max(values):
                self.set(p, 'status', 'winner')
                self.output(p, 'MIS', True)
        if self.r%3 ==2:
            if 'winner' in values:
                self.set(p, 'status', 'loser')
                self.output(p,'MIS', False)
        if self.r%3 == 0:
            rem_nbrs = self.get(p, 'rem_nbrs')
            for m in msgs:
                if m.content == 'loser':
                    rem_nbrs.remove(m.author)
            self.set(p, 'rem_nbrs', rem_nbrs)
            if self.get(p, 'status') in ['winner', 'loser']:
                p.terminate(self)

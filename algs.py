from distalgs import *

#Leader Election Algorithms for Ring networks:

class LCR(Synchronous_Algorithm):
    """
    The LeLann, Chang and Roberts algorithm for Leader Election in a Synchronous Unidirectional_Ring. 
    
    Each Process sends its identifier around the ring.
    When a Process receives an incoming identifier, it compares that identifier to its own.
    If the incoming identifier is greater than its own, it keeps passing the identifier;
    if it is less than its own, it discards the incoming identifier;
    if it is equal to its own, the Process declares itself the leader.

    Requires:
        Every process knows n, the size of the network
    Effects:
        Every process has state['status'] is 'leader' or 'non-leader'.
        Exactly one process has state['status'] is 'leader'
    """
    def msgs_i(self, p):
        if not self.has(p, "send"):
            self.set(p, 'send', Message(self, p.UID))

        msg = self.get(p, "send")
        if msg is None:
            return
        self.set(p,"send", None)
        p.send_msg(msg, p.out_nbrs[-1])

    def trans_i(self, p, msgs): #TODO replace params['silent'] with verbosity levels.
        if len(msgs) == 0:
            self.set(p,"send", None)
        else:
            msg = msgs.pop()
            if msg.content == p.UID:
                p.output("status", "leader", self.params["silent"])
            elif msg.content > p.UID:
                self.set(p,"send", msg)
                p.output("status", "non-leader", self.params["silent"])
            else:
                self.set(p, "send",  None)
        if self.r == p.state['n']: p.terminate(self)
    
    def cleanup_i(self, p): self.delete(p, 'send')

class AsyncLCR(Asynchronous_Algorithm):
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

    def trans_i(self, p, verbose=False):
        msgs = p.get_msgs(self)
        if verbose:
            print str(p) + " received " + str(p.in_channel)
        while len(msgs) > 0:
            msg = msgs.pop()
            if isinstance(msg, AsyncLCR.Leader_Declaration):
                p.send_msg(msg, p.out_nbrs[-1])
                if verbose:
                    print p,"sends",msg
                p.terminate(self)
                return
            elif msg.content == p.UID:
                p.output("status", "leader", self.params["silent"])
            elif msg.content > p.UID:
                self.get(p, "sends").append(msg)
                p.output("status", "non-leader", self.params["silent"])

    def cleanup_i(self, p): self.delete(p, 'sends')

#Leader Election Algorithms for general Networks:

class FloodMax(Synchronous_Algorithm):
    """
    Every process maintains a record of the maximum UID it has seen so far
    (initially its own). At each round, each process propagates this maximum
    on all of its outgoing edges. After diam rounds, if the maximum value seen
    is the process's own UID, the process elects itself the leader; otherwise,
    it is a non-leader.

    Precondition: for every process, p, self.get(p, "diam") >= dist( p, q ), forall q.
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

        if self.r == self.get(p, "diam"):
            if self.get(p, "send").content == p.UID:
                p.output("status", "leader", self.params["silent"])
                p.terminate(self)
            else:
                p.output("status", "non-leader", self.params["silent"])
                p.terminate(self)

    def cleanup_i(self,p): self.delete(p, 'send')
   
#Construct BFS Tree

class SynchBFS(Synchronous_Algorithm):
    """
    At any point during execution, there is some set of processes that is
    "marked," initially just i0. Process i0 sends out a search message at
    round 1, to all of its outgoing neighbors. At any round, if an unmarked
    process receives a search message, it marks itself and chooses one of the
    processes from which the search has arrived as its parent. At the first
    round after a process gets marked, it sends a search message to all of its
    outgoing neighbors.

    Requires: testLeaderElection
    Effects: every Process has state['parent']. Leader has state['parent'] = None
    """
    class Search(Message):
        """Search for children"""
        pass
    
    def is_i0(self, p): return p.state["status"] == "leader"

    def msgs_i(self, p):
        if self.is_i0(p) and self.r == 1:
            p.output("parent",  None, self.params["silent"])
            p.send_msg(SynchBFS.Search(self, p))
        if self.has(p, "recently_marked"):
            p.send_msg(SynchBFS.Search(self, p))
            self.delete(p, "recently_marked")
    def trans_i(self, p, msgs):
        if len(msgs)> 0:
            if "parent" not in p.state:
                p.output("parent",  msgs[0].content, self.params["silent"])
                self.set(p, "recently_marked",  True)
                return
        if "parent" in p.state:
            if self.has(p, "recently_marked"): self.delete(p, "recently_marked")
            p.terminate(self)

class SynchBFSAck(Synchronous_Algorithm):
    """
    At any point during execution, there is some set of processes that is
    "marked," initially just i0. Process i0 sends out a search message at
    round 1, to all of its outgoing neighbors. At any round, if an unmarked
    process receives a search message, it marks itself and chooses one of the
    processes from which the search arrived as its parent. At the first
    round after a process gets marked, it sends a search message to all of its
    outgoing neighbors, and an acknowledgement to its parent, so that nodes
    will also know their children.

    Requires: testLeaderElection
    Effects: Every process has:
                state['parent']. Leader has state['parent'] = None
                state['childen']. Leaves have state['children'] = []
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
            p.output( "parent",  None, self.params["silent"])
            self.set(p, "recently_marked",  True)
            p.send_msg(SynchBFSAck.Search(self, p))
        elif self.has(p, "recently_marked"):
            p.send_msg(SynchBFSAck.Search(self, p))
            p.send_msg(SynchBFSAck.AckParent(self, p), p.state['parent'] )
            if not self.params["silent"]:
                print p,"ack", p.state['parent']
    def trans_i(self, p, msgs):
        search_msgs = [m.content for m in msgs if isinstance(m, SynchBFSAck.Search)]
        ack_msgs = [m.content for m in msgs if isinstance(m, SynchBFSAck.AckParent)]

        if 'parent' not in p.state:
            if len(search_msgs)> 0:
                p.output( "parent",  search_msgs[0], self.params["silent"])
                self.set(p, "recently_marked",  True)
                if not self.params["silent"]:
                    print str(p), "chooses parent"
        else:
            if self.has(p, "recently_marked"):
                self.delete(p, "recently_marked")
            elif "children" not in p.state:
                p.output("children",  ack_msgs, self.params["silent"])
                p.terminate(self)
                if not self.params["silent"]:
                    print p,"knows children"

#Convergecast

class SynchConvergecast(Synchronous_Algorithm):
    """Precondition: Every Process knows state['parent']

    #TODO If Processes also know state['children'] ==> Reduced Communication Complexity.
    """
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
    def cleanup_i(self, p): self.delete(p, 'send')
    def trans_root(self, p, msgs):          pass
    def outpout_root(self, p):              pass
    def initial_msg_to_parent(self, p):     return
    def trans_msg_to_parent(self, p, msgs): return

class AsynchConvergecast(Asynchronous_Algorithm):
    """
    Requires:
    -  Every Process knows state['parent'] and state['children']"""
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
        self.increment(p,'reports', msgs)
        if len(p.state['children']) == len(self.get(p, 'reports')):
            if self.is_root(p):
                self.trans_root(p, self.get(p, 'reports'))
                self.output_root(p)
                p.terminate(self)
            else:
                trans_msg = self.trans_msg_to_parent(p, self.get(p, 'reports'))
                self.set(p, 'send', trans_msg)

    def cleanup_i(self, p):
        self.delete(p, 'send')
        self.delete(p, 'reports')

    def trans_root(self, p, msgs):          pass
    def outpout_root(self, p):              pass
    def initial_msg_to_parent(self, p):     return
    def trans_msg_to_parent(self, p, msgs): return

def _ConvergeHeight(Convergecast):
    class ConvergeHeight(Convergecast):
        """
        Requires: BFS Tree
        Effects: i0 gets height of tree in state["height"]
        """
        def trans_root(self, p, msgs):      #Updates height
            self.set(p, 'height', max(msgs)) 
        def output_root(self, p):           #Decides height
            p.output('height', self.get(p, 'height'), self.params['silent']) 
        def initial_msg_to_parent(self, p):
            return Message(self, 1)
        def trans_msg_to_parent(self, p, msgs):
            return Message(self, 1 + max(msgs))    
        def cleanup_i(self, p):
            Convergecast.cleanup_i(self,p)
            self.delete(p, 'height')
    return ConvergeHeight

SynchConvergeHeight = _ConvergeHeight(SynchConvergecast)
AsynchConvergeHeight = _ConvergeHeight(AsynchConvergecast)

#Broadcast
class SynchBroadcast(Synchronous_Algorithm):
    """
    Requires: BFS Tree with children pointers, where root node has state['height']
    Effects: Broadcasts state['height'] to all nodes as state['height'].
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
                p.output(attr,  msgs[0], self.params["silent"])
                if len(p.state['children']) > 0:
                    self.set(p, 'send',  msgs[0])
                else:
                    p.terminate(self)
    def cleanup_i(self, p): self.delete(p, 'send')

#Maximal Independent Set
class SynchLubyMIS(Synchronous_Algorithm):
    """ 
    The algorithm works in stages, each consisting of three rounds.

    Round 1: In the first round of a stage, the processes choose their
        respective vals and send them to their neighbors. By the end of round
        1, when all the val messages have been received, the winners--that is,
        the processes in F--know who they are.
    Round 2: In the second round, the winners notify their neighbors. By
        the end of round 2, the losers--that is, the processes having neighbors
        in F--know who they are.
    Round 3: In the third round, each loser notifies its neighbors. Then
        all the involved processes--the winners, the losers, and the losers'
        neighbors-- remove the appropriate nodes and edges from the graph. More
        precisely, this means the winners and losers discontinue participation
        after this stage, and the losers' neighbors remove all the edges that
        are incident on the newly removed nodes.

    Requires: n, the size of the network
    Effect: Every process knows 'MIS'. A boolean representing whether it is a member
    of the Maximal Independent Set found by Luby's algorithm.
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
                p.output('MIS', True, self.params['silent'])
        if self.r%3 ==2:
            if 'winner' in values:
                self.set(p, 'status', 'loser')
                p.output('MIS', False, self.params['silent'])
        if self.r%3 == 0:
            rem_nbrs = self.get(p, 'rem_nbrs')
            for m in msgs:
                if m.content == 'loser':
                    rem_nbrs.remove(m.author)
            self.set(p, 'rem_nbrs', rem_nbrs)
            if self.get(p, 'status') in ['winner', 'loser']:
                p.terminate(self)

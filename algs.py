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

    Effects:
        Every process has state['status'] is 'leader' or 'non-leader'.
        Exactly one process has state['status'] is 'leader'
    """
    def __init__(self, network = None, params = {"draw": False, "silent": False}, name=None):
        def LCR_msgs(p):
            if not self.has(p, "send"):
                self.set(p, 'send', Message(self, p.UID))

            msg = self.get(p, "send")
            if msg is None:
                return
            self.set(p,"send", None)
            p.send_msg(msg, p.out_nbrs[-1])

        def LCR_trans(p, msgs): #TODO replace params['silent'] with verbosity levels.
            if len(msgs) == 0:
                self.set(p,"send", None)
            else:
                msg = msgs.pop()
                if msg.content == p.UID:
                    p.output("status", "leader", params["silent"])
                    p.terminate(self)
                elif msg.content > p.UID:
                    self.set(p,"send", msg)
                    p.output("status", "non-leader", params["silent"])
                    p.terminate(self) #shouldn't really halt yet.
                else:
                    self.set(p, "send",  None)
        
        def cleanup (p): self.delete(p, 'send')
        Synchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, cleanup_i=cleanup, network=network, params=params, name=name)

class AsyncLCR(Asynchronous_Algorithm):
    class Leader_Declaration(Message): pass
    def __init__(self, network = None, params= {"draw":False, "silent":False}):
        def LCR_msgs(p, verbose=False):
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

        def LCR_trans(p, verbose=False):
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
                    p.output("status", "leader", params["silent"])
                elif msg.content > p.UID:
                    self.get(p, "sends").append(msg)
                    p.output("status", "non-leader", params["silent"])

        def cleanup (p): self.delete(p, 'sends')
        Asynchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, cleanup_i=cleanup, network = network, params=params )

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
    def __init__(self, network = None, params = {"draw": False, "silent": False}):
        
        def FloodMax_msgs(p):
            if self.r < self.get(p, "diam"):
                if not self.has(p, "send"):
                    self.set(p, "send",  Message(self, p.UID))
                p.send_msg(self.get(p, "send"))

        def FloodMax_trans(p, msgs, verbose=False):
            if verbose:
                print p, "received", p.in_channel
            seen_uids = msgs + [self.get(p, "send")]
            self.set(p, "send",  max(seen_uids, key = lambda m: m.content))

            if self.r == self.get(p, "diam"):
                if self.get(p, "send").content == p.UID:
                    p.output("status", "leader", params["silent"])
                    p.terminate(self)
                else:
                    p.output("status", "non-leader", params["silent"])
                    p.terminate(self)

        def cleanup (p): self.delete(p, 'send')
        Synchronous_Algorithm.__init__(self, FloodMax_msgs, FloodMax_trans, cleanup_i=cleanup, network = network, params = params)

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

    def __init__(self, network = None, params = {"draw": False, "silent": False}):
        is_i0 = lambda p: p.state["status"] == "leader"
        def BFS_msgs(p):
            if is_i0(p) and self.r == 1:
                p.output("parent",  None, params["silent"])
                p.send_msg(SynchBFS.Search(self, p))
            if self.has(p, "recently_marked"):
                p.send_msg(SynchBFS.Search(self, p))
                self.delete(p, "recently_marked")
        def BFS_trans(p, msgs):
            if len(msgs)> 0:
                if "parent" not in p.state:
                    p.output("parent",  msgs[0].content, params["silent"])
                    self.set(p, "recently_marked",  True)
                    return
            if "parent" in p.state:
                if self.has(p, "recently_marked"): self.delete(p, "recently_marked")
                p.terminate(self)

        Synchronous_Algorithm.__init__(self, BFS_msgs, BFS_trans, network = network, params = params)

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

    def __init__(self, network = None, params = {"draw": False, "silent": False}):
        is_i0 = lambda p: p.state["status"] == "leader"
        def BFS_msgs(p):
            if is_i0(p) and self.r == 1:
                p.output( "parent",  None, params["silent"])
                self.set(p, "recently_marked",  True)
                p.send_msg(SynchBFSAck.Search(self, p))
            elif self.has(p, "recently_marked"):
                p.send_msg(SynchBFSAck.Search(self, p))
                p.send_msg(SynchBFSAck.AckParent(self, p), p.state['parent'] )
                if not params["silent"]:
                    print p,"ack", p.state['parent']
        def BFS_trans(p, msgs):
            search_msgs = [m.content for m in msgs if isinstance(m, SynchBFSAck.Search)]
            ack_msgs = [m.content for m in msgs if isinstance(m, SynchBFSAck.AckParent)]

            if 'parent' not in p.state:
                if len(search_msgs)> 0:
                    p.output( "parent",  search_msgs[0], params["silent"])
                    self.set(p, "recently_marked",  True)
                    if not params["silent"]:
                        print str(p), "chooses parent"
            else:
                if self.has(p, "recently_marked"):
                    self.delete(p, "recently_marked")
                elif "children" not in p.state:
                    p.output("children",  ack_msgs, params["silent"])
                    p.terminate(self)
                    if not params["silent"]:
                        print p,"knows children"

        Synchronous_Algorithm.__init__(self, BFS_msgs, BFS_trans, network = network, params = params)

#Convergecast

class SynchConvergeHeight(Synchronous_Algorithm):
    """
    Requires: BFS Tree
    Effects: i0 gets height of tree in state["height"]
    """
    def __init__(self, network = None, params = {"draw": False, "silent": False}):
        def msgs(p):
            if p.state['parent'] is not None:
                if self.r == 1:
                    self.set(p, 'send',  Message(self, 1))
                if self.get(p, 'send') is not None:
                    p.send_msg(self.get(p, 'send'), p.state['parent'])
                    self.set(p, 'send',  None)
        def trans(p, msgs):
            msgs = [m.content for m in msgs]
            if p.state['parent'] is None: #p is root node, i0.
                if self.r == 1:
                    self.set(p, 'height',  0) #Initializes height.
                if len (msgs) > 0:
                    self.set(p, 'height',  max(msgs)) #Updates height.
                else:
                    p.output('height', self.get(p, 'height'), params["silent"]) #Decides height.
                    p.terminate(self)
            else: #p is not root node.
                if len (msgs) > 0:
                    self.set(p, 'send',  Message(self, 1 + max(msgs)))
                else:
                    p.terminate(self)

        def cleanup(p): self.delete(p, 'send'); self.delete(p, 'height')
        Synchronous_Algorithm.__init__(self, msgs, trans, cleanup_i=cleanup, network = network, params = params)


class SynchConvergecast(Synchronous_Algorithm):
    """Precondition: Every Process knows state['parent']

    If Processes also know state['children'] ==> Reduced Communication Complexity."""
    pass

class AsynchConvergecast(Asynchronous_Algorithm):
    """Precondition: Every Process has state['parent'] and state['children']"""
    pass

#Broadcast
class SynchBroadcast(Synchronous_Algorithm):
    """
    Requires: BFS Tree with children pointers, where root node has state['height']
    Effects: Broadcasts state['height'] to all nodes as state['height'].
    """
    def __init__(self, network = None, params = {'attr':'height', "draw": False, "silent": False}):
        attr = params['attr']
        def msgs(p):
            if p.state['parent'] is None:
                if self.r == 1:
                    p.send_msg(Message(self, p.state[attr]), p.state['children']) 
            if p.state['parent'] is not None:
                if self.get(p, 'send') is not None:
                    p.send_msg(Message(self,self.get(p, 'send')), p.state['children'])
                    self.set(p, 'send',  None)
                    p.terminate(self)
        def trans(p, msgs):
            msgs = [m.content for m in msgs]
            if p.state['parent'] is None:
                p.terminate(self)
            else:
                if len (msgs) == 1:
                    p.output(attr,  msgs[0], params["silent"])
                    if len(p.state['children']) > 0:
                        self.set(p, 'send',  msgs[0])
                    else:
                        p.terminate(self)
        def cleanup(p): self.delete(p, 'send')
        Synchronous_Algorithm.__init__(self, msgs, trans, cleanup_i = cleanup, network = network, params = params)

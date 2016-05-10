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

    def get_draw_args(self,network,vals):
        """network - refers to the network on which the algorithm is running.
        vals - the positions of the nodes in the network"""
        node_colors = dict()
        edge_colors = None
        for p in network.processes:
            # if self.has(p, "decided"):
            if p.state['status'] == "leader":
                node_colors[p.UID] = 'ro'

            elif p.state['status'] == "non-leader": # non-leader
                node_colors[p.UID] = 'bo'

        # algoDrawArgs = AlgorithmDrawArgs(node_colors = node_colors, edge_colors = edge_colors)
        return node_colors, edge_colors

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
class SynchFloodMax(Synchronous_Algorithm):
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

class SynchHS(Synchronous_Algorithm):
    """The Hirschberg and Sinclair ("HS") algorithm for Leader Election in a Synchronous Bidirectional Ring Network

    This algorithm works in phases 0, 1, 2, ... O(logn) in a bidrectional ring. It achieves a message complexity of O(n*logn), 
    which improves upon the O(n**2) message complexity of LCR.

    Each Process sends out "tokens" containing its identifier in both directions (left and right)
    around the ring. These tokens are intended to travel a distance 2**l, and then return to
    the Process. If the Process receives back both tokens, it continues with the next phase.
    However, a Process will not always receive back both of its tokens. As a token is
    passed around the ring, when a Process receives an incoming token, it compares the identifier
    encoded in that token to its own. If the incoming identifier is greater than its own, it keeps passing the identifier;
    If the identifier is less than its own, it discards the incoming identifier;
    if it is equal to its own, the Process declares itself the leader.

    Effects:
        - Every process has state['status'] is 'leader' or 'non-leader'.
        - Exactly one process has state['status'] is 'leader'
    """
    class Leader_Declaration(Message): pass
    
    def msgs_i(self, p):
        if "status" in p.state:
            p.send_msg(SynchHS.Leader_Declaration(self), p.out_nbrs[-1])
            return p.terminate(self)

        # initialize messages if needed
        plus_msg = (p.UID, "out", 1)
        minus_msg = (p.UID, "out", 1)
        if not self.has(p, "send+"):
            self.set(p, 'send+', Message(self, plus_msg))

        if not self.has(p, "send-"):
            self.set(p, 'send-', Message(self, minus_msg))

       # send the current value of send+ to process i + 1
        msg = self.get(p, "send+")
        if msg is not None:
            self.set(p, "send+", None)
            p.send_msg(msg, p.out_nbrs[-1])

        # send the current value of send- to process i- 1
        msg = self.get(p, "send-")
        if msg is not None:
            self.set(p, "send-", None)
            p.send_msg(msg, p.out_nbrs[0])

    def trans_i(self, p, msgs):
        # initialize the phase of process p to phase 0
        if not self.has(p, "phase"):
            self.set(p, "phase", 0)

        left_msg_returned = False
        right_msg_returned = False
        for msg in msgs:
            if isinstance(msg, SynchHS.Leader_Declaration):
                self.output(p, "status", "non-leader") #Terminates next msgs_i
                return
            val, flag, hopcount = msg.content

            # If msg came from process i-1
            if msg.author == p.out_nbrs[0]:
                if flag == 'out':
                    if val > p.UID and hopcount > 1:
                        self.set(p, 'send+', Message(self, (val, flag, hopcount-1)))
                    if val > p.UID and hopcount == 1:
                        self.set(p, 'send-', Message(self, (val, 'in', 1)))
                    if val == p.UID:
                        return self.output(p, "status", "leader") #Terminates next msgs_i
                if flag == 'in':
                    if val != p.UID:
                        self.set(p, 'send+', msg)
                    else:
                        left_msg_returned = True

            #If msg came from process i+1
            if msg.author == p.out_nbrs[1]:
                if flag == 'out':
                    if val > p.UID and hopcount > 1:
                        self.set(p, 'send-', Message(self, (val, flag, hopcount-1)))
                    if val > p.UID and hopcount == 1:
                        self.set(p, 'send+', Message(self, (val, 'in', 1)))
                    if val == p.UID:
                        return self.output(p, "status", "leader") #Terminates next msgs_i
                if flag == 'in':
                    if val != p.UID:
                        self.set(p, 'send-', msg)
                    else:
                        right_msg_returned = True

        if left_msg_returned and right_msg_returned:
            #Start next phase
            next_phase = self.get(p, 'phase') + 1
            self.set(p, 'phase', next_phase)
            self.set(p, 'send+', Message(self, (p.UID, "out", 2**next_phase)))
            self.set(p, 'send-', Message(self, (p.UID, "out", 2**next_phase)))

class SynchTimeSlice(Synchronous_Algorithm):
    """The TimeSlice algorithm in a Synchronous Ring Network

    Computation proceeds in phases 1, 2, ..., where each phase consists
    of n consecutive rounds. Each phase is devoted to the possible
    circulation, all the way around the ring, of a token carrying a
    particular UID. More specifically, in phase v, which consists of
    rounds (v - 1)n + 1,... , vn, only a token carrying UID v is permitted
    to circulate. If a process i with UID v exists, and round (v - 1)n + 1
    is reached without i having previously received any non-null messages,
    then process i elects itself the leader and sends a token carrying its
    UID around the ring. As this token travels, all the other processes note
    that they have received it, which prevents them from electing themselves
    as leader or initiating the sending of a token at any later phase.

    Requires:
        - Every process knows state['n'], the size of the network

    Effects:
        - Every process has state['status'] is 'leader' or 'non-leader'.
        - Exactly one process has state['status'] is 'leader'
    """
    def msgs_i(self, p):
        msg = self.get(p, "send")
        if msg:
            if (self.r - 1)/p.state['n'] == msg.content-1:
                p.send_msg(msg)

            p.terminate(self)
        
        elif self.r == (p.UID-1)*p.state['n']+1 and not self.has(p, "decided"): # check if logic is correct for this
            self.set(p, 'decided', None)
            self.output(p,"status", "leader")
            msg = Message(self, p.UID)
            p.send_msg( msg) 
            p.terminate(self)


    def trans_i(self, p, msgs):
        if len(msgs) > 0:
            msg = msgs[0] # modify this
            if (self.r - 1)/p.state['n'] == msg.content-1 and not self.has(p,"decided"):
                self.set(p, 'decided', None)
                self.output(p,"status", "non-leader")
                self.set(p,"send", msg)

            else:
                self.set(p,"send",None)
                p.terminate(self)

class SynchVariableSpeeds(Synchronous_Algorithm):
    """
    The VariableSpeeds algorithm for Leader Election in a Synchronous Ring Network 

    Each process i initiates a token which travels around the ring.
    - Different tokens tavel at different rates: a token carraying UID v travels at
    the rate of 1 message transmission every 2^v rounds. 
    For example, for the token with UID 1, each process along its path waits 
    2 rounds after receiving the token before sending it out.
    - Each process keeps track of the smallest UID it has seen and discard any token 
    with the UID larger than the smallest UID
    - If a token returns to its originator, the originator is elected.
    
    Effects:
        - Every process has state['status'] is 'leader' or 'non-leader'.
        - Exactly one process has state['status'] is 'leader'
    """
    class Leader_Declaration(Message): pass

    def msgs_i(self, p):
        if 'status' in p.state:
            p.send_msg(SynchVariableSpeeds.Leader_Declaration(self), p.out_nbrs[-1])
            return p.terminate(self)

        if not self.has(p, "queue"):
            token =  Message(self, {"UID": p.UID, "TTS": 2**p.UID})
            self.set(p, "queue", [token])
            self.set(p, "smallest_uid", p.UID)

        queue = self.get(p, "queue")

        for i in reversed(range(len(queue))):
            msg = queue[i]
            msg.content["TTS"] -= 1
            if msg.content["TTS"] <= 0:
                if msg.content['UID'] == self.get(p, "smallest_uid"):
                    p.send_msg(msg, p.out_nbrs[-1])
                queue.pop(i)

        self.set(p, "queue", queue)

    def trans_i(self, p, msgs):
        queue = self.get(p, "queue")

        for msg in msgs:
            if isinstance(msg, SynchVariableSpeeds.Leader_Declaration):
                return self.output(p, 'status', 'non-leader') #Terminates next msgs_i
            if msg.content["UID"] == p.UID:
                return self.output(p, 'status', 'leader') #Terminates next msgs_i
            if msg.content["UID"] < self.get(p, "smallest_uid"):
                self.set(p, "smallest_uid", msg.content["UID"])
            
            msg.content["TTS"] = 2**msg.content["UID"]
            queue.append(msg)

        self.set(p, "queue", queue)

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
        - assertLeaderElection
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

    def get_draw_args(self,network,vals):
        """network - refers to the network on which the algorithm is running.
        vals - the positions of the nodes in the network"""
        node_colors = None
        edge_colors = dict()
        for p in network.processes:
            if p.state['parent']:
                parent_UID = p.state['parent'].UID
                edge_colors[(p.UID,parent_UID)] = 'r'

        return node_colors, edge_colors
        

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
        - assertLeaderElection
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
    Effects:
        - The root node knows the result of some global computation on the
        network (subclasses of SynchConvergecast define this computation).
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

class AsynchConvergecast(Asynchronous_Algorithm):
    """The abstract superclass of a class of Asynchronous Algorithms that
    propagate information from the leaves of a BFS tree to its root.

    Requires:
        - Every Process knows state['parent'] and state['children']
    Effects:
        - The root node knows the result of some global computation on the
        network (subclasses of SynchConvergecast define this computation).
    """
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

#All pairs shortest paths
#TODO : Doesn't seem to work for networks with negative weight edges.
class SynchBellmanFord(Synchronous_Algorithm):
    """
    All pairs shortest paths algorithm for a synchronous Network.

    Requires:
        - Every process knows state['nbr_dist'][UID], the weight of the edge
        form the process to the neighboring process with uid UID, for all
        neighbors.
    Effect:
        - Every process knows state['SP'][UID], the weight of the
        shortest path to the process with uid UID, for every other process
        in the network.
    """
    def msgs_i(self, p):
        if self.r == 1:
            self.set(p, 'SP', p.state['nbr_dist'])
            self.set(p, 'send', True)
        
        if self.get(p, 'send') == True:
            p.send_msg(Message(self, self.get(p, 'SP')))

        if self.r == p.state['n']:
            p.output('SP', self.get(p, 'SP'))
            p.terminate(self)

    def trans_i(self, p, msgs):
        self.set(p, 'send', False)

        SP = self.get(p, 'SP')
        updated_SP = deepcopy(SP)
        for msg in msgs:
            u = msg.author.UID
            for v, weight in msg.content.items():
                if v == p.UID:
                    continue
                if v not in SP or SP[u] + weight < SP[v]:
                    updated_SP[v] = SP[u] + weight

        if updated_SP != SP:
            self.set(p, 'SP', updated_SP)
            self.set(p, 'send', True)

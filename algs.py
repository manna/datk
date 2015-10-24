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
    """
    def __init__(self, network = None, params = {"draw": False, "silent": False}):
        def LCR_msgs(p):
            msg = p.state["send"]
            if msg is None:
                return
            p.state["send"] = None
            p.send_msg(self, msg, p.out_nbrs[-1])

        def LCR_trans(p, verbose=False): #TODO replace params['silent'] with verbosity levels.
            msgs = p.get_msgs()
            if len(msgs) == 0:
                p.state["send"] = None
            else:
                msg = msgs.pop()
                if msg == p.UID:
                    p.output("leader", params["silent"])
                    p.terminate(self)
                elif msg > p.UID:
                    p.state["send"] = msg
                    p.output("non-leader", params["silent"])
                    p.terminate(self)
                else:
                    p.state["send"] = None
            if verbose:
                print str(p) + " received " + str(p.in_channel)
                print "state: " + str(p.state)
        Synchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, network=network, params=params)

class AsyncLCR(Asynchronous_Algorithm):
    class Leader_Declaration(Message):
        def __str__(self):
            return "LD"
    def __init__(self, network = None, params= {"draw":False, "silent":False}):
        def LCR_msgs(p, verbose=False):
            if "status" in p.state and p.state["status"] == "leader":
                msg = AsyncLCR.Leader_Declaration()
                p.send_msg(self, msg, p.out_nbrs[-1])
                if verbose:
                    print str(p) + " sends " + str(msg)
                p.terminate(self)
                return
            while len(p.state["sends"]) > 0:
                msg = p.state["sends"].pop()
                p.send_msg(self, msg, p.out_nbrs[-1])
                if verbose:
                    print str(p) + " sends " + str(msg)

        def LCR_trans(p, verbose=False):
            if verbose:
                print str(p) + " received " + str(p.in_channel)
            msgs = p.get_msgs()
            while len(msgs) > 0:
                msg = msgs.pop()
                if isinstance(msg, AsyncLCR.Leader_Declaration):
                    p.send_msg(self, msg, p.out_nbrs[-1])
                    if verbose:
                        print str(p) + " sends " + str(msg)
                    p.terminate(self)
                    return
                if msg == p.UID:
                    p.output("leader", params["silent"])
                elif msg > p.UID:
                    p.state["sends"].append(msg)
                    p.output("non-leader", params["silent"])

        Asynchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, network = network, params=params )


#Leader Election Algorithms for general Networks:

class FloodMax(Synchronous_Algorithm):
    """
    Every process maintains a record of the maximum UID it has seen so far
    (initially its own). At each round, each process propagates this maximum
    on all of its outgoing edges. After diam rounds, if the maximum value seen
    is the process's own UID, the process elects itself the leader; otherwise,
    it is a non-leader.

    Assumes, for every process, p, p.state["diam"] == the diameter of the network.
    """
    def __init__(self, network = None, params = {"draw": False, "silent": False}):
        def LCR_msgs(p):
            if self.r < p.state["diam"]:
                msg = p.state["send"]
                p.send_msg(self, msg)

        def LCR_trans(p, verbose=False):
            if verbose:
                print "state: " + str(p.state)
                print str(p) + " received " + str(p.in_channel)
            seen_uids = p.get_msgs()+[p.state["send"]]
            p.state["send"] = max(seen_uids)

            if self.r == p.state["diam"]:
                if p.state["send"] == p.UID:
                    p.output("leader", params["silent"])
                    p.terminate(self)
                else:
                    p.output("non-leader", params["silent"])
                    p.terminate(self)

        Synchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, network = network, params = params)

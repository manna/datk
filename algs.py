from distalgs import *

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
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
            p.send_to_all_neighbors(msg)

        def LCR_trans(p, verbose=False):
            msgs = p.get_msgs()
            if len(msgs) == 0:
                p.state["send"] = None
            else:
                msg = msgs.pop()
                if msg == p.UID:
                    p.output("leader")
                    p.terminate(self)
                elif msg > p.UID:
                    p.state["send"] = msg
                    p.output("non-leader")
                    p.terminate(self)
                else:
                    p.state["send"] = None
            if verbose:
                print str(p) + " received " + str(p.in_channel)
                print "state: " + str(p.state)
        Synchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, network = network )

class AsyncLCR(Asynchronous_Algorithm):
    class Leader_Declaration(Message):
        def __str__(self):
            return "LD"
    def __init__(self, network = None):
        def LCR_msgs(p, verbose=False):
            if "status" in p.state and p.state["status"] == "leader":
                msg = AsyncLCR.Leader_Declaration()
                p.send_to_all_neighbors(msg)
                if verbose:
                    print str(p) + " sends " + str(msg)
                p.terminate(self)
                return
            while len(p.state["sends"]) > 0:
                msg = p.state["sends"].pop()
                p.send_to_all_neighbors(msg)
                if verbose:
                    print str(p) + " sends " + str(msg)

        def LCR_trans(p, verbose=False):
            if verbose:
                print str(p) + " received " + str(p.in_channel)
            msgs = p.get_msgs()
            while len(msgs) > 0:
                msg = msgs.pop()
                if isinstance(msg, AsyncLCR.Leader_Declaration):
                    p.send_to_all_neighbors(msg)
                    if verbose:
                        print str(p) + " sends " + str(msg)
                    p.terminate(self)
                    return
                if msg == p.UID:
                    p.output("leader")
                elif msg > p.UID:
                    p.state["sends"].append(msg)
                    p.output("non-leader")

        Asynchronous_Algorithm.__init__(self, LCR_msgs, LCR_trans, network = network)

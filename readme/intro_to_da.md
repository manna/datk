#Distributed Algorithms

In 6.006 and 6.046, you have been exposed to a number of algorithms: shortest paths, searches, median-finding.. etc.

One thing all of these algorithms have in common is that they run on a single machine. When you define the algorithm, you dictate how it will run, and in which order the commands will execute.

##Stuff you couldn't do before
*Imagine now that you are writing an algorithm that is to be executed collaboratively by n different processes...*  
* The immediate implication that  the algorithm will terminate more quickly if you split up the work and let different processes work on their parts simultaneously is motivation enough in itself to care about distributed algorithms.
  * Distributed mergesort: imagine that the 2<sup>L</sup> merges that take place at level L of the tree were performed in parallel by 2<sup>L</sup> processes. What would the complexity be?
* If that doesn't stir you: many of the algorithms you will encounter in industry will be distibuted.
  * Twitter's multiple signed in users simultaneously adding tweets to a database.
  * Google's MapReduce sifting through more data than it is possible to store on one machine.
  * Facebook messenger passing messages between users, guaranteeing that users see the messages in the same order. (Imagine you send a message to your friend, and before it arrives there, they send you a message).
  * Two Amazon users try to buy the last item in stock at the same time. When their requests hit Amazon's servers, the item is still available. Ensure that not both of them are allowed to buy it.
  * ...and more

##Problems you didn't think you had
Here are some problems that don't exist in a non-distributed setting. If you take 6.852 in the fall, these are the problems you'll be thinking about.
* Leader Election (keep reading)
* Distributed Consensus (google it)
* Mutual Exclusion (google it)

###Leader Election:
Imagine that you have a number of processes collaborating, and a designated leader process coordinating them. If the leader process crashes, they remaining processes would need to elect a new leader.

**Leader Election in a synchronous ring netowrk with identical processes is impossible**
* 'identical' : all processes are identical, right down to generating the same random numbers, and running the same code.
* All processes have the same initial states, so in the first round of the algorithm, they send the exact same messages their neighbors. The symmetry of the ring means that at the second round, every Process will have received the same messages, and transitioned to the same state as every other Process. When one of them decides to elect itself leader, they all do.

So, let's assume that the processes are identical *except* that each has a **unique identifier** (UID). Now, Leader Election is possible.

####LCR: Leader Election in a Synchronous Ring Netork
>"Each Process sends its identifier around the ring. When a Process receives an incoming identifier, it compares that identifier to its own. If the incoming identifier is greater than its own, it keeps passing the identifier; if it is less than its own, it discards the incoming identifier; if it is equal to its own, the Process declares itself the leader."  *(Distributed Algorithms. Nancy Lynch)*  

If you have Python 2.7, you can simulate distributed algorithms using the python package "datk" (Distributed Algorithms ToolKit). Here's a basic tutorial to get you started:

    $ pip install datk
    $ python
    >>> from datk import *
    >>> ring = Unidirectional_Ring(10)  #Choose the size of the network
    >>> ring.state() #What does this print? ('P3' represents the process with UID 3)
    >>> LCR(ring)
    >>> ring.state() #What does this print now?
Go read about other distributed algorithms, and take 6.852 next semester to study them in depth!


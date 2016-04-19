from threading import Thread, Lock
from time import sleep, time
from distalgs import Process, Algorithm, Synchronous_Algorithm

def print_with_underline(text):
    print text
    print "="*len(text)

class Tester:
    def __init__(self, DEFAULT_TIMEOUT = 10, TEST_BY_DEFAULT = True, MAIN_THREAD_BY_DEFAULT = False):
        self.DEFAULT_TIMEOUT = DEFAULT_TIMEOUT
        self.TEST_BY_DEFAULT = TEST_BY_DEFAULT
        self.MAIN_THREAD_BY_DEFAULT = MAIN_THREAD_BY_DEFAULT

        self._lock = Lock()
        self._num_tests = 0
        self._failed_tests = set()

    def test(self, f=None, timeout=None, main_thread=None, test=None):
        """
        Decorator function test to run distributed algorithm tests in safe environment. Logs failed tests.

        @param f: the test (a function) to run.
        @param timeout: the number of seconds to allow the test to run, before timing it out (causing it to fail).
        @param main_thread: True iff the test cannot run on a thread other than the main thread.
        @param test: If false, skips testing this function. Useful because it can be set to default to false, and then set to True for a select few tests currently being tested.
        """
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        if main_thread is None:
            main_thread = self.MAIN_THREAD_BY_DEFAULT
        if test is None:
            test = self.TEST_BY_DEFAULT

        if not test: return lambda f: f

        def test_decorator(f):

            def test_f():
                try:
                    f()
                except Exception, e:
                    self._failed_tests.add(f.__name__)
                    print_with_underline("TEST "+f.__name__+" FAILED.")
                    raise e
                finally:
                    self._num_tests+=1
            with self._lock:
                if main_thread:
                    status = "Running test "+f.__name__+" on main thread."
                    print status
                    test_f()
                    print "#"*len(status)
                else:
                    t = Thread(target = test_f)
                    t.daemon = True
                    
                    start_time = time()
                    t.start()
                    t.join(timeout)
                    end_time = time()
                    if end_time - start_time >= timeout:
                        self._failed_tests.add(f.__name__)
                        print_with_underline(f.__name__ + " TIMED OUT AFTER " + str(timeout) + "s")
                    else:
                        print_with_underline(f.__name__ + " RAN IN " +str(end_time-start_time) + "s")
        if f is None:
            return test_decorator
        else:
            test_decorator(f)
            return f

    def summarize(self):
        """Called at the end of a test suite. Prints out summary of failed tests"""
        
        print self._num_tests, "tests ran with", len(self._failed_tests), "failures:", sorted(list(self._failed_tests))

        self._num_tests = 0
        self._failed_tests = set()

import matplotlib.pyplot as plt
def benchmark(Algorithm_, Network_, test):
    """
    Benchmarks the Algorithm on a given class of Networks. Samples variable network size, and plots results.

    @param Algorithm_: a subclass of Synchronous_Algorithm, the algorithm to test.
    @param Network_: a subclass of Network, the network on which to benchmark the algorithm.
    @param test: a function that may throw an assertion error 
    """                     
    
    def sample(Algorithm_, Network_, test):
        """
        Runs the Algorithm on Networks of the given type, varying n.
        After every execution, runs test on the resultant Network_.

        @param Algorithm_: a subclass of Synchronous_Algorithm, the algorithm to test.
        @param Network_: a subclass of Network, the network on which to benchmark the algorithm.
        @param test: a function that may throw an assertion error 
        @return: (size, time, comm) where size is a list of values of network size,
        and time and comm are lists of corresponding values of time and communication complexities.
        """
        size = []
        time = []
        comm = []
        n, lgn = 2, 1
        max_time = 0
        max_comm = 0
        print "Sampling n = ...",
        while max(max_time, max_comm) < 10000 and n < 500:

            #Progress
            if n == 2:
                print "\b\b\b\b"+str(n)+"...",
            else:
                print "\b\b\b\b, "+str(n)+"...",

            cur_times = []
            cur_comms = []
            for i in xrange( max(4, 2+lgn) ):
                A = Algorithm_(params={'draw': False, 'verbosity': Algorithm.SILENT})
                x = Network_(n)
                A(x)
                try:
                    test(x)
                except AssertionError, e:
                    print "Algorithm Failed"
                    return None
                else:
                    size.append(n)
                    cur_comms.append(A.message_count)
                    comm.append(A.message_count)

                    if issubclass(Algorithm_, Synchronous_Algorithm):
                        cur_times.append(A.r)
                        time.append(A.r)
                        max_time = max(max_time, A.r)
                    max_comm = max(max_comm, A.message_count)

            #TODO here, decide whether need more samples for this n, based on cur_times and cur_comms variance
            n*=2
            lgn += 1
        print " DONE"
        return size, comm, time

    def averages(x,y):
        """
        Groups x's with the same value, averages corresponding y values.

        @param x: A sorted list of x values
        @param y: A list of corresponding y values
        @return: (x grouped by value, corresponding mean y values)
        
        Example:

        averages([1,1,2,2,2,3], [5,6,3,5,1,8]) --> ([1, 2, 3], [5.5, 3.0, 8.0])
        
        """
        new_x = [x[0]]
        new_y = []

        cur_x = new_x[0]
        cur_ys = []
        for x_i, y_i in zip(x,y):
            if x_i == cur_x:
                cur_ys.append(y_i)
            else:
                new_y.append( sum(cur_ys)/float(len(cur_ys) ) )
                new_x.append( x_i )
                cur_ys = [y_i]
                cur_x = x_i
        new_y.append( sum(cur_ys)/float(len(cur_ys) ) )
        return new_x, new_y

    def plot(x, y, title):
        """Plots the points (x[i],y[i]) for all i, fig."""
        fig, ax = plt.subplots()

        x_ave,y_ave = averages(x,y)

        ax.scatter(x, y, label="data", color='b')
        ax.scatter(x_ave, y_ave, label="means", color='r')
        
        ax.set_xlim( xmin=0 ) 
        ax.set_ylim( ymin=0 )
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_title(title)
        ax.set_xlabel(Network_.__name__ +' size')

    data = sample(Algorithm_, Network_, test)
    if data == None: return
    size, comm, time = data
    
    if issubclass(Algorithm_, Synchronous_Algorithm):
        plot(size, time, Algorithm_.__name__ + ' Time Complexity')

    plot(size, comm, Algorithm_.__name__ + ' Communication Complexity')

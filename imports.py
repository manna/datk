from datk.core.distalgs import *
from datk.core.algs import *
from datk.core.networks import *
from datk.core.benchmark import *
from datk.tests.helpers import *

def configure_ipython():
  """
  Convenient helper function to determine if environment is IPython.

  Sets matplotlib inline, if indeed in IPython
  Note that drawing is only safe in IPython qtconsole with matplotlib inline
  
  @return: True iff environment is IPython
  """
  try:
    __IPYTHON__
    ip = get_ipython()
    ip.magic("%matplotlib inline") 
  except NameError:
    return False
  else:
    return True

configure_ipython()
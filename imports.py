from datk.core.distalgs import *
from datk.core.algs import *
from datk.core.networks import *
from datk.tests.helpers import *

try:
  __IPYTHON__
  ip = get_ipython()
  ip.magic("%matplotlib inline") 
except NameError:
  pass

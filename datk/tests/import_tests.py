"""
From project root, can run:
$ nosetests datk.tests.import_tests
"""
from datk.core.tester import Tester
tester = Tester()
test = tester.test

@test
def test_core_imports():
    from datk.core.distalgs import *
    from datk.core.networks import *
    from datk.core.algs import *
    from datk.core.tester import *
    from datk.core.helpers import *
    from datk.core.simulator_mpl import *
    from datk.core.simulator_qt import *
    from datk.core.simulator_tk import *

@test
def test_simulator_qt_import():
    from datk.core.simulator_qt import (draw, simulate)

@test
def test_simulator__tk_import():
    from datk.core.simulator_tk import (draw, simulate)

# TODO: simulator_mpl under construction
# @test
# def test_simulator_mpl_import():
#     from datk.core.simulator_mpl import (draw, simulate)

tester.summarize()
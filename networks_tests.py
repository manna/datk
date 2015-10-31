from networks import *
from tester import *

@test(main_thread=True)
def DRAW_RANDOM():
    Random_Network(25).draw()

@test(main_thread=True)
def DRAW_UNI_RING():
    Unidirectional_Ring(4).draw()

@test(main_thread=True)
def DRAW_BI_RING():
    Bidirectional_Ring(7).draw()

@test(main_thread=True)
def DRAW_COMPLETE_GRAPH():
    Complete_Graph(10).draw()

@test(main_thread=True)
def DRAW_UNI_LINE():
    Unidirectional_Line(4).draw()

@test(main_thread=True)
def DRAW_BI_LINE():
    Bidirectional_Line(5).draw()


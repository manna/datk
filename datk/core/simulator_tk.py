"""
Algorithm step by step visualizer

Tk based GUI. Used by Network.start_simulation
"""
from Tkinter import Tk, Scale, ALL, HORIZONTAL
from colorizer import Color

class Simulator(Tk):
    def __init__(self, network):
        Tk.__init__(self)
        self.title("DATK")

        self.network = network
        self.n_steps = network.count_snapshots()
        self.network.restore_snapshot(0)
        self.canvas = Canvas(self, width=800, height=500)
        self.canvas.draw(self.network)
        self.canvas.pack()

        self.slider = Scale(self, from_=0, to=self.n_steps-1, length=300,
            orient=HORIZONTAL, command=self.updateValue)
        self.slider.pack(padx=10, pady=10)
    
    def updateValue(self, val):
        self.network.restore_snapshot(val)
        self.canvas.draw(self.network)
        
class Canvas(tk.Canvas):
    def __init__(self, root, width=300, height=300):
        tk.Canvas.__init__(self, root, width=width, height=height)
        self.width = width
        self.height = height
        self.pack()

    def draw(self, network):

        SCALE = 150

        def scale(v):
            x, y = v
            x *= SCALE
            y *= SCALE
            x += self.width/2
            y += self.height/2
            return x, y

        def v_draw(network, vertex, color=Color.black, radius=5):
            x,y = scale(vertex)
            color = color.toTk()
            self.create_oval(
                x-radius,
                y-radius,
                x+radius,
                y+radius,
                fill=color
            )

        def e_draw(network, edge, color=Color.black):
            start, end = edge
            start, end = scale(start), scale(end)
            x1,y1 = start
            x2,y2 = end
            color = color.toTk()
            self.create_line(x1, y1, x2, y2, fill=color)

        self.delete(ALL)
        network.general_draw(v_draw, e_draw)

def simulate(network):
    root = Simulator(network)
    root.mainloop()

def draw(network):
    master = Tk()
    master.title(str(len(network))+"-process "+network.__class__.__name__)
    c = Canvas(master)
    c.draw(network)
    master.mainloop()

if __name__=='__main__':
    from networks import Bidirectional_Ring
    from algs import LCR
    
    x = Bidirectional_Ring(5)
    LCR(x)
    simulate(x)
"""
Algorithm step by step visualizer

Tk based GUI. Used by Network.start_simulation
"""
import Tkinter as tk
from Tkinter import Tk, Scale, ALL, HORIZONTAL, CURRENT, Label, Toplevel
from ttk import Scale, Treeview
from colorizer import Color
from distalgs import Algorithm

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
        self.network.restore_snapshot(int(float(val)))
        self.canvas.draw(self.network)
    
    def destroy(self):
        self.network.restore_snapshot(-1)
        Tk.destroy(self)

class Canvas(tk.Canvas):
    def __init__(self, root, width=300, height=300):
        tk.Canvas.__init__(self, root, width=width, height=height)
        self.width = width
        self.height = height
        self.pack()
        self.graphicsItem2Process = {} #GraphicsItem id : process
        self.register_click_listener()
        self.tt = None #ToolTip
    
    def register_click_listener(self):
        def onclick(event):
            if self.tt: #Clicking anywhere off the tooltip hides it
                self.tt.destroy()
                self.tt = None
            if self.find_withtag(CURRENT): #Shows a tooltip
                item = self.find_withtag(CURRENT)[0]
                if item in self.graphicsItem2Process:
                    p = self.graphicsItem2Process[item]
                    text = "UID: "+str(p.UID)
                    self.tt = ToolTip(self, p, event.x, event.y)

        self.bind("<Button-1>", onclick)

    def draw(self, network):

        SCALE = 250

        def scale(v):
            x, y = v
            x *= SCALE
            y *= SCALE
            x += self.width/2
            y += self.height/2
            return x, y

        def v_draw(vertex, process, color=Color.black, radius=5):
            x,y = scale(vertex)
            color = color.toTk()
            item_id = self.create_oval(
                x-radius,
                y-radius,
                x+radius,
                y+radius,
                fill=color
            )
            self.graphicsItem2Process[item_id] = process

        def e_draw(edge, color=Color.black):
            start, end = edge
            start, end = scale(start), scale(end)
            x1,y1 = start
            x2,y2 = end
            color = color.toTk()
            self.create_line(x1, y1, x2, y2, fill=color)

        self.delete(ALL)
        network.general_draw(v_draw, e_draw)

class ToolTip(Toplevel):
    def __init__(self, parent, process, x, y):
        Toplevel.__init__(self, parent)
        self.wm_overrideredirect(True)
        self.wm_geometry("+%d+%d" % (x+25,y+20))
        label = Label(self, text="", justify='left',
                       background='white', relief='solid', borderwidth=1,
                       font=("times", "12", "normal"))
        label.pack(ipadx=20)
        tree = Treeview(label)
        tree["columns"] = ("value")
        tree.column("#0", minwidth=0, width=100)
        tree.column("#1", minwidth=0, width=100)
        tree.heading("#0", text="Name")
        tree.heading("#1", text="Value")

        for A, state in process.state.items():
            if isinstance(A, Algorithm):
                tree.insert("", 0, iid=A, text=str(A), values=("",))
                for key, val in state.items():
                    tree.insert(A, 0, text=key, values=(val,))
        for key, val in process.state.items():
            if not isinstance(key, Algorithm):
                tree.insert("", 0, text=key, values=(val,))
        tree.insert("", 0, text="UID", values=(process.UID,))
        tree.pack()

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
    from algs import LCR, SynchBFS
    
    x = Bidirectional_Ring(5)
    LCR(x)
    simulate(x)

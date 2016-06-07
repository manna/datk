"""
Algorithm step by step visualizer

Tk based GUI. Used by Network.start_simulation
"""
import matplotlib 
matplotlib.use('TkAgg')
#matplotlib.use('Agg')
from matplotlib import pyplot as plt
import Tkinter as tk
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler

LARGE_FONT=('Verdana',12)
class VizApp(tk.Tk):

    def __init__(self, network):
        
        tk.Tk.__init__(self)
        #tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "DATK Visualization")     
        
        self.frames = {}
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = False)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for F in (StartPage, GraphPage):
            frame = F(container, self, network)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(GraphPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        
    def terminate(self):
        self.quit()
        self.destroy()
        print "VizApp terminated"

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller,network):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = tk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(GraphPage))
        button.pack()
        
        
class GraphPage(tk.Frame):

    def __init__(self, parent, controller, network):
        tk.Frame.__init__(self, parent)
        self.network = network
        self.label = tk.Label(self, text="DATK simulation page!", font=LARGE_FONT)
        self.button_home = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        self.n_steps = 100
        if len(network._snapshots) > 0:
            self.n_steps = len(network._snapshots)
            
        self.slider = tk.Scale(self, from_=0, to=self.n_steps-1, length=300,orient=tk.HORIZONTAL, command=self.updateValue)

        self.label.pack(pady=10,padx=10)
        self.button_home.pack()
        self.slider.pack()

        
        self.canvas = FigureCanvasTkAgg(network.fig, self)
        self.ax = network.ax
        #canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def updateValue(self, event):
        print self.slider.get()
        self.network.restore_snapshot(self.slider.get())
        # print 'restored snapshot to the slider value'
        # print self.network.state()
        self.network.draw(new_fig=False)
        self.canvas.show()
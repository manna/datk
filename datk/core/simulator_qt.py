from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import (QMainWindow, QWidget, QApplication, QVBoxLayout,
     QSlider, QHBoxLayout, QPushButton, QGraphicsLineItem, QGraphicsScene, 
     QGraphicsEllipseItem, QGraphicsView, QBrush, QColor, QPen)
from PyQt4.QtCore import QPointF, Qt, SIGNAL
from colorizer import Color
from distalgs import Algorithm


class Canvas(QGraphicsView):
   patterns = [ Qt.BDiagPattern, Qt.ConicalGradientPattern, Qt.CrossPattern,
      Qt.Dense1Pattern, Qt.Dense2Pattern, Qt.Dense3Pattern, Qt.Dense4Pattern,
      Qt.Dense5Pattern, Qt.Dense6Pattern, Qt.Dense7Pattern, Qt.DiagCrossPattern,
      Qt.FDiagPattern, Qt.HorPattern, Qt.LinearGradientPattern, Qt.NoBrush,
      Qt.RadialGradientPattern, Qt.SolidPattern, Qt.VerPattern ]

   def __init__(self):
      super(Canvas, self).__init__()
      app = QtGui.QApplication.instance()
      app.setStyleSheet("""
      QToolTip {
       padding: 5px;
       border-radius: 3px;
      }
      """)
   
   @staticmethod
   def line(scene, x1, y1, x2, y2, color="blue", width=5):
      item = QGraphicsLineItem(x1, y1, x2, y2)
      pen = QPen(QColor(color))
      pen.setWidth(width)
      item.setPen(pen)
      scene.addItem(item)

   @staticmethod
   def point(scene, x, y, color='black', fill='black', diam=10, toolTip=None):
      item = QGraphicsEllipseItem(x-diam/2, y-diam/2, diam, diam)
      brush = QBrush(QColor(color), style=Qt.SolidPattern)
      item.setBrush(brush)
      if toolTip:
         item.setToolTip(toolTip)
      scene.addItem(item)

   def draw(self, network):
      scene = QGraphicsScene(self)
      SCALE = min(self.size().width(), self.size().height())

      def v_draw(vertex, process, color=Color.black):
         x, y = vertex
         color = color.toQt()

         tr = lambda col1,col2:'<tr><td>'+str(col1)+'</td><td>'+str(col2)+'</td></tr>'
         table_open = '<table border="1" cellspacing="0" cellpadding="5" style="border-color:black; border-style:solid; padding:0;">'
         table_close = '</table>'

         toolTip = '<b>' + str(process) + ':</b>'
         toolTip+=table_open
         for key, val in process.state.items():
            if not isinstance(key, Algorithm):
               toolTip+=tr(key, val)
         toolTip+=table_close

         for key, val in process.state.items():
            if isinstance(key, Algorithm):
               toolTip+='<p><i>'+str(key)+'</i></p>'
               toolTip+=table_open
               for k, v in val.items():
                  toolTip+=tr(k, v)
               toolTip+=table_close

         Canvas.point(scene, x*SCALE, y*SCALE, color=color, fill=color, toolTip=toolTip)

      def e_draw(edge, color=Color.black):
         start, end = edge
         color = color.toQt()
         x1,y1 = start
         x2,y2 = end
         Canvas.line(scene, x1*SCALE, y1*SCALE, x2*SCALE, y2*SCALE, color=color)

      network.general_draw(v_draw, e_draw)
      
      self.setScene(scene)


class Simulator(QMainWindow):

   def __init__(self, network):
      super(Simulator, self).__init__()
      x, y, w, h = 100, 100, 800, 500
      self.setGeometry(x, y, w, h)

      # Network
      self.network = network

      # Canvas
      self.canvas = Canvas()

      #Controls
      self.slider = QSlider(Qt.Horizontal, self)
      self.slider.setMaximum(self.network.count_snapshots()-1)
      self.slider.setTickPosition(QSlider.TicksBelow)
      self.slider.setTickInterval(1)
      self.connect(self.slider, SIGNAL("valueChanged(int)"), self.draw_network)
      self.prevButton = QPushButton(u"\u25C0")
      self.connect(self.prevButton, SIGNAL("clicked()"), self.onClickPrev)
      self.nextButton = QPushButton(u"\u25B6")
      self.connect(self.nextButton, SIGNAL("clicked()"), self.onClickNext)

      controls = QHBoxLayout()
      controls.addWidget(self.prevButton)
      controls.addWidget(self.slider)
      controls.addWidget(self.nextButton)

      #Main Layout
      mainLayout = QVBoxLayout()
      mainLayout.addWidget(self.canvas)
      mainLayout.addLayout(controls)

      self.widget = QtGui.QWidget()
      self.widget.setLayout(mainLayout)
      self.setCentralWidget(self.widget)

      self.setWindowTitle('DATK Simulator')

      #Reset Network and draw in starting state
      self.draw_network(0)


   def draw_network(self, value):
      self.network.restore_snapshot(value)
      self.canvas.draw(self.network)

   def onClickPrev(self):
      v = self.slider.value()
      if v > 0:
         self.slider.setValue(v-1)

   def onClickNext(self):
      v = self.slider.value()
      if v < self.slider.maximum():
         self.slider.setValue(v+1)

   def closeEvent(self, event): 
      self.network.restore_snapshot(-1)
      self.deleteLater() 


def simulate(network):
   import sys

   app = QtGui.QApplication.instance() # checks if QApplication already exists 
   if not app:
      app = QtGui.QApplication(sys.argv)
      app.aboutToQuit.connect(app.deleteLater)
      form = Simulator(network)
      form.show()
      app.exec_()
   else:
      print "A pyqt application alraedy exists. Please close it first."


def draw(network):
   import sys

   app = QtGui.QApplication.instance()
   if not app:
      app = QtGui.QApplication(sys.argv)
      app.aboutToQuit.connect(app.deleteLater)
      c = Canvas()
      c.draw(network)
      c.show()
      app.exec_()
   else:
      print "A pyqt application alraedy exists. Please close it first."

if __name__ == '__main__':
   from networks import *
   from algs import *
   x = Bidirectional_Ring(20)
   LCR(x)
   SynchBFS(x)
   draw(x)
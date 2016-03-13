import sys
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import RamanData as rd
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication,
    QBoxLayout, QSizePolicy, QWidget, QTabWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class RGui(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("RGui")

        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction('&Open', self.openFile,
            QtCore.Qt.CTRL + QtCore.Qt.Key_O)

        self.mainWidget = QWidget(self)

        layout = QBoxLayout(QBoxLayout.LeftToRight, self.mainWidget)
        self.canvas = CanvasWidget(self.mainWidget,
            width = 10, height = 8, dpi = 100)
        layout.addWidget(self.canvas)

        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)

        self.statusBar()

    def openFile(self):
        fileName = QFileDialog.getOpenFileName(self, "Open file", '/home')
        if fileName[0]:
            self.spec = rd.SpecData(fileName[0])

        self.canvas.updatePlot(self.spec)

class MyBaseCanvas(FigureCanvas):

    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
        fig = Figure(figsize = (width, height), dpi = dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)

        self.computeInitialFigure()

        super().__init__(fig)
        self.setParent(parent)

        super().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        super().updateGeometry()

    def computeInitialFigure(self):
        pass

class CanvasWidget(MyBaseCanvas):

    def updatePlot(self, spec):
        self.axes.plot(spec._data[[0]].T, spec._data[1:].T)
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = RGui()
    mw.setWindowTitle("Raman Gui")
    mw.show()
    sys.exit(app.exec_())

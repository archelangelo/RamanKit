#!/usr/bin/env python3
# Defines the GUI of Raman Kit
#
# This is part of a Raman spectrum analysis toolkit.
#
# Yiran Hu (yiranhu@gatech.edu)
# Epitaxial Graphene Lab
# School of Physics
# Georgia Tech

import sys
import os.path
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import RamanData as rd
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication,
    QBoxLayout, QSizePolicy, QWidget, QTabWidget, QListWidget, QListWidgetItem)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class RGui(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main window set up
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("RGui")

        # File menu and Open action
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction('&Open', self.openFile,
            QtCore.Qt.CTRL + QtCore.Qt.Key_O)

        # Main widget and its layout
        self.mainWidget = QWidget(self)
        layout = QBoxLayout(QBoxLayout.LeftToRight, self.mainWidget)
        self.subWidget = QWidget(self.mainWidget)
        subLayout = QBoxLayout(QBoxLayout.TopToBottom, self.subWidget)

        # Plot canvas set up, added to layout
        self.canvas = CanvasWidget(self.mainWidget,
            width = 5, height = 4, dpi = 100)
        layout.addWidget(self.canvas)

        # List widget embedded in Tab widget
        self.selectPane = QTabWidget(self.subWidget)
        listWidget = QListWidget(self.selectPane)
        self.selectPane.addTab(listWidget, 'Untitled')
        self.firstPlot = True
        self.spec = []

        subLayout.addWidget(self.selectPane)
        layout.addWidget(self.subWidget)

        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)
        self.statusBar()

    def openFile(self):
        fileName = QFileDialog.getOpenFileName(self, "Open file", '/home/workspace/RamanKit/')
        if fileName[0]:
            self.spec.append(rd.SpecData(fileName[0]))

        if self.firstPlot:
            listWidget = self.selectPane.currentWidget()
            self.selectPane.setTabText(0, os.path.basename(fileName[0]))
        else:
            listWidget = QListWidget(self.selectPane)
            self.selectPane.addTab(listWidget, os.path.basename(fileName[0]))

        for i in range(self.spec[-1]._coord.shape[0]):
            newItem = QListWidgetItem("[%d %d %d]" % \
                tuple(self.spec[-1]._coord[i]), listWidget)
            newItem.setData(0x0100, QtCore.QVariant([len(self.spec) - 1, i]))
            listWidget.addItem(newItem)
        listWidget.itemDoubleClicked.\
            connect(self.updatePlot)

    def updatePlot(self, item):
        bArray = item.data(0x0100)
        n = int(bArray[0])
        i = int(bArray[1])
        use = np.array(i).reshape(-1)
        self.canvas.updatePlot(self.spec[n], use)

class CanvasWidget(FigureCanvas):

    def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
        fig = Figure(figsize = (width, height), dpi = dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)

        super().__init__(fig)
        self.setParent(parent)

        super().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        super().updateGeometry()

    def updatePlot(self, spec, use):
        self.axes.plot(spec._data[[0]].T, spec._data[use].T)
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = RGui()
    mw.setWindowTitle("Raman Gui")
    mw.show()
    sys.exit(app.exec_())

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
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QApplication,
    QSplitter, QSizePolicy, QFrame, QTabWidget, QListWidget, QListWidgetItem,
    QHBoxLayout, QPushButton, QGridLayout, QAbstractItemView, QDoubleSpinBox,
    QSpinBox, QLabel)
# from Qt.QtGui import QDoubleValidator
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
        # subWidget is embedded in the right half of mainWidget
        self.mainWidget = QSplitter(QtCore.Qt.Horizontal, self)
        self.subWidget = QSplitter(QtCore.Qt.Vertical, self)

        # Plot canvas set up, added to layout
        self.canvas = CanvasWidget(self,
            width = 10, height = 8, dpi = 100)

        # Set up the control panel
        self.ctrPane = QTabWidget(self)
        self.initCtrPane()

        # List widget embedded in Tab widget
        self.selectPane = QTabWidget(self.subWidget)
        listWidget = QListWidget(self.selectPane)
        listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.selectPane.addTab(listWidget, 'Untitled')
        self.firstPlot = True
        self.spec = []

        # Set up the layouts
        self.mainWidget.addWidget(self.canvas)
        self.subWidget.addWidget(self.ctrPane)
        self.subWidget.addWidget(self.selectPane)
        self.mainWidget.addWidget(self.subWidget)

        # Set up the MainWindow
        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)
        self.setGeometry(300, 300, 500, 400)
        self.statusBar()

    def initCtrPane(self):
        # main control set up
        mainCtr = QFrame(self.ctrPane)
        mainCtr.setFrameShape(QFrame.StyledPanel)
        mainCtr.setFrameShadow(QFrame.Sunken)

        backSubButton = QPushButton('Background Subtraction', mainCtr)
        backSubButton.clicked.connect(self.backSub)

        mainLayout = QGridLayout(mainCtr)
        mainLayout.addWidget(backSubButton, 0, 0)
        mainCtr.setLayout(mainLayout)

        self.ctrPane.addTab(mainCtr, 'Main Ctrol')

        NMFCtr = QFrame(self.ctrPane)
        NMFCtr.setFrameShape(QFrame.StyledPanel)
        NMFCtr.setFrameShadow(QFrame.Sunken)

        self.alphaBox = MyDoubleSpinBox(NMFCtr)
        self.alphaE = ESpinBox(NMFCtr)
        self.l1RatioBox = MyDoubleSpinBox(NMFCtr)
        self.l1RatioE = ESpinBox(NMFCtr)
        NMFButton = QPushButton('NMF', NMFCtr)
        NMFButton.clicked.connect(self.NMF)

        NMFLayout = QGridLayout(NMFCtr)

        NMFLayout.addWidget(self.alphaBox, 0, 0)
        NMFLayout.addWidget(QLabel('E'), 0, 1)
        NMFLayout.addWidget(self.alphaE, 0, 2)

        NMFLayout.addWidget(self.l1RatioBox, 1, 0)
        NMFLayout.addWidget(QLabel('E'), 1, 1)
        NMFLayout.addWidget(self.l1RatioE, 1, 2)

        NMFLayout.addWidget(NMFButton, 2, 0, 1, 3)

        NMFCtr.setLayout(NMFLayout)

        self.ctrPane.addTab(NMFCtr, 'NMF Control')

    def openFile(self):
        fileName = QFileDialog.getOpenFileName(self, "Open file")
        if fileName[0]:
            self.addSpec(rd.SpecData(fileName[0]), os.path.basename(fileName[0]))

    def addSpec(self, spec, title):
        # import spectra from file
        self.spec.append(spec)
        if self.firstPlot:
            listWidget = self.selectPane.currentWidget()
            self.selectPane.setTabText(0, title)
            self.firstPlot = False
        else:
            listWidget = QListWidget(self.selectPane)
            listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.selectPane.addTab(listWidget, title)

        for i in range(self.spec[-1]._coord.shape[0]):
            newItem = QListWidgetItem("[%d %d %d]" % \
                tuple(self.spec[-1]._coord[i]), listWidget)
            newItem.setData(QtCore.Qt.UserRole, QtCore.QVariant([len(self.spec) - 1, i]))
            listWidget.addItem(newItem)
        listWidget.itemDoubleClicked.connect(self.updatePlot)

    def updatePlot(self, item):
        bArray = item.data(QtCore.Qt.UserRole)
        n = int(bArray[0])
        i = int(bArray[1])
        use = np.array(i).reshape(-1)
        self.canvas.updatePlot(self.spec[n], use)

    # Here comes the data analysis operations

    def backSub(self):
        if self.firstPlot:
            pass # raise an error

        fileName = QFileDialog.getOpenFileName(self, "Open background file")
        if fileName[0]:
            bg = rd.SpecData(fileName[0])
            listWidget = self.selectPane.currentWidget()
            item = listWidget.item(0)
            n = item.data(QtCore.Qt.UserRole)[0]
            newSpec = self.spec[n].backSub(bg.getSpec(0))
            self.addSpec(newSpec, self.currentTabText + '_subtracted')

    def NMF(self):
        if self.firstPlot:
            pass # raise an error

        item = self.selectPane.currentWidget().item(0)
        n = item.data(QtCore.Qt.UserRole)[0]
        alpha = self.alphaE.EValue(self.alphaBox)
        l1Ratio = self.l1RatioE.EValue(self.l1RatioBox)
        model = self.spec[n].NMF(n_components = 3, init = 'nndsvd',
            alpha = alpha, l1_ratio = l1Ratio, sparseness = 'data')
        newSpec = rd.SpecData()
        newSpec._data = np.append(self.spec[n]._data[[0]],
            model.components_, axis = 0)
        newSpec._coord = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]])
        newSpec._dim = np.array([1, 1, 3])
        self.addSpec(newSpec, self.currentTabTitle() + '_NMF')

    def currentTabTitle(self):
        return self.selectPane.tabText(self.selectPane.currentIndex())

class MyDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRange(0., 1.)
        self.setSingleStep(0.1)

class ESpinBox(QSpinBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRange(-100, 0)

    def EValue(self, doubleBox):
        t1 = doubleBox.text()
        t2 = self.text()
        return float(t1 + 'E' + t2)

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
        self.axes.plot(spec._data[[0]].T, spec._data[use + 1].T)
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = RGui()
    mw.setWindowTitle("Raman Gui")
    mw.show()
    sys.exit(app.exec_())

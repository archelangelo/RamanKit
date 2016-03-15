#!/usr/bin/env python3
# Defines the basic datatype used to store Raman spectra from
# Horiba Jobin-Yvon LabRam.
#
# This is part of a Raman spectrum analysis toolkit.
#
# Yiran Hu (yiranhu@gatech.edu)
# Epitaxial Graphene Lab
# School of Physics
# Georgia Tech

import numpy as np
import BackSub as bs
import sklearn.decomposition as skd

class SpecData():

    def __init__(self, fileName = None, a = None, b = None):
        if fileName is None:
            self._data = None
            self._coord = None
            self._dim = np.array([0, 1, 1])
        else:
            try:
                x = np.genfromtxt(fileName, delimiter = '\t')
            except Exception as e:
                print("Problem reading the file in __init__\nError message: ", \
                e)
                raise
            if not np.isnan(x[0, 0]): # Single point spectrum
                self._data = x.T
                self._coord = np.array([[0., 0., 0.]])
                self._dim = np.array([1, 1, 1])
            elif not np.isnan(x[0, 1]): # Line mapping spectra
                self._data = x[:, 1:]
                self._coord = np.zeros([x.shape[0] - 1, 3], dtype = float)
                self._coord[:, 0] = x[1:, 0]
                self._dim = np.array([self._coord.shape[0], 1, 1])
            else: # 2-D mapping
                self._data = x[:, 2:]
                self._coord = np.concatenate((x[1:, [0, 1]], \
                np.zeros([x.shape[0] - 1, 1])), axis = 1)
                # self._dim = np.array([self._coord.shape[0], 1])
                if a != None and b != None:
                    try:
                        self.setDim(a, b, 1)
                    except DimWarning:
                        print("Dimensions don't match the data size")
                        self.setDim(c = 2) # Find the dimensions automatically
                else:
                    self.setDim(c = 2)

    def copyFrom(self, target):
        self._data = target._data.copy()
        self._coord = target._coord.copy()
        self._dim = target._dim.copy()

    def getSpec(self, i):
        return self._data[[0, i + 1], :]

    def addSpec(self, fileName, coord):
        try:
            x = np.genfromtxt(fileName, delimiter = '\t')
        except Exception as e:
            print("Problem reading the file in addSpec\nError message: ", e)
            raise
        if np.isnan(x[0, 0]):
            raise SpectrumInputError()
        else:
            if self._data is None:
                self._data = x.T
                self._coord = coord
            else:
                self._data = np.concatenate((self._data, x[:, [1]].T))
                self._coord = np.concatenate((self._coord, coord))
            self.setDim(c = 1)

    def getCoord(self, i):
        return self._coord[i]

    def setDim(self, a = None, b = None, d = None, c = 0):
        # c = 0: set to a, b, d
        #     1: increase the 0th dim with the others = 1 (otherwise raise
        #        error)
        #     2: automatically decide the dimension based on the coordicates
        if c == 0:
            if a is None or b is None or d is None:
                raise ValueError("Invalid dimension arguments")
            self._dim = np.array([a, b, d], dtype = int)
            if a * b * d != self._data.shape[0] - 1:
                raise DimWarning()
        elif c == 1:
            self._dim[0] += 1
            if self._dim[1] != 1 or self._dim[2] != 1:
                raise DimWarning("Warning: tempting to increase 0th dimension \
                with others not being 1")
        elif c == 2:
            a = 1
            n = self._coord.shape[0]
            while a < n and self._coord[a, 0] == self._coord[a - 1, 0]:
                a += 1
            b = int(n / a)
            d = 1
            self._dim = np.array([a, b, d], dtype = int)
            if n % a != 0:
                raise DimWarning("Warning: auto dimension not devisible")

    def backSub(self, bg, st = 1700, nd = 2100):
        n = self._data.shape[0]
        newSpec = SpecData()
        newSpec.copyFrom(self)
        for i in range(0, n - 1):
            x = self.getSpec(i)
            y = bs.backSub(x, bg, shft = np.nan)
            newSpec._data[i + 1] = y[0]
        return newSpec

    def NMF(self, use = None, *args, **kwargs):
        self.baseSub()
        self.normalize()
        if not use is None:
            use = np.array(use) + 1
            x = self._data[use]
        else:
            x = self._data[1:]
        t = skd.NMF(*args, **kwargs)
        t.fit(x)
        return t

    def baseSub(self):
        m = self._data[1:].min(1)
        for i in range(0, m.shape[0]):
            self._data[i + 1] -= m[i]

    def normalize(self):
        m = self._data[1:].max()
        self._data[1:] /= m

class SpectrumInputError(Exception):

    def __init__(self, msg = "Single spectrum expected\nMultiple found"):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class DimWarning(Exception):

    def __init__(self, msg = "Warning: Dimension mismatch"):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

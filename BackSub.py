#!/usr/bin/env python3
# backSub() function takes in the Raman spectrum and corresponding
# background, fits the background to the spectrum and subtracts it.
#
# This is part of a Raman spectrum analysis toolkit.
#
# Yiran Hu (yiranhu@gatech.edu)
# Epitaxial Graphene Lab
# School of Physics
# Georgia Tech


import numpy as np
from matplotlib import pyplot
from numpy import sum

def backSub(X, Y, st = 1700, nd = 2100, shft = 0, plt = False):
    if np.isnan(shft):
        sqdmin = np.inf
        for i in range(-5, 6):
            ans = backSub(X, Y, st, nd, i)
            if ans[1] < sqdmin:
                sqdmin = ans[1]
                bestAns = ans
        return bestAns
    else:
        d0 = X[0]
        d1 = X[1]
        if X.shape[1] != Y.shape[1] or X[0, 0] != Y[0, 0]:
            raise BackgroundError("Background doesn't match")
        d2 = Y[1]
        if shft != 0:
            nans = np.empty([abs(shft)])
            nans[:] = np.nan
            if shft > 0:
                d2 = np.concatenate((nans, d2[0:-shft]))
            elif shft < 0:
                d2 = np.concatenate((d2[-shft:], nans))

        msk = (d0 > st) & (d0 < nd)
        x = d1[msk]
        y = d2[msk]
        A = np.matrix([[sum(y**2), sum(y)], [sum(y), y.shape[0]]])
        B = np.matrix([[sum(x*y)], [sum(x)]])
        sol = A.I * B
        d3 = d2 * (sol[0, 0]) + sol[1, 0]
        d4 = d1 - d3
        diff = x - (y * (sol[0, 0]) + sol[1, 0])
        sqd = sum(diff**2)
        d1 = d1.reshape([-1, 1])
        d3 = d3.reshape([-1, 1])
        d4 = d4.reshape([-1, 1])
        if plt:
            l1, l2, l3 = pyplot.plot(d0, np.concatenate((d1, d3, d4), axis = 1))
            pyplot.show()
        return (d4.reshape([-1]), sqd, shft, d3.reshape([-1]))

class BackgroundError(Exception):

    def __init__(self, msg = None):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

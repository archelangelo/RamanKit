import numpy as np
import RamanData as rd
from matplotlib import pyplot

spec = rd.SpecData()
for i in range(1, 14):
    fn = 'JanData/p%d.txt' % i
    spec.addSpec(fn, np.array([[0, 0, i]]))
ans = spec.NMF()
comp = ans.components_
x = spec._data[[0], :]
l = pyplot.plot(x.T, comp.T)
pyplot.show()
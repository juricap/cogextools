
import sys
sys.path.append('..')

from pylab import *
from cogextools import *

fname = '../data/wacom_CDT.f8'
a = penopen(fname)
ins = segments(a)
# find the longest segment (the circle clock outline)
i = argmax(diff(ins))
cdt = a[ins[i,0]:ins[-2,1]]

fname = '../data/wacom_spiral_s1.f8'
a = penopen(fname)
ins = segments(a)
# find the longest segment (the spiral)
i = argmax(diff(ins))
spiral = a[ins[i,0]:ins[-2,1]]

figure(figsize=(12,5))

ax = subplot(121)
strokes(cdt,alpha=0.1)
ax.invert_yaxis()

ax = subplot(122)
# draw only about 1000 points, nicer for SVG
di = int(floor(spiral.shape[0]//1000))
pressurec(spiral[::di])
ax.invert_yaxis()

show()


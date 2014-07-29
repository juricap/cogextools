"""
CogExTools by Peter Jurica (juricap@gmail.com), 2014
Cichocki Laboratory for Advanced Brain Signal Processing, RIKEN BSI

cgtexam_preview.py FILE.(i4|f8)

    FILE.(i4|f8)   an '.i4' or '.f8' files recorded by cgtexam_ programs
    
CogExTools examination data preview.

"""

from cogextools import *

from numpy import *
from pylab import *
from matplotlib.collections import LineCollection

noshow = get_option(sys.argv,'noshow')

fname = 'data/wacom_spiral_s2.f8'
if len(sys.argv) > 1:
    fname = sys.argv[1]

a = penopen(fname)

figure(figsize=(14,5.2))
subplot(121)
strokes(a)
xlabel('X')
ylabel('Y')
axis('image')
gca().invert_yaxis()
xticks([]); yticks([])

subplot(122)
pressurec(a)
axis('image')
gca().invert_yaxis()
xlabel('X')
xticks([]); yticks([])

if os.path.exists('doc/source'):
    savefig('doc/source/%s.png'%psplit(fname)[1][:-3],bbox_inches='tight')

suptitle(fname,fontsize=14)

show()



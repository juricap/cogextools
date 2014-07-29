
import sys
sys.path.append('..')

from pylab import *
from cogextools import *

BASE = '../data/'
fnames = [ BASE+x for x in os.listdir(BASE) if 'spiral_' in x ]
#fnames = [ BASE+x for x in os.listdir(BASE) if 'spiraltest' in x ]
fnames.sort()

def get_spiral(fname):
    a = penopen(fname)
    ins = segments(a)
    i = argmax(diff(ins))
    return a[ins[i,0]+10:ins[i,1]-10]

cnv = lambda x,N: convolve(x,ones(N,'f8'),'same')

data = [ get_spiral(fname) for fname in fnames ]

figure(figsize=(12,5))

for a in data:
    t = a[:,0] - a[0,0]
    print diff(t).mean()
    
    a[:,2:5] /= 2.0
    sa = c_[cnv(a[:,2],20),cnv(a[:,3],20), cnv(a[:,3],20)]
    v = sqrt(gradient(sa[:,0],t[1]-t[0])**2 + gradient(sa[:,1],t[1]-t[0])**2 + gradient(sa[:,2],t[1]-t[0])**2)
    v0 = v.mean()
    dt = a[-1,0]-a[0,0]
    d0 = sqrt((diff(sa,1,0)**2).sum(1)).sum()/1000.0
    d1 = sqrt((diff(a[:,2:4],1,0)**2).sum(1)).sum()/1000.0
    
    p = a[:,5]/1023.0
    #n = a[:,6]/3600.0
    n = a[:,7]/900.0/pi*180.0
    print 
    subplot(321)
    plot(t,v/1000.0)
    #xt,xtl = xticks()
    xt = arange(-30,31,15)
    xticks(xt,['']*len(xt))
    yticks([0,2,4,6])
    axis([0,25,0,7.5])
    ylabel('Speed\n[m/s]')
    #plot(xlim(),r_[d0,d0]/dt,'k--')
    #plot(xlim(),r_[d1,d1]/dt,'r--')

    subplot(323)
    plot(t,p)
    xt,xtl = xticks()
    xticks(xt,['']*len(xt))
    axis([0,25,0,1])
    ylabel('normalized\npressure')

    subplot(325)
    plot(t,n)
    yticks([15,30,45,60])
    axis([0,25,25,60])
    ylabel('altitude\n[deg]')


    ax = subplot(122)
    r = sqrt(((a[:,2:4]-a[0,2:4])**2).sum(1))
    w = unwrap(arctan2(a[:,2]-a[0,2],a[:,3]-a[0,3]))
    plot(w,r)
    k = polyfit(w,r,1)
    plot(w,k[0]*w+k[1],'k--')
    for direction in ["right", "top"]:
        ax.spines[direction].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.invert_xaxis()

xlabel('angle from origin')
ylabel('radius [mm]')

from mpl_toolkits.axes_grid1.inset_locator import inset_axes

inset_axes = inset_axes(ax, width="30%", height = "30%", loc=2)

for a in data:
    r = sqrt(((a[:,2:4]-a[0,2:4])**2).sum(1))
    w = unwrap(arctan2(a[:,2]-a[0,2],a[:,3]-a[0,3]))
    k = polyfit(w,r,1)
    N,b = histogram(r-(k[0]*w+k[1]),101,normed=True)
    plot(b[:-1] + diff(b)/2,cnv(N,15))

for direction in ["left", "right", "top"]:
    inset_axes.axis[direction].set_visible(False)

xticks(arange(-30,31,15),fontsize=8)
xlabel('radius error')

savefig('figure3c.svg')

show()


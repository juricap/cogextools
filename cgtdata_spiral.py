
import sys
from numpy import *
from pylab import *
from matplotlib.collections import LineCollection

from scipy.signal import fftconvolve
cnv = lambda x,N: fftconvolve(x,ones(N,'f8'),'same')

try:
    noshow = sys.argv.index('noshow')
    sys.argv.pop(noshow)
except:
    noshow = False

def fixdiv(a,b):
    temp = (a/b) << 16
    rem = a%b
    btemp = b
    if int(btemp) < 256:
        rem <<= 8
    else:
        btemp >>= 8
    temp += (rem/btemp) << 8
    rem %= btemp
    rem << 8
    temp += rem /btemp
    return temp

def penopen(fname,x01):
    if fname.endswith('i4'):
        a = fromfile(fname,'i4').reshape(-1,13)
    else:
        a = fromfile(fname,'f8').reshape(-1,14)
    # scaling factors in thousandths of cm per axis unit
    #axResolution = 131072000
    #A = (1000.0/0.0254)/axResolution
    Ax = 10000.0/65023#/2.54
    Ay = 10000.0/40639#/2.54
    a[:,2] *= Ax
    a[:,3] *= Ay
    on = a[:,1] == 1
    of = logical_not(on)
    i0,i1 = x01
    a0 = a[i0:i1]
    return a, on, of, a0

def showtrace(a,p=4.0):
    p = (a[:,5]/a[:,5].max())**p
    plot(a[:,0]-a[0,0],p)

def pressurec(a,p=4.0):
    p = (a[:,5]/a[:,5].max())**p
    sz = 20*p
    col = cm.jet(p)
    return scatter(a[:,2],a[:,3],s=sz**2,c=col,edgecolors='none',alpha=0.25)

def strokes(a,p=4.0,alpha=0.25,step=1):
    p = (a[:,5]/a[:,5].max())**p
    sz = 20*p
    
    segs = [[]]
    for i in xrange(a.shape[0]):
        if a[i,1] == 1:
            segs[-1].append(i)
        else:
            if len(segs[-1]) < 2:
                segs[-1] = []
            else:
                segs.append([])

    col = 'bgrcymk'*10
    for i in xrange(len(segs)):
        ins = segs[i][::step]
        scatter(a[ins,2],a[ins,3],c=col[i],s=sz[ins]**2,edgecolors='none',alpha=alpha)

    b = a.copy()
    b[(a[:,4]<16),:] = nan
    plot(b[:,2],b[:,3],'r')

    plot(a[0,2],a[0,3],'gd',lw=3.0,ms=10.0)
    plot(a[-1,2],a[-1,3],'kd',lw=3.0,ms=10.0)


fname = 'wacom_20140319141055.f8'; x01 = 3727,7890 # spiral
a2, on2, of2, a02 = penopen(fname,x01)

figure()
a = a2
i0, i1 = x01
p = (a[:,5]**4)/1e12
sz = 32*p
#cols = cm.jet(log(sz)/log(sz).max())
r = sqrt(((a[:,2:4]-a[0,2:4])**2).sum(1))
w = unwrap(arctan2(a[:,2]-a[0,2],-a[:,3]+a[0,3]))
k = polyfit(w,r,1)
y = k[0]*w+k[1]
cols = cm.jet((y-y.min())/(y.max()-y.min()))
won = scatter(a[i0:i1,2],a[i0:i1,3],s=sz[i0:i1]**2,c=cols,edgecolors='none',alpha=0.1)

figure()

# http://d.hatena.ne.jp/hiroki0/20101224/1293217750
for a in [a02]:
    t = a[:,0] - a[0,0]
    
    #sa = a[:,2:4].copy()
    sa = c_[cnv(a[:,2],20),cnv(a[:,3],20)]
    v = sqrt(gradient(sa[:,0],t[1]-t[0])**2 + gradient(sa[:,1],t[1]-t[0])**2)
    v0 = v.mean()
    dt = a[-1,0]-a[0,0]
    d0 = sqrt((diff(sa,1,0)**2).sum(1)).sum()/1000.0
    d1 = sqrt((diff(a[:,2:4],1,0)**2).sum(1)).sum()/1000.0
    print d0, d1
    p = a[:,5]/1023.0
    #n = a[:,6]/3600.0
    n = a[:,8]/900.0/pi*180.0
    subplot(321)
    plot(t,v/1000.0)
    xt,xtl = xticks()
    xticks(xt,['']*len(xt))
    axis([0,25,0,1])
    ylabel('Speed\n[m/s]')
    plot(xlim(),r_[d0,d0]/dt,'k--')
    plot(xlim(),r_[d1,d1]/dt,'r--')

    subplot(323)
    plot(t,p)
    xt,xtl = xticks()
    xticks(xt,['']*len(xt))
    axis([0,25,0,1])
    ylabel('normalized\npressure')

    subplot(325)
    plot(t,n)
    axis([0,25,30,60])
    yticks([30,45,60])
    ylabel('altitude\n[deg]')


    subplot(122)
    r = sqrt(((a[:,2:4]-a[0,2:4])**2).sum(1))
    w = unwrap(arctan2(a[:,2]-a[0,2],-a[:,3]+a[0,3]))
    plot(w,r)
    k = polyfit(w,r,1)
    plot(w,k[0]*w+k[1],'k--')

xlabel('angle from origin')
ylabel('radius [mm]')

"""figure()
#hist(r-(k[0]*w+k[1]),101)
N,b = histogram(r-(k[0]*w+k[1]),41)
plot(b[:-1] + diff(b)/2,N)"""

figure()
for a in [a02]:
    r = sqrt(((a[:,2:4]-a[0,2:4])**2).sum(1))
    w = unwrap(arctan2(a[:,2]-a[0,2],-a[:,3]+a[0,3]))
    k = polyfit(w,r,1)
    N,b = histogram(r-(k[0]*w+k[1]),101,normed=True)
    plot(b[:-1] + diff(b)/2,cnv(N,15))

show()


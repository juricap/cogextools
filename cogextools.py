
from __future__ import print_function

VERSION = '1.0'
AUTHOR = 'Peter Jurica (juricap@gmail.com)'

import os
from os.path import join as pjoin, split as psplit
import sys
import time

_cgtpath = psplit(__file__)[0]
pkg = pjoin(_cgtpath,'cogex_packages.zip')
sys.path[:0] = [pkg]

import zipfile
_zp = zipfile.ZipFile(pkg)
_DIR = pjoin(_cgtpath,'cogex_packages')
if not os.path.exists(_DIR):
    os.mkdir(_DIR)
    files  = ['_wintab.pyd','boost_python-vc90-mt-1_52.dll']
    files += [x for x in _zp.namelist() if x.startswith('cairo') ]
    for x in files: _zp.extract(x,_DIR)

ppath = os.path.abspath(_DIR)
sys.path[:0] = [ppath]
os.environ['PATH'] += ';'+ppath

del zipfile, _zp, _DIR

from os.path import join as pjoin, split as psplit

def debug(*args):
    print(*args)
    print()

def error(msg,exc):
    print(msg)
    if exc:
        print(exc)
    print()

def askfile():
    out = ''
    from ctypes.wintypes import DWORD,HWND,HINSTANCE,LPSTR,LPCSTR,BOOL,WORD
    from ctypes import windll, Structure, c_voidp, POINTER, sizeof, \
                       create_string_buffer, byref
    class OPENFILENAME(Structure):
        _fields_ = [('lStructSize', DWORD),
                ('hwndOwner', HWND),
                ('hInstance', HINSTANCE),
                ('lpstrFilter', LPCSTR), 
                ('lpstrCustomFilter', LPSTR), 
                ('nMaxCustFilter', DWORD),
                ('nFilterIndex', DWORD),
                ('lpstrFile', LPSTR), 
                ('nMaxFile', DWORD),
                ('lpstrFileTitle', LPSTR), 
                ('nMaxFileTitle', DWORD),
                ('lpstrInitialDir', LPCSTR),
                ('lpstrTitle', LPCSTR), 
                ('Flags', DWORD),
                ('nFileOffset', WORD),
                ('nFileExtension', WORD),
                ('lpstrDefExt', LPCSTR), 
                ('lCustData', DWORD),
                ('lpfnHook', c_voidp),
                ('lpTemplateName', LPCSTR)]

    GetOpenFileName = windll.comdlg32.GetOpenFileNameA
    GetOpenFileName.argtypes = [POINTER(OPENFILENAME)]
    GetOpenFileName.restype = BOOL
    OFN_READONLY = 0x00000001
    OFN_EXPLORER = 0x00080000

    filt = ['Executables (*.exe)','*.exe',
            'All files (*.*)','*.*',
            '\0']
    filt = '\0'.join(filt)

    ofn = OPENFILENAME()
    ofn.lStructSize = sizeof(ofn)
    ofn.hwndOwner = 0
    ofn.hInstance = windll.kernel32.GetModuleHandleW(None)
    ofn.Flags = OFN_READONLY | OFN_EXPLORER
    ofn.lpstrFilter = filt
    ofn.lpstrFile = '\0'*260
    ofn.nMaxFile = 260
    ok = GetOpenFileName(byref(ofn))
    if ok:
        out = ofn.lpstrFile
    return out

def remote_commands():
    def remote_server(messages):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('',12999))
        sock.listen(1)
        while True:
            (conn,addr) = sock.accept()
            while True:
                msg = conn.recv(4)
                if not msg: break
                messages.append(msg)
                #if messages[-1] == 'quit': break;
    
    messages = []
    from threading import Thread
    thr = Thread(None,remote_server,'CGTREMOTE',(messages,))
    thr.daemon = True
    thr.start()
    return messages

def remote_control(ip='localhost',port=12999):
    import socket
    def connect(ip,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ip,port))
        except:
            sock = None
        return sock

    class Sock:
        def __init__(self,ip,port):
            self.sock = connect(ip,port)
        def __call__(self,msg):
            try:
                self.sock.send(msg)
            except Exception as exc:
                debug('Trying to connect to server ...')
                self.sock = connect(ip,port)
                try: self.sock.send(msg)
                except: pass
    return Sock(ip,port)

def get_option(argv,option):
    out = False
    try:
        out = sys.argv.index(option)
        out = sys.argv.pop(out)
    except:
        pass
    return out

from numpy import *
try:
    from scipy.signal import fftconvolve
    cnv = lambda x,N: fftconvolve(x,ones(N,'f8'),'same')
except:
    cnv = lambda x,N: convolve(x,ones(N,'f8'),'same')

def segments(a):
    on = a[:,1] == 1
    of = logical_not(on)
    do = diff(on.astype('i4'))
    ins = c_[where(do>0)[0]+1,where(do<0)[0]+1]
    return ins
        
def penopen(fname):
    if 'tablet' in fname:
        x = fromfile(fname,'f8').reshape(-1,6)
        a = zeros((x.shape[0],13),'f8')
        a[:,3] = -a[:,3]
        a[:,:6] = x
    elif fname.endswith('i4'):
        a = fromfile(fname,'u4').reshape(-1,13).astype('f8')
        a[:,3] = -a[:,3]
    else:
        # original format of cogextools data files
        a = fromfile(fname,'f8').reshape(-1,14)
        # from: time, buttons, x, y, z, pressure, tilt, orient, rot, tpressure
        # to: time, buttons, x, y, z, pressure, orient, rot, tpressure
        a = a[:,[0, 1, 2,3,4, 5, 7,8,9, 10,11,12, 13]]
    return a

def showtrace(a,p=4.0):
    from pylab import plot
    p = (a[:,5]/a[:,5].max())**p
    plot(a[:,0]-a[0,0],p)

def pressurec(a,p=4.0):
    from pylab import scatter, cm
    p = (a[:,5]/a[:,5].max())**p
    sz = 20*p
    col = cm.jet(p)
    return scatter(a[:,2],a[:,3],s=sz**2,c=col,edgecolors='none',alpha=0.25)

def strokes(a,p=4.0,alpha=0.25,step=1):
    from pylab import scatter, plot
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

def demo_remote():
    print('Listening for commands: ')
    msg = remote_commands()
    i = 0
    while True:
        print(i, msg)
        time.sleep(0.5)
        i += 1

if __name__ == "__main__":
    demo_remote()


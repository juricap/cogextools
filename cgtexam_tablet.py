
from cogextools import *

import itertools as it
    
from pyglet import *
from pyglet.gl import *
from pyglet.window import mouse, key

import numpy as np

WINDOW = False
if '-w' in sys.argv:
    sys.argv.pop(sys.argv.index('-w'))
    WINDOW = True

DIR = '.'
if len(sys.argv) > 1:
    DIR = sys.argv[1]

PNGS = pjoin(DIR,'pngs')
sheets = [ pjoin(PNGS,x) for x in os.listdir(PNGS) if 'solution' not in x and x.endswith('.png') ]
sheets.sort()

class TWin(window.Window):
    def __init__(self,fullscreen=True,**kwargs):
        super(TWin,self).__init__(fullscreen=fullscreen,**kwargs)
        # drawing buffers
        self.Ndata = 1000
        self.data = np.zeros((self.Ndata,2),'f4') - 10
        self.i = 0
        self.colors = np.zeros((self.Ndata,4),'f4')
        self.colors[:,0] = 1.0
        self.colors[:,-1] = 1.0
        #
        self.times = []
        self.DEBUG = False
        #
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glTexEnvi(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPointSize(3.0)
        glLineWidth(3.0)
        glClearColor(1.0,1.0,1.0,1.0)
        #
        self.strokecolor = it.cycle([(0.0,0.0,1.0,1.0),(0.0,1.0,0.0,1.0),(1.0,0.0,0.0,1.0),
                                     (1.0,0.0,1.0,1.0),(1.0,1.0,0.0,1.0),(0.5,0.7,0.2,1.0)])
        
    def on_draw(self):
        self.clear()
        batch.draw()
        spr2.draw()
        if self.DEBUG:
            batch_d.draw()
        if self.i > 1:
            graphics.draw(self.i,GL_LINE_STRIP,('v2f',self.data[:self.i].ravel()),
                    ('c4f',self.colors[:self.i].ravel()))

    def on_key_press(self,s,m):
        if s == key.D:
            self.DEBUG = not self.DEBUG
        elif s == key.RIGHT:
            change_sheet(si+1)
        elif s == key.LEFT:
            change_sheet(si-1)
        elif s == key.ESCAPE:
            app.exit()
    def on_mouse_drag(self,x,y,dx,dy,b,m):
        global rfile
        if b & mouse.LEFT:
            if rfile: np.array((t.time(),1,x,y,0,200),'f8').tofile(rfile)
            self.data[self.i,:] = x, y
            self.i = (self.i+1)%self.Ndata
            ctx.line_to(x,y)
    def on_mouse_motion(self,x,y,dx,dy):
        global rfile
        if rfile:
            np.array((t.time(),0,x,y,50,0),'f8').tofile(rfile)
    def on_mouse_press(self,x,y,b,m):
        global rfile
        if b & mouse.LEFT:
            ctx.move_to(x,y)            
            # store data
            if rfile: np.array((t.time(),0,x,y,20,100),'f8').tofile(rfile)
            # reset gl_points buffer
            self.i = 0
            self.data[...] = -10
            # check for commands
            dt = t_tripple.tick()
            if dt < 0.35:
                self.times.append(dt)
                if len(self.times) == 3:
                    app.exit()
                elif len(self.times) == 2:
                    if x > int(0.9*self.width):
                        change_sheet(si+1)
                    elif x < int(0.1*self.width):
                        change_sheet(si-1)
            else:
                self.times = []
    def on_mouse_release(self,x,y,b,m):
        global rfile
        if self.i > 0:
            if rfile: np.array((t.time(),0,x,y,20,100),'f8').tofile(rfile)
            arr[:,:,:3] = 0
            a = self.data[:self.i]
            x0, y0 = a.min(0)
            x1, y1 = a.max(0)
            A = max(x1-x0,y1-y0)
            a = (0.5 + 15*(a - [x0,y0])/A).astype('i4')
            for x,y in a:
                arr[y,x,:3] = 255
            sprd.image = image.ImageData(16,16,'RGBA',arr.tostring())
            # update the cairo layer
            ctx.set_source_rgba(*self.strokecolor.next()) # Solid color
            ctx.set_line_width(3.5)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
            refresh()

def refresh():
    spr2.image = image.ImageData(win.width,win.height,'RGBA',path[:,:,[2,1,0,3]].tostring())

if WINDOW:
    win = TWin(fullscreen=False,width=1024,height=768)
else:
    win = TWin()

t = clock.Clock()
t_tripple = clock.Clock()

messages = remote_commands()
def update(dt):
    if messages:
        msg = messages.pop()
        if msg == 'next': change_sheet(si+1)
        elif msg == 'prev': change_sheet(si-1)
        elif msg == 'quit': app.exit()
        elif msg == 'info': app.exit()

clock.schedule_interval(update,1/100.0)

def load2spr(fname,batch=None):
    im = image.load(fname)
    spr = sprite.Sprite(im,batch=batch,usage='dynamic')
    r = 1.0/min(float(im.width)/win.width,float(im.height)/win.height)
    spr.scale = r
    spr.x = (win.width - r*im.width)//2
    spr.y = (win.height - r*im.height)//2
    return spr

batch = graphics.Batch()
batch_d = graphics.Batch()

spr0 = load2spr(sheets[0],batch)
spr1 = load2spr(sheets[0][:-4]+'_solution.png',batch_d)

path = np.zeros((win.height,win.width,4),'u1')
impath = image.ImageData(win.width,win.height,'RGBA',path.tostring())
spr2 = sprite.Sprite(impath)

import cairo
cim = cairo.ImageSurface.create_for_data(path,0,spr2.image.width,spr2.image.height,)
ctx = cairo.Context(cim)

from datetime import datetime as dtime
rfile = None
SESSION = 'data/tablet_ses%s'%dtime.strftime(dtime.now(),'%Y%m%d%H%M%S')
def record(name):
    global rfile
    if rfile:
        rfile.close()
        rfile = None
    # record
    oname = '%s[%s].f8'%(SESSION,name)
    if not os.path.exists('data'): os.mkdir('data')
    rfile = open(oname,'wb')
    print 'recording', oname
    return rfile

def change_sheet(nsi):
    global si
    nsi = max(0,min(len(sheets),nsi))
    if nsi != si:
        si = nsi
        name = sheets[si][:-4]
        spr0.image = image.load(name+'.png')
        spr1.image = image.load(name+'_solution.png')
        path[...] = 0
        refresh()
        record(os.path.split(name)[1])

arr = np.zeros((16,16,4),'u1')
arr[:,:,-1] = 255
img = image.ImageData(16,16,'RGBA',arr.tostring())
sprd = sprite.Sprite(img,win.width-4*16,0,batch=batch_d,usage='dynamic')
sprd.scale=4.0

si = -1
change_sheet(0)
app.run()


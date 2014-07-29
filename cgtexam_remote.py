"""
CogExTools by Peter Jurica (juricap@gmail.com), 2014
Cichocki Laboratory for Advanced Brain Signal Processing, RIKEN BSI

cgtexam_remote.py [-gui] [IP][]

    -gui      open graphical user interface

    IP        IP address of examination PC/tablet (default 127.0.0.1)
    PORT      network port of the examination PC/tablet (default 12999)
    
CogExTools examination remote control interface.

"""

from cogextools import *

from pyglet import *
from pyglet.window import key

if not '-gui' in sys.argv:
    import msvcrt
    print "Press "
    sys.exit(0)

win = window.Window(1024,768)

IP, PORT = '127.0.0.1',12999
if len(sys.argv) > 1: IP = sys.argv[1]
if len(sys.argv) > 2: IP = sys.argv[2]

remote = remote_control(IP,PORT)

batch = graphics.Batch()
_buts = []
def make_button(btext,event=None):
    global _buts, batch
    label = text.Label(btext,x=len(_buts)*150+20,y=20,font_size=20,bold=True,
                       width=150, multiline=True,batch=batch)
    _buts.append((label,event))

make_button('prev (<-)', lambda: on_key_press(key.LEFT,0))
make_button('next (->)', lambda: on_key_press(key.RIGHT,0))
make_button('quit ( s)', lambda: on_key_press(key.S,0))

@win.event
def on_key_press(symbol, modifiers):
    if symbol == key.ESCAPE:
        app.exit()
    elif symbol == key.LEFT:
        remote('prev')
    elif symbol == key.RIGHT:
        remote('next')
    elif symbol == key.S:
        remote('quit')

@win.event
def on_draw():
    win.clear()
    batch.draw()

app.run()


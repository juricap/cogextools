"""
CogExTools sheets.py
Peter Jurica (juricap@gmail.com), 2014

cgtmake_sheets.py [-y] DIRECTORY

    -y           overwrite existing files
    -nopdf       do not generate PDF files
    -c           combine

    DIRECTORY    folder containing SVG sheets (current directory is default)

This will attempt to translate all SVG files in DIRECTORY to

"""

from cogextools import *

import os
from os.path import join as pjoin
import sys
import tempfile
import subprocess as sp

PDFS = True
PNGS = True
OVER = False
COMBINE = False
DIR = '.'
DIRNAME = 'Sheets'

## parse input arguments
if len(sys.argv) == 1 or '-h' in sys.argv:
    print __doc__
    sys.exit(0)

if '-y' in sys.argv:
    OVER = True
    sys.argv.pop(sys.argv.index('-y'))

if '-nopdf' in sys.argv:
    PDFS = False
    sys.argv.pop(sys.argv.index('-nopdf'))

if '-c' in sys.argv:
    COMBINE = True
    PDFS = True
    sys.argv.pop(sys.argv.index('-c'))

if len(sys.argv) > 1:
    DIR = sys.argv[1]
    DIRNAME = os.path.split(os.path.abspath(DIR))[-1]

if not os.path.isdir(DIR):
    print >>sys.stderr, 'ERROR: "%s" is not a directory!'%sys.argv[1]
    sys.exit(1)

INKSCAPE = 'C:\Program Files (x86)\Inkscape\inkscape.exe'
if not os.path.exists(INKSCAPE):
    print 'Inkscape application not found at "%s",'%INKSCAPE
    while not os.path.exists(INKSCAPE):
        print 'Please provide a valid path or press ENTER to select:',
        INKSCAPE = raw_input()
        if not INKSCAPE.strip():
            INKSCAPE = askfile()
    import re
    code = open(__file__,'rb').read()
    NEWINKSCAPE = "INKSCAPE = '%s'"%INKSCAPE
    try:
        exec NEWINKSCAPE
        code = re.sub('^INKSCAPE = .*$',NEWINKSCAPE,code,1,re.M)
        open(__file__,'wb').write(code)
    except Exception as exc:
        error('INKSCAPE path setting failed. Edit "cgtmake_sheets.py" and set variable manually.')

## functions that do the work

def makedirs(pth):
    if os.path.exists(pth) and os.path.isdir(pth): return
    os.makedirs(pth)

def export(iname,oname):
    ext = os.path.splitext(oname)[1].lower()
    iname = os.path.normpath(os.path.abspath(iname))
    oname = os.path.normpath(os.path.abspath(oname))
    if ext == '.pdf':
        debug('SVG2PDF:', iname, oname)
        return sp.Popen([INKSCAPE,'--export-pdf='+oname,'--export-area-page',iname])
    elif ext == '.png':
        debug('SVG2PNG:', iname, oname)
        return sp.Popen([INKSCAPE,'--export-png='+oname,'--export-area-page',iname])
    else:
        raise Exception('Unsupported image format "%s".'%ext)

def make_pdfs(files):
    for x in files:
        pth, name = os.path.split(x)
        pth = pjoin(pth,'pdfs')
        name = os.path.splitext(name)[0]
        makedirs(pth)
        oname = pjoin(DIR,'pdfs','%s.pdf'%name)
        onames = pjoin(DIR,'pdfs','%s_solution.pdf'%name)
        if not OVER and os.path.exists(oname) and os.path.exists(onames):
            continue
        tmpfd, temp = tempfile.mkstemp('.svg','cogex_')
        open(temp,'wb').write(open(x,'rb').read().replace('style="display:none"','style="display:inline"'))
        try:
            pid1 = export(x,    oname)
            pid2 = export(temp, onames)
            pid1.wait()
            pid2.wait()
        except Exception as exc:
            error('Error converting "%s" to PDF.'%x, exc)
        os.close(tmpfd)
        os.unlink(temp)

def make_pngs(files):
    for x in files:
        pth, name = os.path.split(x)
        pth = pjoin(pth,'pngs')
        name = os.path.splitext(name)[0]
        makedirs(pth)
        oname = pjoin(DIR,'pngs','%s.png'%name)
        onames = pjoin(DIR,'pngs','%s_solution.png'%name)
        if not OVER and os.path.exists(oname) and os.path.exists(onames):
            continue
        svg = open(x,'rb').read()
        svg = svg.replace('style="display:inline"','')
        svg = svg.replace('style="display:none"','style="display:inline"')
        svg = svg.replace('id="layer1"','id="layer1" style="display:none"')
        tmpfd, temp = tempfile.mkstemp('.svg','cogex_')
        open(temp,'wb').write(svg)
        try:
            pid1 = export(x,    oname)
            pid2 = export(temp, onames)
            pid1.wait()
            pid2.wait()
        except Exception as exc:
            error('Error converting "%s" to PDF.'%x, exc)
        os.close(tmpfd)
        os.unlink(temp)

def make_book(files,oname):
    from pyPdf import PdfFileWriter, PdfFileReader
    print 'Generating PDF booklet.'
    output = PdfFileWriter()
    for x in files:
        print x
        input1 = PdfFileReader(file(x,'rb'))
        output.addPage(input1.getPage(0))

    outputStream = file(oname,'wb')
    output.write(outputStream)
    outputStream.close()

files = [ pjoin(DIR,x) for x in os.listdir(DIR) if x.endswith('.svg') ]

if PDFS:
    print 'Generating PDFs.'
    make_pdfs(files)
    if COMBINE:
        files = [ pjoin(DIR,'pdfs',x) for x in os.listdir(pjoin(DIR,'pdfs')) if x.endswith('.pdf') and 'solution' not in x ]
        files.sort()
        make_book(files,'%s.pdf'%DIRNAME)
        files = [ pjoin(DIR,'pdfs',x) for x in os.listdir(pjoin(DIR,'pdfs')) if x.endswith('_solution.pdf') ]
        files.sort()
        make_book(files,'%s_solution.pdf'%DIRNAME)

if PNGS:
    print 'Generating PNGs.'
    make_pngs(files)


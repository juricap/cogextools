
from __future__ import print_function

VERSION = '1.0'
AUTHOR = 'Peter Jurica (juricap@gmail.com)'

import os
import sys
sys.path[:0] = ['./cogex_packages.zip']

import zipfile
_zp = zipfile.ZipFile('./cogex_packages.zip')
_DIR = 'cogex_packages'
if not os.path.exists(_DIR):
    os.mkdir(_DIR)
    files  = ['_wintab.pyd','boost_python-vc90-mt-1_52.dll']
    files += [x for x in _zp.namelist() if x.startswith('cairo') ]
    for x in files: _zp.extract(x,_DIR)
del zipfile, _zp, _DIR

sys.path[:0] = ['./cogex_packages/']

def debug(*args):
    print(*args)
    print()

def error(msg,exc):
    print(msg)
    if exc:
        print(exc)
    print()


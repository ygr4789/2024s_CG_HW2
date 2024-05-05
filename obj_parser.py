import os, sys

from pyglet.math import Vec3
from pyglet.util import asstr

from geometry import *

default_cube_v = [
    [-1.0,  1.0,  1.0],
    [-1.0, -1.0,  1.0],
    [1.0, -1.0,  1.0],
    [1.0,  1.0,  1.0],
    [1.0, -1.0, -1.0],
    [1.0,  1.0, -1.0],
    [-1.0, -1.0, -1.0],
    [-1.0,  1.0, -1.0],
]
default_cube_f = [
    [0, 1, 2, 3],
    [3, 2, 4, 5],
    [5, 4, 6, 7],
    [7, 0, 3, 5],
    [7, 6, 1, 0],
    [6, 4, 2, 1],
]

def load_obj_to_vflist(filename, file=None):
    try:
        if file is None:
            with open(filename, 'r') as f:
                file_contents = f.read()
        else:
            file_contents = asstr(file.read())
    except (UnicodeDecodeError, OSError):
        raise Exception(f"model decode exception.")

    vlist = []
    flist = []

    for line in file_contents.splitlines():

        if line.startswith('#'):
            continue
        values = line.split()
        if not values:
            continue

        if values[0] == 'v':
            vlist.append(list(map(float, values[1:4])))

        elif values[0] == 'f':
            face = []

            for i, v in enumerate(values[1:]):
                v_i, t_i, n_i = (list(map(int, [j or 0 for j in v.split('/')])) + [0, 0])[:3]
                if v_i < 0:
                    v_i += len(vlist)
                v_i -= 1
                face.append(v_i)
            flist.append(face)

    return vlist, flist

def save_vflist_to_obj(filename, vlist, flist):
    try:
        with open(filename, 'w') as f:
            for l in vlist:
                data = "v %s\n" % ' '.join(map(str,l))
                f.write(data)
            for l in flist:
                l_ = [x + 1 for x in l]
                data = "f %s\n" % ' '.join(map(str,l_))
                f.write(data)
    except (UnicodeDecodeError, OSError):
        raise Exception(f"model save exception.")
    pass
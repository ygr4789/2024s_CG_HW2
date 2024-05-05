from pyglet.math import Mat4, Vec3, Vec4
from geometry.geom import Geometry
import numpy as np

class Cube(Geometry):
    '''
    default structure of cube
    '''
    def __init__(self, scale=Vec3(1.0, 1.0, 1.0), translate=Vec3()):
        super().__init__()

        self.vertices = [
            -0.5, -0.5,  -0.5,
            -0.5,  0.5,  -0.5,
            0.5, -0.5,  -0.5,
            -0.5,  0.5,  -0.5,
            0.5,  0.5,  -0.5,
            0.5, -0.5,  -0.5,

            -0.5, -0.5,   0.5,
            0.5, -0.5,   0.5,
            -0.5,  0.5,   0.5,
            -0.5,  0.5,   0.5,
            0.5, -0.5,   0.5,
            0.5,  0.5,   0.5,

            -0.5,   0.5, -0.5,
            -0.5,   0.5,  0.5,
            0.5,   0.5, -0.5,
            -0.5,   0.5,  0.5,
            0.5,   0.5,  0.5,
            0.5,   0.5, -0.5,

            -0.5,  -0.5, -0.5,
            0.5,  -0.5, -0.5,
            -0.5,  -0.5,  0.5,
            -0.5,  -0.5,  0.5,
            0.5,  -0.5, -0.5,
            0.5,  -0.5,  0.5,

            -0.5,  -0.5, -0.5,
            -0.5,  -0.5,  0.5,
            -0.5,   0.5, -0.5,
            -0.5,  -0.5,  0.5,
            -0.5,   0.5,  0.5,
            -0.5,   0.5, -0.5,

            0.5,  -0.5, -0.5,
            0.5,   0.5, -0.5,
            0.5,  -0.5,  0.5,
            0.5,  -0.5,  0.5,
            0.5,   0.5, -0.5,
            0.5,   0.5,  0.5,
        ]
        
        self.uvs = [
            0, 0,
            0, 1,
            1, 0,
            0, 1,
            1, 1,
            1, 0,
        ] * 6
        
        self.vertices = [scale[idx % 3] * x + translate[idx % 3] for idx,
                         x in enumerate(self.vertices)]

        self.normals = [0.0, 0.0, -1.0] * 6 \
                     + [0.0, 0.0, 1.0] * 6 \
                     + [0.0, 1.0, 0.0] * 6 \
                     + [0.0, -1.0, 0.0] * 6 \
                     + [-1.0, 0.0, 0.0] * 6 \
                     + [1.0, 0.0, 0.0] * 6

class Rod(Cube):
    def __init__(self, l=1.0, t=0.2, w=0.2):
        scale = Vec3(l, t, w)
        translate = Vec3(l/2, 0, 0)
        super().__init__(scale, translate)
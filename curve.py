import numpy as np
from pyglet.math import Vec3

from geometry import *
from const import *

class ControlSurface:
    def __init__(self) -> None:
        self.points: list[Vec3] = []
        for i in range(16):
            self.points.append(Vec3())
        self.step = 9
        self.use_bezier = True
        self.reset()

    def reset(self):
        self.points[0][:] = (-1.5, 0, -1.5)
        self.points[1][:] = (-0.5, 0, -1.5)
        self.points[2][:] = (0.5, 0, -1.5)
        self.points[3][:] = (1.5, 0, -1.5)
        self.points[4][:] = (-1.5, 0, -0.5)
        self.points[5][:] = (-0.5, 0, -0.5)
        self.points[6][:] = (0.5, 0, -0.5)
        self.points[7][:] = (1.5, 0, -0.5)
        self.points[8][:] = (-1.5, 0, 0.5)
        self.points[9][:] = (-0.5, 0, 0.5)
        self.points[10][:] = (0.5, 0, 0.5)
        self.points[11][:] = (1.5, 0, 0.5)
        self.points[12][:] = (-1.5, 0, 1.5)
        self.points[13][:] = (-0.5, 0, 1.5)
        self.points[14][:] = (0.5, 0, 1.5)
        self.points[15][:] = (1.5, 0, 1.5)

    def guide_lines(self):
        lines = []
        for i, p in enumerate(self.points):
            if i % 4 != 3:
                p_ = self.points[i + 1]
                lines += [*p.xyz, *p_.xyz]
            if i // 4 != 3:
                p_ = self.points[i + 4]
                lines += [*p.xyz, *p_.xyz]
        return lines

    def point_mat(self):
        g = np.array(
            [
                [self.points[0], self.points[1], self.points[2], self.points[3]],
                [self.points[4], self.points[5], self.points[6], self.points[7]],
                [self.points[8], self.points[9], self.points[10], self.points[11]],
                [self.points[12], self.points[13], self.points[14], self.points[15]],
            ]
        )

        bezier = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
        bspline = (
            np.array([[1, -3, 3, -1], [4, 0, -6, 3], [1, 3, 3, -3], [0, 0, 0, 1]]) / 6
        )
        
        b = bezier if self.use_bezier else bspline

        n = self.step
        dim = g.shape[2]

        arr = np.arange(n + 1) / n
        m = np.column_stack([np.ones(n + 1), arr, arr**2, arr**3]).T

        points = np.empty((n + 1, n + 1, dim))
        for i in range(dim):
            points[:, :, i] = m.T @ b.T @ g[:, :, i] @ b @ m
            
        return points
    
    def lines(self):
        n = self.step
        p = self.point_mat()
        
        v_i = np.tile(np.arange(n), (n, 1))
        u_i = v_i.T
        u_i = u_i.flatten()
        v_i = v_i.flatten()
        
        # 1 - 3
        # |   |
        # 2 - 4
        p1 = p[u_i + 0, v_i + 0]
        p2 = p[u_i + 1, v_i + 0]
        p3 = p[u_i + 0, v_i + 1]
        p4 = p[u_i + 1, v_i + 1]
        lines = np.stack((p1,p2,p2,p4,p4,p3,p3,p1), axis=1).flatten().tolist()
        return lines

    def geo(self):
        n = self.step
        p = self.point_mat()

        v_i = np.tile(np.arange(n), (n, 1))
        u_i = v_i.T
        u_i = u_i.flatten()
        v_i = v_i.flatten()

        # 1 - 3
        # | / |
        # 2 - 4
        p1 = p[u_i + 0, v_i + 0]
        p2 = p[u_i + 1, v_i + 0]
        p3 = p[u_i + 0, v_i + 1]
        p4 = p[u_i + 1, v_i + 1]

        u_t = np.stack((p1, p2, p3), axis=1)
        l_t = np.stack((p2, p4, p3), axis=1)
        t = np.vstack((u_t, l_t))

        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 1])
        n = n / np.linalg.norm(n, axis=1)[:, np.newaxis]
        n = np.repeat(n[:, np.newaxis, :], 3, axis=1)

        geo = Geometry()
        geo.vertices = t.flatten().tolist()
        geo.normals = n.flatten().tolist()
        return geo

    def vflist(self):
        n = self.step
        p = self.point_mat()
        vlist = np.reshape(p, (-1, 3)).tolist()
        
        i, j = np.indices((n, n))
        p = j + i * (n + 1)
        # 1 < 4
        # |   |
        # 2 > 3
        p1 = p.reshape(-1, 1)
        p2 = (p+(n+1)).reshape(-1, 1)
        p3 = (p+(n+2)).reshape(-1, 1)
        p4 = (p+1).reshape(-1, 1)
        flist = np.hstack((p1,p2,p3,p4)).tolist()
    
        return vlist, flist
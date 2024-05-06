from pyglet.math import Vec3

import copy
import numpy as np
from geometry import *

class HalfEdgeStructure:
    def __init__(self):
        self.step = 0
        
        self.h: int = 0
        self.v: int = 0
        self.f: int = 0
        self.e: int = 0
        self.twin: list[int] = []
        self.next: list[int] = []
        self.prev: list[int] = []
        self.vert: list[int] = []
        self.edge: list[int] = []
        self.face: list[int] = []
        self.point: list[Vec3] = []
        
        self.init_h: int = 0
        self.init_v: int = 0
        self.init_f: int = 0
        self.init_e: int = 0
        self.init_twin: list[int] = []
        self.init_next: list[int] = []
        self.init_prev: list[int] = []
        self.init_vert: list[int] = []
        self.init_edge: list[int] = []
        self.init_face: list[int] = []
        self.init_point: list[Vec3] = []
        
    def parse_vf(self, vertices: list, faces: list):
        self.__init__()
        
        for f in faces:
            self.h += len(f)
        self.v = len(vertices)
        self.f = len(faces)
        
        self.twin = [-1] * self.h
        self.next = [-1] * self.h
        self.prev = [-1] * self.h
        self.vert = [-1] * self.h
        self.edge = [-1] * self.h
        self.face = [-1] * self.h
        
        edge_map = {}
        index = 0
        
        for p in vertices:
            self.point.append(Vec3(*p))
            
        for f_i, f in enumerate(faces):
            n = len(f)
            for i in range(n):
                v_i = f[i]
                v_j = f[(i+1)%n]
                
                e = tuple(sorted((v_i, v_j)))
                e_i = len(edge_map)
                if e in edge_map:
                    twin = edge_map[e]
                    e_i = self.edge[twin]
                    self.twin[index] = twin
                    self.twin[twin] = index
                else:
                    edge_map[e] = index
                
                self.next[index] = index + 1 - (n if i == n-1 else 0)
                self.prev[index] = index - 1 + (n if i == 0 else 0)
                    
                self.vert[index] = v_i
                self.edge[index] = e_i
                self.face[index] = f_i
                
                index += 1
        self.e = len(edge_map)
        
        self.init_h = self.h
        self.init_v = self.v
        self.init_f = self.f
        self.init_e = self.e
        self.init_twin = self.twin
        self.init_next = self.next
        self.init_prev = self.prev
        self.init_vert = self.vert
        self.init_edge = self.edge
        self.init_face = self.face
        self.init_point = self.point
                
    def reset(self):
        self.step = 0
        
        self.h = self.init_h
        self.v = self.init_v
        self.f = self.init_f
        self.e = self.init_e
        self.twin = self.init_twin
        self.next = self.init_next
        self.prev = self.init_prev
        self.vert = self.init_vert
        self.edge = self.init_edge
        self.face = self.init_face
        self.point = self.init_point
                
    def subdiv(self):
        if -1 in self.twin:
            raise Exception("Given structure is not manifold")
        
        self.step += 1
        
        h = self.h
        v = self.v
        f = self.f
        e = self.e
        twin = np.array(self.twin)
        next = np.array(self.next)
        prev = np.array(self.prev)
        vert = np.array(self.vert)
        edge = np.array(self.edge)
        face = np.array(self.face)
        point = np.array(self.point)
        
        new_h = 4 * h
        new_v = v + f + e
        new_f = h
        new_e = 2 * e + h
        new_twin = np.full(new_h, -1)
        new_next = np.full(new_h, -1)
        new_prev = np.full(new_h, -1)
        new_vert = np.full(new_h, -1)
        new_edge = np.full(new_h, -1)
        new_face = np.full(new_h, -1)
        new_point = np.zeros((new_v, 3))
        
        num_vert = np.full(v, -1)
        num_face = np.full(f, -1)
        
        for i in range(h): # cyclelength
            if self.step > 0:
                num_face = np.full(f, 4)
                break
            fi = face[i]
            if num_face[fi] == -1:
                n = 1
                i_ = next[i]
                while i_ != i:
                    n += 1
                    i_ = next[i_]
                num_face[fi] = n
                
        for i in range(h): # valence
            vi = vert[i]
            if num_vert[vi] == -1:
                n = 1
                i_ = next[twin[i]]
                while i_ != i:
                    n += 1
                    i_ = next[twin[i_]]
                num_vert[vi] = n
                
        curr = np.arange(h)
                
        new_twin[0::4] = 4*next[twin] + 3
        new_twin[1::4] = 4*next + 2
        new_twin[2::4] = 4*prev + 1
        new_twin[3::4] = 4*twin[prev] + 0
        
        new_next[0::4] = 4*curr + 1
        new_next[1::4] = 4*curr + 2
        new_next[2::4] = 4*curr + 3
        new_next[3::4] = 4*curr + 0
        
        new_prev[0::4] = 4*curr + 3
        new_prev[1::4] = 4*curr + 0
        new_prev[2::4] = 4*curr + 1
        new_prev[3::4] = 4*curr + 2
        
        new_vert[0::4] = vert
        new_vert[1::4] = edge + v + f
        new_vert[2::4] = face + v
        new_vert[3::4] = edge[prev] + v + f
        
        new_edge[0::4] = np.where(curr > twin, 2*edge, 2*edge+1)
        new_edge[1::4] = curr + 2*e
        new_edge[2::4] = prev + 2*e
        new_edge[3::4] = np.where(prev > twin[prev], 2*edge[prev]+1, 2*edge[prev])
        
        new_face[0::4] = curr
        new_face[1::4] = curr
        new_face[2::4] = curr
        new_face[3::4] = curr
        
        self.h = new_h
        self.v = new_v
        self.f = new_f
        self.e = new_e
        self.twin = new_twin.tolist()
        self.next = new_next.tolist()
        self.prev = new_prev.tolist()
        self.vert = new_vert.tolist()
        self.edge = new_edge.tolist()
        self.face = new_face.tolist()
                
        # face point
        n = num_face[face] # face's num of sides
        n = n[:,np.newaxis]
        vi = vert # halfedge vertex ID
        fi = face + v # new face point fertex ID
        np.add.at(new_point, fi, point[vi] / n)
        
        # smooth edge point
        vi = vert # halfedge vertex ID
        fi = face + v # new face point vertex ID
        ei = edge + v + f  # new edge point vertex ID
        np.add.at(new_point, ei, (new_point[fi] + point[vi]) / 4)
            
        # smooth vert point
        n = num_vert[vert] # vert's num of adj edges
        n = n[:,np.newaxis]
        vi = vert # halfedge vertex ID
        fi = face + v  # new face point vertex ID
        ei = edge + v + f  # new edge point vertex ID
        np.add.at(new_point, vi, (new_point[ei] * 4 - new_point[fi] + (point[vi]) * (n-3)) / (n*n))
            
        self.point = [Vec3(*p) for p in new_point]
        
    def guide_lines(self):
        lines = []
        for i in range(self.init_h):
            v1 = self.init_vert[i]
            v2 = self.init_vert[self.init_next[i]]
            lines.extend(self.init_point[v1].xyz)
            lines.extend(self.init_point[v2].xyz)
        return lines
        
    def lines(self):
        next = np.array(self.next)
        vert = np.array(self.vert)
        point = np.array(self.point)
        
        p1 = point[vert]
        p2 = point[vert[next]]
        
        e = np.stack((p1, p2), axis=1)
        lines = e.flatten().tolist()
        return lines
    
    def geo(self):
        if self.step > 0:
            return self.fast_geo()
        
        geo = Geometry()
        
        visit = [False]* self.f
        vertices = []
        normals = []
        for i in range(self.h):
            fi = self.face[i]
            if visit[fi]: continue
            visit[fi] = True
            
            v0 = self.vert[i]
            cnt = 1
            i_ = self.next[i]
            while i_ != i:
                vi = self.vert[i_]
                cnt += 1
                if cnt >= 3:
                    p0 = self.point[v0]
                    p1 = self.point[vlast]
                    p2 = self.point[vi]
                    p01 = p1 - p0
                    p12 = p2 - p1
                    n = p01.cross(p12).normalize()
                    vertices += [*p0.xyz, *p1.xyz, *p2.xyz]
                    normals += [*n.xyz] * 3
                i_ = self.next[i_]
                vlast = vi
                    
        geo.vertices = vertices
        geo.normals = normals
        return geo
    
    def fast_geo(self):
        h = self.h
        f = self.f
        next = np.array(self.next)
        vert = np.array(self.vert)
        face = np.array(self.face)
        point = np.array(self.point)
        
        curr = np.arange(h)
        f_he = np.zeros(f, dtype=int)
        f_he[face] = curr
        
        # 1 - 4
        # | \ |
        # 2 - 3
        v1 = vert[f_he]; f_he=next[f_he]
        v2 = vert[f_he]; f_he=next[f_he]
        v3 = vert[f_he]; f_he=next[f_he]
        v4 = vert[f_he]
        
        p1 = point[v1]
        p2 = point[v2]
        p3 = point[v3]
        p4 = point[v4]
        
        u_t = np.stack((p1, p2, p3), axis=1)
        l_t = np.stack((p3, p4, p1), axis=1)
        t = np.vstack((u_t, l_t))

        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 1])
        n = n / np.linalg.norm(n, axis=1)[:, np.newaxis]
        n = np.repeat(n[:, np.newaxis, :], 3, axis=1)
        
        geo = Geometry()
        geo.vertices = t.flatten().tolist()
        geo.normals = n.flatten().tolist()
        return geo
    
    def vflist(self):
        vlist = []
        for p in self.point:
            vlist.append([*p.xyz])
            
        visit = [False]* self.f
        flist = []
        for i in range(self.h):
            fi = self.face[i]
            if visit[fi]: continue
            visit[fi] = True
            
            face = [self.vert[i]]
            i_ = self.next[i]
            while i_ != i:
                face.append(self.vert[i_])
                i_ = self.next[i_]
            flist.append(face)
                    
        return vlist, flist
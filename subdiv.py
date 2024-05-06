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
        twin = self.twin
        next = self.next
        prev = self.prev
        vert = self.vert
        edge = self.edge
        face = self.face
        point = self.point
        
        new_h = 4 * h
        new_v = v + f + e
        new_f = h
        new_e = 2 * e + h
        new_twin = [-1] * new_h
        new_next = [-1] * new_h
        new_prev = [-1] * new_h
        new_vert = [-1] * new_h
        new_edge = [-1] * new_h
        new_face = [-1] * new_h
        new_point = []
        
        for i in range(new_v):
            new_point.append(Vec3())
        
        num_vert = [-1] * v
        num_face = [-1] * f
        
        for i in range(h): # cyclelength, valence
            fi = face[i]
            vi = vert[i]
            
            if num_face[fi] == -1:
                n = 1
                i_ = next[i]
                while i_ != i:
                    n += 1
                    i_ = next[i_]
                num_face[fi] = n
                
            if num_vert[vi] == -1:
                n = 1
                # print(vert[i])
                i_ = next[twin[i]]
                # print(vert[i_])
                # cnt =0
                while i_ != i:
                    # cnt += 1
                    n += 1
                    # if(cnt < 30):
                        # print(vert[i_])
                    i_ = next[twin[i_]]
                num_vert[vi] = n
                
        for i in range(h): # halfedge refinement
            i_ = prev[i]
            
            new_twin[4*i + 0] = 4*next[twin[i]] + 3
            new_twin[4*i + 1] = 4*next[i] + 2
            new_twin[4*i + 2] = 4*prev[i] + 1
            new_twin[4*i + 3] = 4*twin[prev[i]] + 0
            
            new_next[4*i + 0] = 4*i + 1
            new_next[4*i + 1] = 4*i + 2
            new_next[4*i + 2] = 4*i + 3
            new_next[4*i + 3] = 4*i + 0
            
            new_prev[4*i + 0] = 4*i + 3
            new_prev[4*i + 1] = 4*i + 0
            new_prev[4*i + 2] = 4*i + 1
            new_prev[4*i + 3] = 4*i + 2
            
            new_vert[4*i + 0] = vert[i]
            new_vert[4*i + 1] = v + f + edge[i]
            new_vert[4*i + 2] = v + face[i]
            new_vert[4*i + 3] = v + f + edge[i_]
            
            new_edge[4*i + 0] = 2*edge[i] if i > twin[i] else 2*edge[i]+1
            new_edge[4*i + 1] = 2*e + i
            new_edge[4*i + 2] = 2*e + i_
            new_edge[4*i + 3] = 2*edge[i_]+1 if i_ > twin[i_] else 2*edge[i_]
            
            new_face[4*i + 0] = i
            new_face[4*i + 1] = i
            new_face[4*i + 2] = i
            new_face[4*i + 3] = i
            
            self.h = new_h
            self.v = new_v
            self.f = new_f
            self.e = new_e
            self.twin = new_twin
            self.next = new_next
            self.prev = new_prev
            self.vert = new_vert
            self.edge = new_edge
            self.face = new_face
                
        for i in range(h): # face point
            n = num_face[face[i]] # face's num of sides
            vi = vert[i] # halfedge vertex ID
            fi = v + face[i] # new face point fertex ID
            new_point[fi] += point[vi] / n
            
        for i in range(h): # smooth edge point
            vi = vert[i] # halfedge vertex ID
            fi = v + face[i] # new face point vertex ID
            ei = v + f + edge[i] # new edge point vertex ID
            new_point[ei] += (new_point[fi] + point[vi]) / 4
            
        for i in range(h): # smooth vert point
            n = num_vert[vert[i]] # vert's num of adj edges
            vi = vert[i] # halfedge vertex ID
            fi = v + face[i] # new face point vertex ID
            ei = v + f + edge[i] # new edge point vertex ID
            new_point[vi] += (new_point[ei] * 4 - new_point[fi] + (point[vi]) * (n-3)) / (n*n)
            
        self.point = new_point
        
    def guide_lines(self):
        lines = []
        for i in range(self.init_h):
            v1 = self.init_vert[i]
            v2 = self.init_vert[self.init_next[i]]
            lines.extend(self.init_point[v1].xyz)
            lines.extend(self.init_point[v2].xyz)
        return lines
        
    def lines(self):
        lines = []
        for i in range(self.h):
            v1 = self.vert[i]
            v2 = self.vert[self.next[i]]
            lines.extend(self.point[v1].xyz)
            lines.extend(self.point[v2].xyz)
        return lines
    
    def geo(self):
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
import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

from typing import List

import shader.shader as shader
from object_3d import Object3D

class CustomLineGroup(pyglet.graphics.Group):
    __totGroup__ = 0
    '''
    To draw multiple 3D shapes in Pyglet, you should make a group for an object.
    '''

    def __init__(self):
        super().__init__(CustomLineGroup.__totGroup__)
        CustomLineGroup.__totGroup__ += 1
        self.shader_program = shader.create_program(
            shader.vertex_source_simple,
            shader.fragment_source_simple
        )
        self.transform_mat = Mat4()
        self.vlist = None
        self.width = 1
        self.shader_program.use()

    def set_state(self):
        self.shader_program.use()
        model = self.transform_mat
        self.shader_program['model'] = model
        glLineWidth(self.width)
        glDepthFunc(GL_LEQUAL)

    def unset_state(self):
        self.shader_program.stop()

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.order == other.order and
                self.parent == other.parent)

    def __hash__(self):
        return hash((self.order))


class ObjectLine:
    def __init__(self, lines, color: Vec4 = Vec4(1,1,1,1), width = 1):
        self.group = CustomLineGroup()
        self.group.width = width
        self.color = color
        self.vertices = lines
        self.parent: Object3D = None
        self.translate_mat: Mat4 = Mat4()
        self.rotation_mat: Mat4 = Mat4()

    def set_batch(self, batch: pyglet.graphics.Batch):
        self.batch = batch
        
        count = len(self.vertices)//3
        args = {
            'count':count,
            'mode':GL_LINES,
            'batch':batch,
            'group':self.group,
            'vertices':('f', self.vertices),
        }
        self.group.vlist = self.group.shader_program.vertex_list(**args)
        self.group.shader_program['color'] = self.color
        
    def update(self, lines: List[Vec3] = None, color: Vec4 = None):
        if lines:
            self.vertices = lines
            count = len(self.vertices)//3
            self.group.vlist.resize(count)
            self.group.vlist.set_attribute_data('vertices', self.vertices)
        if color:
            self.color = color
            self.group.shader_program['color'] = color
    
    def delete(self):
        self.group.shader_program.delete()
        self.group.shader_program = None
        self.group.visible = False
        self.group = None
        
    def calc_transform_mat(self):
        parent_transform_mat = Mat4()
        if self.parent is not None:
            parent_transform_mat = self.parent.group.transform_mat
        self.group.transform_mat = parent_transform_mat @ self.translate_mat @ self.rotation_mat

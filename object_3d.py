import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

import shader.shader as shader
from geometry import *


class CustomGroup(pyglet.graphics.Group):
    __totGroup__ = 0
    """
    To draw multiple 3D shapes in Pyglet, you should make a group for an object.
    """

    def __init__(self, texture: pyglet.image.Texture = None):
        super().__init__(CustomGroup.__totGroup__)
        CustomGroup.__totGroup__ += 1
        self.texture = texture
        """
        Create shader program for each shape
        """
        self.shader_program = shader.create_program(
            shader.vertex_source_phong, shader.fragment_source_phong
        )
        self.transform_mat = Mat4()
        self.vlist = None
        self.shader_program.use()

    def set_state(self):
        self.shader_program.use()
        model = self.transform_mat
        self.shader_program["model"] = model
        self.shader_program["textured"] = self.texture is not None
        glDepthFunc(GL_LESS)

        if self.texture is not None:
            glActiveTexture(GL_TEXTURE0)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glBindTexture(self.texture.target, self.texture.id)

    def unset_state(self):
        self.shader_program.stop()

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.order == other.order
            and self.parent == other.parent
        )

    def __hash__(self):
        return hash((self.order))


class Object3D:
    def __init__(
        self,
        geometry: Geometry,
        texture: pyglet.image.Texture = None,
        color: Vec4 = Vec4(1, 0, 0, 1),
    ):
        self.group = CustomGroup(texture=texture)
        self.color = color
        self.geometry = geometry
        self.parent: Object3D = None
        self.children: list[Object3D] = []
        self.translate_mat: Mat4 = Mat4()
        self.rotation_mat: Mat4 = Mat4()

    def set_batch(self, batch: pyglet.graphics.Batch):
        glLineWidth(10)
        count = len(self.geometry.vertices) // 3
        args = {
            "count": count,
            "mode": GL_TRIANGLES,
            "batch": batch,
            "group": self.group,
            "vertices": ("f", self.geometry.vertices),
        }
        if self.geometry.normals:
            args["normals"] = ("f", self.geometry.normals)
        if self.geometry.uvs:
            args["uvs"] = ("f", self.geometry.uvs)

        if self.geometry.indices:
            args["indices"] = self.geometry.indices
            self.group.vlist = self.group.shader_program.vertex_list_indexed(**args)
        else:
            self.group.vlist = self.group.shader_program.vertex_list(**args)
        self.group.shader_program["color"] = self.color

    def update(self, geometry:Geometry = None, color:Vec4 = None):
        if geometry:
            self.geometry = geometry
            count = len(self.geometry.vertices) // 3
            self.group.vlist.resize(count)
            self.group.vlist.set_attribute_data("vertices", geometry.vertices)
            self.group.vlist.set_attribute_data("normals", geometry.normals)
        if color:
            self.color = color
            self.group.shader_program["color"] = self.color

    def delete(self):
        self.group.shader_program.delete()
        self.group.shader_program = None
        self.group.visible = False
        self.group = None

    def calc_transform_mat(self):
        parent_transform_mat = Mat4()
        if self.parent is not None:
            parent_transform_mat = self.parent.group.transform_mat

        self.group.transform_mat = (
            parent_transform_mat @ self.translate_mat @ self.rotation_mat
        )
        for child in self.children:
            child.calc_transform_mat()

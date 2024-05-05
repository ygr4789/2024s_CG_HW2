import pyglet
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Mat4, Vec3, Vec4
from pyglet.gl import *

from object_3d import Object3D
from ui import UI

class RenderWindow(pyglet.window.Window):
    '''
    inherits pyglet.window.Window which is the default render window of Pyglet
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()
        '''
        View (camera) parameters
        '''
        self.cam_eye = Vec3(6,3,4)
        self.cam_target = Vec3(0,0,0)
        self.cam_vup = Vec3(0,1,0)
        self.view_mat = None
        '''
        Projection parameters
        '''
        self.z_near = 0.01
        self.z_far = 100
        self.fov = 60
        self.proj_mat = None
        '''
        Uniforms (Lighting)
        '''
        self.view_proj = None
        self.dir_light = Vec3(4, 3, -6).normalize()
        
        self.objects: list[Object3D] = []
        self.ui = UI(self)
        self.setup()


    def setup(self) -> None:
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.1, 0.1, 0.1, 1)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        self.calc_matrices()
        
    def calc_matrices(self) -> None:
        # 1. Create a view matrix
        self.view_mat = Mat4.look_at(
            self.cam_eye, target=self.cam_target, up=self.cam_vup)
        
        # 2. Create a projection matrix
        self.proj_mat = Mat4.perspective_projection(
            aspect = self.width/self.height, 
            z_near=self.z_near, 
            z_far=self.z_far, 
            fov = self.fov)
        
        # 3. Calc a view_proj matrix
        self.view_proj = self.proj_mat @ self.view_mat

    def on_draw(self) -> None:
        self.clear()
        self.batch.draw()
        self.ui.render()
        
    def on_resize(self, width, height):
        glViewport(0, 0, *self.get_framebuffer_size())
        self.calc_matrices()
        return pyglet.event.EVENT_HANDLED
        
    def add_object(self, object):
        '''
        Assign a group for each object
        '''
        object.set_batch(self.batch)
        self.objects.append(object)

    def update(self,dt) -> None:
        for object in self.objects:
            '''
            Update position/orientation in the scene. In the current setting, 
            objects created later rotate faster while positions are not changed.
            '''
            self.calc_matrices()
            
            if(object.group is None):
                self.objects.remove(object)
                continue
            if(object.parent is None):
                object.calc_transform_mat()
                
            object.group.shader_program['view_proj'] = self.view_proj
            if isinstance(object, Object3D):
                object.group.shader_program['dir_light'] = self.dir_light
                object.group.shader_program['cam_eye'] = self.cam_eye
        
    def fixed_update(self,dt) -> None:
        pass
        
    def run(self):
        pyglet.clock.schedule_interval(self.fixed_update, 1/60)
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()
        
        


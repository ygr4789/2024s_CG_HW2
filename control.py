import pyglet, math
from pyglet import window, app, shapes
from pyglet.window import mouse,key
from pyglet.math import Mat4, Vec4, Vec3, Vec2

from typing import List

from render import RenderWindow

class Control:
    """
    Control class controls keyboard & mouse inputs.
    """
    def __init__(self, window: RenderWindow):
        window.on_key_press = self.on_key_press
        window.on_key_release = self.on_key_release
        window.on_mouse_motion = self.on_mouse_motion
        window.on_mouse_drag = self.on_mouse_drag
        window.on_mouse_press = self.on_mouse_press
        window.on_mouse_release = self.on_mouse_release
        window.on_mouse_scroll = self.on_mouse_scroll
        self.window = window
        self.setup()
        
    def __getitem__(self, key):
        return self.data.get(key, False)
    
    def __getattr__(self, name):
        return self.data.get(name, False)
    
    def check_disabled(func):
        def wrapper(self, *args, **kwargs):
            if not self.disabled:
                return func(self, *args, **kwargs)
        return wrapper

    def setup(self):
        self.data = {
            "grabbed": -1,
            "diabled": False
        }
        self.points: list[Vec3] = []
        
    def bind_points(self, points: List[Vec3] = []):
        self.points = points

    def update(self, vector):
        pass

    @check_disabled
    def on_key_press(self, symbol, modifier):
        pass
    
    @check_disabled
    def on_key_release(self, symbol, modifier):
        if symbol == key.ESCAPE:
            pyglet.app.exit()

    @check_disabled
    def on_mouse_motion(self, x, y, dx, dy):
        if (i := self.grabbed) != -1:
            nx = (x / self.window.width) * 2 - 1
            ny = (y / self.window.height) * 2 - 1
            cursor_norm_coord = Vec4(nx, ny, 0, 1)
            cursor_world_coord = ~(self.window.view_proj) @ cursor_norm_coord
            
            cam_target = self.window.cam_target
            cam_eye = self.window.cam_eye
            
            ray_target = cursor_world_coord.xyz / cursor_world_coord.w
            ray_origin = cam_eye
            ray_dir = ray_target - ray_origin
            
            plane_normal = (cam_eye - cam_target).normalize()
            plane_origin = self.points[i]
            
            t = (plane_origin-ray_origin).dot(plane_normal)/ray_dir.dot(plane_normal)
            target = ray_origin + ray_dir * t
            self.points[i] = target
        
        elif self[mouse.LEFT]:
            cam_eye = self.window.cam_eye
            cam_target = self.window.cam_target
            cam_vup = self.window.cam_vup
            cam_t_to_e = cam_eye - cam_target
            cam_z = (cam_target - cam_eye).normalize()
            cam_x = cam_vup.cross(cam_z)
            cam_y = cam_z.cross(cam_x)
            
            sth = cam_vup.cross(cam_z).dot(cam_x)
            up = cam_vup.dot(cam_z) > 0
            d_pi = -dx * 0.01
            d_th = -dy * 0.01
            if up and sth + d_th < 0 : d_th = 0
            if not up and sth - d_th < 0 : d_th = 0
            R1 = Mat4.from_rotation(d_pi, cam_vup)
            R2 = Mat4.from_rotation(d_th, cam_x)
            
            R = R1 @ R2 
            new_t_to_e = Vec4(*cam_t_to_e.xyz, 0)
            new_t_to_e = (R @ new_t_to_e).xyz
            self.window.cam_eye = cam_target + new_t_to_e
            
        elif self[mouse.RIGHT]:
            cam_eye = self.window.cam_eye
            cam_target = self.window.cam_target
            cam_vup = self.window.cam_vup
            cam_dist = cam_target.distance(cam_eye)
            cam_z = (cam_target - cam_eye).normalize()
            cam_x = cam_vup.cross(cam_z)
            cam_y = cam_z.cross(cam_x)
            
            fov = self.window.fov
            w_width = 2 * cam_dist * math.tan(fov * math.pi / 360)
            s_width = self.window.width
            
            cam_update = (cam_x * dx - cam_y * dy) * (w_width / s_width)
            self.window.cam_target += cam_update
            self.window.cam_eye += cam_update

    @check_disabled
    def on_mouse_drag(self, x, y, dx, dy, button, modifier):
        self.on_mouse_motion(x, y, dx, dy)
        
    @check_disabled
    def on_mouse_press(self, x, y, button, modifier):
        self.data[button] = True
        
        if self[mouse.LEFT]:
            click_bound = 10 # max distance that a target is recognized as clicked (pixel)
            min_dist = click_bound
            for i, p in enumerate(self.points):
                p_coord = Vec4(*p.xyz, 1)
                n_coord = self.window.view_proj @ p_coord
                px = n_coord.x / n_coord.w
                py = n_coord.y / n_coord.w
                px = self.window.width * (px + 1) / 2
                py = self.window.height * (py + 1) / 2
                pixel_dist = Vec2(px - x, py - y).mag
                if pixel_dist < min_dist:
                    min_dist = pixel_dist
                    self.data["grabbed"] = i

    @check_disabled
    def on_mouse_release(self, x, y, button, modifier):
        self.data[button] = False
        self.data["grabbed"] = -1

    @check_disabled
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        cam_eye = self.window.cam_eye
        cam_target = self.window.cam_target
        cam_dir = cam_target - cam_eye
        cam_update = cam_dir * scroll_y * 0.1
        self.window.cam_eye += cam_update
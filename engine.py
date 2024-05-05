from pyglet.gui import WidgetBase
import numpy as np

from render import RenderWindow
from geometry import *

from pyglet.math import Vec4

from object_3d import Object3D
from object_line import ObjectLine
from object_point import ObjectPoint
from control import Control

from subdiv import HalfEdgeStructure
from curve import ControlSurface
from obj_parser import *
from const import *

class Engine:
    def __init__(self, renderer: RenderWindow, controller: Control):
        self.renderer = renderer
        self.controller = controller
        renderer.fixed_update = self.fixed_update
        self.setup()
        
    def setup(self):
        self.control_points = ObjectPoint([0,0,0])
        self.renderer.add_object(self.control_points)
        self.set_curve()
        self.set_subdiv()
        self.change_mode()
        self.update_color()
        self.update_visibility()
        
    def change_mode(self):
        ui = self.renderer.ui
        mode = ui.mode_selected
        if mode == MODE_CURVE:
            self.controller.bind_points(self.control_surface.points)
        elif mode == MODE_SUBDIV:
            self.controller.bind_points(self.halgedge_structure.init_point)
        self.update_visibility()
        
    def update_visibility(self):
        ui = self.renderer.ui
        mode = ui.mode_selected
        grid = ui.grid_active
        wireframe = ui.wireframe_active
        control = ui.control_active
        
        self.curve_obj.group.visible = mode == MODE_CURVE
        self.curve_wireframe.group.visible = mode == MODE_CURVE and wireframe
        self.curve_guide.group.visible = mode == MODE_CURVE and control
        
        self.subidv_obj.group.visible = mode == MODE_SUBDIV
        self.subdiv_wireframe.group.visible = mode == MODE_SUBDIV and wireframe
        self.subdiv_guide.group.visible = mode == MODE_SUBDIV and control
        
        self.control_points.group.visible = control

    def set_curve(self):
        self.control_surface = ControlSurface()
        
        self.curve_wireframe = ObjectLine(self.control_surface.lines(), width = 2)
        self.renderer.add_object(self.curve_wireframe)
        
        self.curve_guide = ObjectLine(self.control_surface.guide_lines(), width = 3)
        self.renderer.add_object(self.curve_guide)
        
        self.curve_obj = Object3D(self.control_surface.geo())
        self.renderer.add_object(self.curve_obj)
        
    def set_subdiv(self):
        self.halgedge_structure = HalfEdgeStructure()
        self.halgedge_structure.parse_vf(default_cube_v, default_cube_f)
        
        self.subdiv_guide = ObjectLine(self.halgedge_structure.guide_lines(), width = 3)
        self.renderer.add_object(self.subdiv_guide)
        
        self.subidv_obj = Object3D(self.halgedge_structure.geo())
        self.renderer.add_object(self.subidv_obj)
        
        self.subdiv_wireframe = ObjectLine(self.halgedge_structure.lines(), width = 2)
        self.renderer.add_object(self.subdiv_wireframe)
            
    def update_control_points(self):
        points = []
        for p in self.controller.points:
            points.extend([*p.xyz])
        self.control_points.update(points)
            
    def update_curve(self):
        ui = self.renderer.ui
        step = ui.curve_step
        type = ui.type_selected
        
        self.control_surface.step = step
        self.control_surface.use_bezier = type == TYPE_BEZIER
        
        self.curve_obj.update(self.control_surface.geo())
        self.curve_wireframe.update(self.control_surface.lines())
        self.curve_guide.update(self.control_surface.guide_lines())
        
    def update_subdiv(self, forced=False):
        ui = self.renderer.ui
        step = ui.subdiv_step
        
        curr_step = self.halgedge_structure.step
        remain_step = step - curr_step
        
        if remain_step < 0 or forced:
            self.halgedge_structure.reset()
            remain_step = step
        for i in range(remain_step):
            self.halgedge_structure.subdiv()
        
        self.subidv_obj.update(self.halgedge_structure.geo())
        self.subdiv_wireframe.update(self.halgedge_structure.lines())
        self.subdiv_guide.update(self.halgedge_structure.guide_lines())
        
    def update_color(self):
        ui = self.renderer.ui
        color = Vec4(*ui.color)
        self.curve_obj.update(color = color)
        self.subidv_obj.update(color = color)
        
    def import_obj(self):
        ui = self.renderer.ui
        filename = ui.filename
        vs, fs = load_obj_to_vflist(filename)
        self.halgedge_structure.parse_vf(vs, fs)
        self.controller.bind_points(self.halgedge_structure.init_point)
        self.update_subdiv()
        
    def export_obj(self):
        ui = self.renderer.ui
        filename = ui.filename
        mode = ui.mode_selected
        if mode == MODE_CURVE:
            vs, fs = self.control_surface.vflist()
        elif mode == MODE_SUBDIV:
            vs, fs = self.halgedge_structure.vflist()
        save_vflist_to_obj(filename, vs, fs)
        
    def fixed_update(self, dt):
        ui = self.renderer.ui
        self.controller.disabled = ui.focused
        
        queue = ui.command_queue
        while len(queue) > 0:
            cmd = queue.pop(0)
            try:
                if cmd == "change_mode":
                    self.change_mode()
                elif cmd == "import":
                    self.import_obj()
                    ui.log("Imported obj file")
                elif cmd == "export":
                    self.export_obj()
                    ui.log("Exported obj file")
                elif cmd == "reset_curve":
                    self.control_surface.reset()
                    self.update_curve()
                elif cmd == "update_curve":
                    self.update_curve()
                elif cmd == "update_subdiv":
                    self.update_subdiv()
                elif cmd == "update_color":
                    self.update_color()
                elif cmd == "update_visibility":
                    self.update_visibility()
            except Exception as e:
                ui.log(e)
        
        self.update_control_points()
        if self.controller.grabbed != -1 and ui.control_active:
            mode = ui.mode_selected
            if mode == MODE_CURVE:
                self.update_curve()
            elif mode == MODE_SUBDIV:
                self.update_subdiv(True)
        pass
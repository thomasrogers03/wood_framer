import os.path
import uuid

from direct.showbase.ShowBase import ShowBase
from panda3d import bullet, core

from . import frame, frame_modifier, highlighter


class App(ShowBase):
    _METRES_TO_INCHES = 2.54
    _INCHES_TO_FEET = 12
    _SIX_FEET = 6 * _INCHES_TO_FEET
    _EIGHT_FEET = 8 * _INCHES_TO_FEET
    _TEN_FEET = 10 * _INCHES_TO_FEET
    _TWELVE_FEET = 12 * _INCHES_TO_FEET
    _TICK_RATE = 1 / 35

    def __init__(self):
        super().__init__()

        self._global_clock: core.ClockObject = globalClock

        light_node_path = self.render.attach_new_node(core.DirectionalLight("light"))
        self.render.set_light(light_node_path)

        self._collision_world = bullet.BulletWorld()
        self._setup_bullet_debug()

        main_light = core.AmbientLight("light2")
        main_light.set_color(core.Vec4(0.5, 0.5, 0.5, 1))
        light_node_path = self.render.attach_new_node(main_light)
        self.render.set_light(light_node_path)

        self._scene: core.NodePath = self.render.attach_new_node("scene")
        self._scene.set_scale(self._METRES_TO_INCHES)

        frame_base: core.NodePath = self._scene.attach_new_node("frame_base")
        box: core.NodePath = self.loader.load_model("box")
        box.reparent_to(frame_base)
        box.set_pos(-0.5, -0.5, 0)

        if os.path.exists("wood.jpg"):
            wood_texture: core.Texture = self.loader.load_texture("wood.jpg")
            frame_base.set_texture(wood_texture, 1)
        else:
            frame_base.set_color(205 / 255, 133 / 255, 63 / 255)
            frame_base.set_texture_off(1)

        self._two_by_four: core.NodePath = self._scene.attach_new_node("two_by_four")
        frame_base.copy_to(self._two_by_four)
        self._two_by_four.set_scale(2, 4, 1)
        self._two_by_four.hide()

        self._two_by_six: core.NodePath = self._scene.attach_new_node("two_by_six")
        frame_base.copy_to(self._two_by_six)
        self._two_by_six.set_scale(2, 6, 1)
        self._two_by_six.hide()

        frame_base.remove_node()

        self._highlighter = highlighter.Highlighter(
            self.render,
            self.mouseWatcherNode,
            self.camLens,
            self.camera,
            self._collision_world,
        )
        self._frame_modifier = frame_modifier.FrameModifier(
            self._scene,
            self.camera,
            self._highlighter,
            self._re_enable_mouse,
            self.disable_mouse,
        )

        self.task_mgr.do_method_later(self._TICK_RATE, self._tick, "tick")

        self.accept("shift-a", self._add_frame)
        self.accept("shift-d", self._copy_frame)

    def _add_frame(self):
        self._build_wall_frame(32, self._EIGHT_FEET)

    def _copy_frame(self):
        if self._highlighter.selected_frame is None:
            return

        frame = self._highlighter.selected_frame
        new_frame = self._build_wall_frame(frame.length, frame.height)
        new_frame.set_position(frame.get_position())
        new_frame.set_rotation(frame.get_rotation())

    def _re_enable_mouse(self):
        camera: core.NodePath = self.camera
        inverse_camera_transform = core.Mat4(camera.get_mat())
        inverse_camera_transform.invertInPlace()

        mouse_interface: core.Trackball = self.mouseInterfaceNode
        mouse_interface.set_mat(inverse_camera_transform)
        self.enable_mouse()

    def _tick(self, task):
        self._collision_world.do_physics(self._global_clock.get_dt())
        self._highlighter.update()
        self._frame_modifier.update()
        return task.again

    def _setup_bullet_debug(self):
        debug_node = bullet.BulletDebugNode("debug")
        debug_node.show_wireframe(True)
        debug_node.show_constraints(True)
        debug_node.show_bounding_boxes(True)
        debug_node.show_normals(True)
        debug: core.NodePath = self.render.attach_new_node(debug_node)
        debug.show()

        self._collision_world.set_debug_node(debug_node)

    def _build_wall_frame(self, length: float, height: float):
        return frame.Frame(
            self._scene, self._collision_world, length, height, self._new_two_by_four
        )

    def _new_two_by_four(self, parent: core.NodePath, length: float):
        result = self._new_frame_piece(parent)
        self._copy(self._two_by_four, result)

        result.set_sz(length)
        return result

    def _new_two_by_six(self, parent: core.NodePath, length: float):
        result = self._new_frame_piece(parent)
        self._copy(self._two_by_six, result)

        result.set_sz(length)
        return result

    @staticmethod
    def _new_frame_piece(parent: core.NodePath) -> core.NodePath:
        piece_id = uuid.uuid4()
        return parent.attach_new_node(f"stud-{piece_id}")

    @staticmethod
    def _copy(source: core.NodePath, destination: core.NodePath):
        source.show()
        source.copy_to(destination)
        source.hide()

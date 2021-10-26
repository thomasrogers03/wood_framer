import json
import os.path
import typing
import uuid

from direct.gui import DirectGui
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
    _PROJECT_PATH = "project.json"

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

        self._frame_base: core.NodePath = self._scene.attach_new_node("frame_base")
        box: core.NodePath = self.loader.load_model("box")
        box.reparent_to(self._frame_base)
        box.set_pos(-0.5, -0.5, 0)

        if os.path.exists("wood.jpg"):
            wood_texture: core.Texture = self.loader.load_texture("wood.jpg")
            self._frame_base.set_texture(wood_texture, 1)
        else:
            self._frame_base.set_color(205 / 255, 133 / 255, 63 / 255)
            self._frame_base.set_texture_off(1)
        self._frame_base.hide()

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
        self.accept("shift-s", self._save_work)

        DirectGui.DirectButton(
            parent=self.a2dTopRight,
            text="New Frame",
            command=self._add_frame,
            scale=0.075,
            pos=core.Point3(-0.22, -0.075),
        )
        DirectGui.DirectButton(
            parent=self.a2dTopRight,
            text='Change to 2"x4"',
            command=self._change_to_two_by_four,
            scale=0.075,
            pos=core.Point3(-0.28, -0.17),
        )
        DirectGui.DirectButton(
            parent=self.a2dTopRight,
            text='Change to 2"x6"',
            command=self._change_to_two_by_six,
            scale=0.075,
            pos=core.Point3(-0.28, -0.278),
        )
        DirectGui.DirectButton(
            parent=self.a2dTopRight,
            text="Save Work",
            command=self._save_work,
            scale=0.075,
            pos=core.Point3(-0.205, -0.385),
        )

        self._load_work()

    def _change_to_two_by_four(self):
        if self._highlighter.selected_frame is None:
            return

        frame_to_change = self._highlighter.selected_frame
        frame_to_change.update(2, 4, frame_to_change.length, frame_to_change.height)

    def _change_to_two_by_six(self):
        if self._highlighter.selected_frame is None:
            return

        frame_to_change = self._highlighter.selected_frame
        frame_to_change.update(2, 6, frame_to_change.length, frame_to_change.height)

    def _load_work(self):
        if not os.path.isfile(self._PROJECT_PATH):
            return

        with open(self._PROJECT_PATH, "r") as file:
            result: typing.List[typing.Dict[str, float]] = json.load(file)

        for details in result:
            new_frame = self._build_wall_frame(
                details["stud_width"],
                details["stud_height"],
                details["length"],
                details["height"],
            )
            new_frame.set_position(details["x"], details["y"], details["z"])
            new_frame.set_rotation(details["h"], details["p"], details["r"])

    def _save_work(self):
        result: typing.List[typing.Dict[str, float]] = []
        for path in self._scene.find_all_matches("frame-*"):
            frame_to_save = frame.Frame.frame_from_node_path(path)
            position = frame_to_save.get_position()
            rotation = frame_to_save.get_rotation()
            details = {
                "stud_width": frame_to_save.stud_width,
                "stud_height": frame_to_save.stud_height,
                "length": frame_to_save.length,
                "height": frame_to_save.height,
                "x": position.x,
                "y": position.y,
                "z": position.z,
                "h": rotation.x,
                "p": rotation.y,
                "r": rotation.z,
            }
            result.append(details)

        with open(self._PROJECT_PATH, "w+") as file:
            json.dump(result, file)

    def _add_frame(self):
        self._build_wall_frame(2, 4, 32, self._EIGHT_FEET)

    def _copy_frame(self):
        if self._highlighter.selected_frame is None:
            return

        old_frame = self._highlighter.selected_frame
        new_frame = self._build_wall_frame(old_frame.length, old_frame.height)
        new_frame.set_position(old_frame.get_position())
        new_frame.set_rotation(old_frame.get_rotation())

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

    def _build_wall_frame(
        self, stud_width: float, stud_height: float, length: float, height: float
    ):
        return frame.Frame(
            self._scene,
            self._collision_world,
            stud_width,
            stud_height,
            length,
            height,
            self._new_stud,
        )

    def _new_stud(
        self, parent: core.NodePath, width: float, height: float, length: float
    ):
        result = self._new_frame_piece(parent)
        display: core.NodePath = result.attach_new_node("display")
        self._copy(self._frame_base, display)
        display.set_scale(width, height, 1)

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

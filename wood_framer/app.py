import os.path
import typing
import uuid

from direct.showbase.ShowBase import ShowBase
from panda3d import core


class App(ShowBase):
    _METRES_TO_INCHES = 2.54
    _INCHES_TO_FEET = 12
    _SIX_FEET = 6 * _INCHES_TO_FEET
    _EIGHT_FEET = 8 * _INCHES_TO_FEET
    _TEN_FEET = 10 * _INCHES_TO_FEET
    _TWELVE_FEET = 12 * _INCHES_TO_FEET
    _SPACE_BETWEEN_STUDS = 16

    def __init__(self):
        super().__init__()

        light_node_path = self.render.attach_new_node(core.DirectionalLight("light"))
        self.render.set_light(light_node_path)

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

        self._frame: typing.List[core.NodePath] = []

        frame_base.remove_node()

        self._build_wall_frame(self._TEN_FEET, self._EIGHT_FEET)

    def _build_wall_frame(self, length: float, height: float):
        frame_id = uuid.uuid4()
        parent: core.NodePath = self._scene.attach_new_node(f"frame-{frame_id}")

        bottom = self._new_two_by_four(parent, length)
        bottom.set_x(-1)
        bottom.set_r(90)
        bottom.set_z(1)

        top = self._new_two_by_four(parent, length)
        top.set_x(-1)
        top.set_r(90)
        top.set_z(height - 1)

        stud_count = int(length / self._SPACE_BETWEEN_STUDS)
        for stud_index in range(stud_count + 1):
            stud = self._new_two_by_four(parent, height - 4)
            stud.set_z(2)
            stud.set_x(stud_index * self._SPACE_BETWEEN_STUDS)

        if stud_count * self._SPACE_BETWEEN_STUDS < length:
            stud = self._new_two_by_four(parent, height - 4)
            stud.set_z(2)
            stud.set_x(length - 2)

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

import enum
import typing
import uuid

from panda3d import bullet, core


class FrameHighlight(enum.Enum):
    none = 0
    highlighted = 1
    selected = 2


class FrameDisplay:
    _SPACE_BETWEEN_STUDS = 16
    _INCHES_TO_FEET = 12

    def __init__(
        self,
        display_parent: core.NodePath,
        stud_width: float,
        stud_height: float,
        length: float,
        height: float,
        make_stud: typing.Callable[[core.NodePath, float, float, float], core.NodePath],
    ):
        self._display_parent = display_parent

        self._frame: core.NodePath = self._display_parent.attach_new_node("frame")
        self.destroy = self._frame.remove_node
        self.set_position = self._frame.set_pos
        self.set_rotation = self._frame.set_hpr

        self._stud_width = stud_width
        self._stud_height = stud_height

        half_stud_width = self._stud_width / 2

        bottom = make_stud(self._frame, self._stud_width, stud_height, length)
        bottom.set_r(90)
        bottom.set_z(half_stud_width)
        self._make_label(bottom, self._length_message(length))

        top = make_stud(self._frame, self._stud_width, stud_height, length)
        top.set_r(90)
        top.set_z(height - half_stud_width)
        self._make_label(top, self._length_message(length))

        wall_stud_length = height - 4
        half_stud_height = self._stud_height / 2

        stud_count = int(length / self._SPACE_BETWEEN_STUDS)
        for stud_index in range(stud_count):
            stud = make_stud(
                self._frame, self._stud_width, self._stud_height, wall_stud_length
            )
            stud.set_z(half_stud_height)
            stud.set_x(stud_index * self._SPACE_BETWEEN_STUDS + half_stud_width)
            self._make_label(stud, self._length_message(wall_stud_length))

        if stud_count * self._SPACE_BETWEEN_STUDS <= length:
            stud = make_stud(
                self._frame, self._stud_width, self._stud_height, wall_stud_length
            )
            stud.set_z(half_stud_height)
            stud.set_x(length - half_stud_width)
            self._make_label(stud, self._length_message(wall_stud_length))

    def _length_message(self, inches: float):
        feet = 0
        while inches >= FrameDisplay._INCHES_TO_FEET:
            feet += 1
            inches -= FrameDisplay._INCHES_TO_FEET
        message = f'{self._stud_width}"x{self._stud_height}"x'
        if feet > 0:
            message += f"{feet}'"
        if inches > 0:
            message += f'{inches}"'
        return message

    def _make_label(self, parent: core.NodePath, text: str):
        text_node = core.TextNode("label")
        text_node.set_text(text)
        text_node.set_text_color(1, 1, 1, 1)
        text_node.set_text_scale(3)
        text_node.set_shadow_color(0, 0, 0, 1)
        text_node.set_card_color(1, 1, 1, 1)

        result: core.NodePath = parent.attach_new_node(text_node)
        result.set_pos(2, -4, 0.5)
        result.set_hpr(0, 0, -90)
        result.set_scale(self._display_parent, core.Vec3(1, 1, 1))
        result.set_two_sided(True)
        result.set_light_off(1)

        return result


class Frame:
    def __init__(
        self,
        scene: core.NodePath,
        world: bullet.BulletWorld,
        stud_width: float,
        stud_height: float,
        length: float,
        height: float,
        make_stud: typing.Callable[[core.NodePath, float, float, float], core.NodePath],
    ):
        self._stud_width = stud_width
        self._stud_height = stud_height
        self._length = length
        self._height = height

        self._make_stud = make_stud
        self._highlight = FrameHighlight.none

        frame_id = uuid.uuid4()
        self._display_parent: core.NodePath = scene.attach_new_node(f"frame-{frame_id}")
        self._display_parent.set_python_tag("frame", self)

        self.get_position = self._display_parent.get_pos
        self.set_position = self._display_parent.set_pos
        self.get_rotation = self._display_parent.get_hpr
        self.set_rotation = self._display_parent.set_hpr

        frame_boundry_shape = bullet.BulletBoxShape(core.Vec3(0.5, 0.5, 0.5))
        frame_boundry_node = bullet.BulletRigidBodyNode(f"frame-{frame_id}")
        frame_boundry_node.add_shape(
            frame_boundry_shape,
            core.TransformState.make_pos(core.Vec3(0.5, 0, 0.5)),
        )
        frame_boundry_node.set_kinematic(True)
        frame_boundry_node.set_mass(0)
        frame_boundry_node.set_python_tag("frame", self)

        world.attach(frame_boundry_node)
        self._frame_boundry: core.NodePath = self._display_parent.attach_new_node(
            frame_boundry_node
        )

        self._frame_display: typing.Optional[FrameDisplay] = None
        self.update(self._length, self._height)

    @staticmethod
    def frame_from_node_path(path: core.NodePath):
        return typing.cast(Frame, path.get_python_tag("frame"))

    @staticmethod
    def frame_from_node(node: bullet.BulletBodyNode):
        return typing.cast(Frame, node.get_python_tag("frame"))

    @property
    def stud_width(self):
        return self._stud_width

    @property
    def stud_height(self):
        return self._stud_height

    @property
    def length(self):
        return self._length

    @property
    def height(self):
        return self._height

    @property
    def is_selected(self):
        return self._highlight == FrameHighlight.selected

    def set_highlight(self, highlight_type: FrameHighlight):
        self._highlight = highlight_type

        if self._highlight == FrameHighlight.highlighted:
            self._display_parent.set_color(0, 1, 0, 1)
        elif self._highlight == FrameHighlight.selected:
            self._display_parent.set_color(0, 0, 1, 1)
        else:
            self._display_parent.set_color(1, 1, 1, 1)

    def update(self, length: float, height: float):
        if self._frame_display is not None:
            self._frame_display.destroy()

        self._length = length
        self._height = height

        self._frame_boundry.set_scale(self._length, 4, self._height)
        self._frame_display = FrameDisplay(
            self._display_parent,
            self._stud_width,
            self._stud_height,
            self._length,
            self._height,
            self._make_stud,
        )

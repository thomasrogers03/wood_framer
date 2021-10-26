import enum
import typing
import uuid

from panda3d import bullet, core

from . import wall_frame


class FrameHighlight(enum.Enum):
    none = 0
    highlighted = 1
    selected = 2


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

        self._frame_display: typing.Optional[wall_frame.Display] = None
        self.update(self._stud_width, self._stud_height, self._length, self._height)

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

    def update(
        self, stud_width: float, stud_height: float, length: float, height: float
    ):
        if self._frame_display is not None:
            self._frame_display.destroy()

        self._stud_width = stud_width
        self._stud_height = stud_height
        self._length = length
        self._height = height

        self._frame_boundry.set_scale(self._length, self._stud_height, self._height)
        self._frame_display = wall_frame.Display(
            self._display_parent,
            self._stud_width,
            self._stud_height,
            self._length,
            self._height,
            self._make_stud,
        )

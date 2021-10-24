import math
import typing

from direct.showbase.DirectObject import DirectObject
from panda3d import bullet, core

from . import highlighter


class FrameModifier(DirectObject):
    _TRANSFORM_SCALE = 20

    def __init__(
        self,
        scene: core.NodePath,
        camera: core.NodePath,
        frame_highligher: highlighter.Highlighter,
        enable_mouse: typing.Callable[[], None],
        disable_mouse: typing.Callable[[], None],
    ):
        self._scene = scene
        self._camera = camera
        self._highligher = frame_highligher
        self._enable_mouse = enable_mouse
        self._disable_mouse = disable_mouse

        self._transforming = False
        self._start_position = core.Point3()
        self._last_mouse_position = core.Point2()

        self.accept("shift-mouse1", self._precheck_mouse)
        self.accept("mouse1-up", self._apply_transform)

        self.accept("-", self._decrease_length)
        self.accept("--repeat", self._decrease_length)
        self.accept("+", self._increase_length)
        self.accept("+-repeat", self._increase_length)

        self.accept("arrow_left", self._decrease_rotation)
        self.accept("arrow_left-repeat", self._decrease_rotation)
        self.accept("arrow_right", self._increase_rotation)
        self.accept("arrow_right-repeat", self._increase_rotation)

    def _decrease_rotation(self):
        self._change_rotation(-45)

    def _increase_rotation(self):
        self._change_rotation(45)

    def _change_rotation(self, amount: float):
        if self._highligher.selected_frame is None:
            return

        frame = self._highligher.selected_frame
        rotation = frame.get_rotation()
        frame.set_rotation(rotation + core.Vec3(amount, 0, 0))

    def _decrease_length(self):
        self._change_length(-1)

    def _increase_length(self):
        self._change_length(1)

    def _change_length(self, amount: float):
        if self._highligher.selected_frame is None:
            return

        frame = self._highligher.selected_frame
        frame.update(frame.length + amount, frame.height)

    def _precheck_mouse(self):
        if self._highligher.selected_frame is None:
            return

        self._last_mouse_position = core.Point2(self._highligher.get_mouse_position())
        self._start_position = self._highligher.selected_frame.get_position()
        self._transforming = True
        self._disable_mouse()

    def _apply_transform(self):
        if self._transforming:
            self._transforming = False
            self._enable_mouse()

    def update(self):
        if not self._transforming:
            return

        new_mouse_position = core.Point2(self._highligher.get_mouse_position())
        mouse_delta: core.Vec2 = new_mouse_position - self._last_mouse_position
        mouse_delta_3d = core.Vec3(mouse_delta.x, 0, mouse_delta.y)

        transform_vector: core.Vec3 = (
            self._scene.get_relative_vector(self._camera, mouse_delta_3d)
        ) * self._TRANSFORM_SCALE

        max_component = max(
            [transform_vector.x, transform_vector.y, transform_vector.z],
            key=lambda component: math.fabs(component),
        )
        snapped_max_component = round(max_component)

        if max_component == transform_vector.x:
            transform_direction = core.Vec3(snapped_max_component, 0, 0)
        elif max_component == transform_vector.y:
            transform_direction = core.Vec3(0, snapped_max_component, 0)
        else:
            transform_direction = core.Vec3(0, 0, snapped_max_component)

        self._highligher.selected_frame.set_position(
            self._start_position + transform_direction
        )

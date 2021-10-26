import math
import typing

from direct.showbase.DirectObject import DirectObject
from panda3d import core

from . import highlighter


class FrameModifier(DirectObject):
    _TRANSFORM_SCALE = 50

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

        self.accept("shift--", self._decrease_height)
        self.accept("shift---repeat", self._decrease_height)
        self.accept("shift-+", self._increase_height)
        self.accept("shift-+-repeat", self._increase_height)

        self.accept("arrow_left", self._decrease_heading)
        self.accept("arrow_left-repeat", self._decrease_heading)
        self.accept("arrow_right", self._increase_heading)
        self.accept("arrow_right-repeat", self._increase_heading)

        self.accept("arrow_down", self._decrease_pitch)
        self.accept("arrow_down-repeat", self._decrease_pitch)
        self.accept("arrow_up", self._increase_pitch)
        self.accept("arrow_up-repeat", self._increase_pitch)

    def _decrease_pitch(self):
        self._change_pitch(-15)

    def _increase_pitch(self):
        self._change_pitch(15)

    def _change_pitch(self, amount: float):
        if self._highligher.selected_frame is None:
            return

        frame = self._highligher.selected_frame
        rotation = frame.get_rotation()
        frame.set_rotation(rotation + core.Vec3(0, amount, 0))

    def _decrease_heading(self):
        self._change_heading(-45)

    def _increase_heading(self):
        self._change_heading(45)

    def _change_heading(self, amount: float):
        if self._highligher.selected_frame is None:
            return

        frame = self._highligher.selected_frame
        rotation = frame.get_rotation()
        frame.set_rotation(rotation + core.Vec3(amount, 0, 0))

    def _decrease_height(self):
        self._change_height(-1)

    def _increase_height(self):
        self._change_height(1)

    def _change_height(self, amount: float):
        if self._highligher.selected_frame is None:
            return

        frame = self._highligher.selected_frame
        frame.update(
            frame.stud_width,
            frame.stud_height,
            frame.length,
            frame.height + amount,
            frame.display_klass,
        )

    def _decrease_length(self):
        self._change_length(-1)

    def _increase_length(self):
        self._change_length(1)

    def _change_length(self, amount: float):
        if self._highligher.selected_frame is None:
            return

        frame = self._highligher.selected_frame
        frame.update(
            frame.stud_width,
            frame.stud_height,
            frame.length + amount,
            frame.height,
            frame.display_klass,
        )

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
        snapped_max_component = round(max_component * 2) / 2

        if max_component == transform_vector.x:
            transform_direction = core.Vec3(snapped_max_component, 0, 0)
        elif max_component == transform_vector.y:
            transform_direction = core.Vec3(0, snapped_max_component, 0)
        else:
            transform_direction = core.Vec3(0, 0, snapped_max_component)

        self._highligher.selected_frame.set_position(
            self._start_position + transform_direction
        )

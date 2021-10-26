import typing

from panda3d import core

from . import frame_display


class Display(frame_display.FrameDisplay):
    SERIALIZED_NAME = "door_frame"

    _SPACE_BETWEEN_STUDS = 16
    _INCHES_TO_FEET = 12
    _SEVEN_FEET = 7 * _INCHES_TO_FEET

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

        frame_stud_length = min(self._SEVEN_FEET, height - 2 * stud_width)

        left_stud = make_stud(
            self._frame, self._stud_width, self._stud_height, frame_stud_length
        )
        left_stud.set_z(self._stud_width)
        left_stud.set_x(half_stud_width)
        self._make_label(left_stud, self._length_message(frame_stud_length))

        right_stud = make_stud(
            self._frame, self._stud_width, self._stud_height, frame_stud_length
        )
        right_stud.set_z(self._stud_width)
        right_stud.set_x(length - half_stud_width)
        self._make_label(right_stud, self._length_message(frame_stud_length))

    @staticmethod
    def create(
        display_parent: core.NodePath,
        stud_width: float,
        stud_height: float,
        length: float,
        height: float,
        make_stud: typing.Callable[[core.NodePath, float, float, float], core.NodePath],
    ) -> frame_display.FrameDisplay:
        return Display(
            display_parent, stud_width, stud_height, length, height, make_stud
        )


frame_display.register(Display.SERIALIZED_NAME, Display)

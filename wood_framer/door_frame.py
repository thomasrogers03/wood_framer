import typing

from panda3d import core

from . import frame_display


class Display(frame_display.FrameDisplay):
    SERIALIZED_NAME = "door_frame"

    _SPACE_BETWEEN_STUDS = 16
    _INCHES_TO_FEET = 12
    _SIX_FEET = 6 * _INCHES_TO_FEET

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

        frame_stud_length = min(self._SIX_FEET, height - half_stud_width)

        support_top = make_stud(self._frame, self._stud_width, stud_height, length)
        support_top.set_r(90)
        support_top.set_z(frame_stud_length + half_stud_width)
        self._make_label(support_top, self._length_message(length))

        support_length = height - frame_stud_length - self._stud_width
        support_centre = make_stud(
            self._frame, self._stud_width, stud_height, support_length
        )
        support_centre.set_z(frame_stud_length + self._stud_width)
        support_centre.set_x(length / 2)
        self._make_label(support_centre, self._length_message(support_length))

        left_stud = make_stud(
            self._frame, self._stud_width, self._stud_height, frame_stud_length
        )
        left_stud.set_x(half_stud_width)
        self._make_label(left_stud, self._length_message(frame_stud_length))

        right_stud = make_stud(
            self._frame, self._stud_width, self._stud_height, frame_stud_length
        )
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

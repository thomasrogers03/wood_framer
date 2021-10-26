import typing

from panda3d import core

from . import frame_display


class Display(frame_display.FrameDisplay):
    SERIALIZED_NAME = "wall_frame"

    _SPACE_BETWEEN_STUDS = 16

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

        wall_stud_length = height - 2 * stud_width

        stud_count = int(length / self._SPACE_BETWEEN_STUDS)
        for stud_index in range(stud_count):
            stud = make_stud(
                self._frame, self._stud_width, self._stud_height, wall_stud_length
            )
            stud.set_z(self._stud_width)
            stud.set_x(stud_index * self._SPACE_BETWEEN_STUDS + half_stud_width)
            self._make_label(stud, self._length_message(wall_stud_length))

        if stud_count * self._SPACE_BETWEEN_STUDS <= length:
            stud = make_stud(
                self._frame, self._stud_width, self._stud_height, wall_stud_length
            )
            stud.set_z(self._stud_width)
            stud.set_x(length - half_stud_width)
            self._make_label(stud, self._length_message(wall_stud_length))

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

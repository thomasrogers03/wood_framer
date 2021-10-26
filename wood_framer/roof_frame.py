import typing

from panda3d import core

from . import frame_display


class Display(frame_display.FrameDisplay):
    SERIALIZED_NAME = "roof_frame"

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

        stud_count = int(length / self._SPACE_BETWEEN_STUDS)
        for stud_index in range(stud_count):
            stud = make_stud(self._frame, self._stud_width, self._stud_height, height)
            stud.set_z(self._stud_width)
            stud.set_x(stud_index * self._SPACE_BETWEEN_STUDS + half_stud_width)
            self._make_label(stud, self._length_message(height))

        if stud_count * self._SPACE_BETWEEN_STUDS <= length:
            stud = make_stud(self._frame, self._stud_width, self._stud_height, height)
            stud.set_z(self._stud_width)
            stud.set_x(length - half_stud_width)
            self._make_label(stud, self._length_message(height))

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

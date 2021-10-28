import typing

from panda3d import core

from . import frame_display, stud, top_and_bottom_frame


class Display(top_and_bottom_frame.Display):
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
        super().__init__(
            display_parent, stud_width, stud_height, length, height, make_stud
        )

        stud.add_studs(
            self._display_parent,
            self._frame,
            self._stud_width,
            self._stud_height,
            length,
            height - 2 * self._stud_width,
            self._SPACE_BETWEEN_STUDS,
            self._stud_width,
            make_stud,
        )

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

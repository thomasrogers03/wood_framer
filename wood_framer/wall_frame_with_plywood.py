import typing

from panda3d import core

from . import frame_display, wall_frame


class Display(wall_frame.Display):
    SERIALIZED_NAME = "wall_frame_with_ply_wood"

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

        outside_board = make_stud(self._frame, length, 1 / 2, height)
        outside_board.set_x(length / 2)
        outside_board.set_y(-(self._stud_height / 2 + 1 / 4))
        outside_board.set_transparency(True)
        outside_board.set_alpha_scale(0.75)

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

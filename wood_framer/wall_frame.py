import typing

from panda3d import core


class Display:
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

    def _length_message(self, inches: float):
        feet = 0
        while inches >= Display._INCHES_TO_FEET:
            feet += 1
            inches -= Display._INCHES_TO_FEET
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

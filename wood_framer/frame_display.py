import abc
import typing

from panda3d import core


class FrameDisplay(metaclass=abc.ABCMeta):
    SERIALIZED_NAME = "undefined"
    _INCHES_TO_FEET = 12

    _display_parent: core.NodePath
    _stud_width: float
    _stud_height: float

    @staticmethod
    def create(
        display_parent: core.NodePath,
        stud_width: float,
        stud_height: float,
        length: float,
        height: float,
        make_stud: typing.Callable[[core.NodePath, float, float, float], core.NodePath],
    ) -> "FrameDisplay":
        raise NotImplementedError()

    def destroy(self):
        self._frame.remove_node()

    def _length_message(self, inches: float):
        feet = 0
        while inches >= FrameDisplay._INCHES_TO_FEET:
            feet += 1
            inches -= FrameDisplay._INCHES_TO_FEET
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


_display_types: typing.Dict[str, typing.Type[FrameDisplay]] = {}


def register(name: str, klass: typing.Type[FrameDisplay]):
    _display_types[name] = klass


def get_klass(name: str):
    return _display_types[name]

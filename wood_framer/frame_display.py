import abc
import typing

from panda3d import core


class FrameDisplay(metaclass=abc.ABCMeta):
    SERIALIZED_NAME = "undefined"
    
    _display_parent: core.NodePath

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
    
    def destroy(self) -> None:
        raise NotImplementedError()

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

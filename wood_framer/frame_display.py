import abc
import typing

from panda3d import core

from . import stud


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
        return stud.length_message(self._stud_width, self._stud_height, inches)

    def _make_label(self, parent: core.NodePath, text: str):
        return stud.make_label(self._display_parent, parent, text)


_display_types: typing.Dict[str, typing.Type[FrameDisplay]] = {}


def register(name: str, klass: typing.Type[FrameDisplay]):
    _display_types[name] = klass


def get_klass(name: str):
    return _display_types[name]

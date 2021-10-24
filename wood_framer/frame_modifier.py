import typing

from direct.showbase.DirectObject import DirectObject
from panda3d import bullet, core

from . import highlighter


class FrameModifier(DirectObject):
    def __init__(self, frame_highligher: highlighter.Highlighter):
        self._highligher = frame_highligher
        self._transforming = False
        self._last_mouse_position = core.Point2()

        self.accept("shift-mouse1", self._precheck_mouse)
        self.accept("mouse1-up", self._apply_transform)

    def _precheck_mouse(self):
        self._last_mouse_position = core.Point2(self._highligher.get_mouse_position())
        self._transforming = True

    def _apply_transform(self):
        self._transforming = False

    def update(self):
        if not self._transforming or self._highligher.selected_frame is None:
            return

        new_mouse_position = core.Point2(self._highligher.get_mouse_position())
        mouse_delta: core.Vec2 = new_mouse_position - self._last_mouse_position

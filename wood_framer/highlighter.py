import typing

from direct.showbase.DirectObject import DirectObject
from panda3d import bullet, core

from . import frame


class Highlighter(DirectObject):
    def __init__(
        self,
        render: core.NodePath,
        mouse_watcher: core.MouseWatcher,
        lens: core.Lens,
        camera: core.NodePath,
        world: bullet.BulletWorld,
    ):
        self._render = render
        self._mouse_watcher = mouse_watcher
        self._lens = lens
        self._camera = camera
        self._world = world

        self._highlighted_frame: typing.Optional[frame.Frame] = None
        self._selected_frame: typing.Optional[frame.Frame] = None

        self._mouse_down = False
        self._last_mouse_position = core.Point2()

        self.accept("mouse1", self._precheck_mouse)
        self.accept("mouse1-up", self._handle_mouse_click)

    @property
    def selected_frame(self):
        return self._selected_frame

    def update(self):
        if self._mouse_down:
            return

        source, target = self._extrude_mouse_to_render_transform()
        if source is None:
            return

        if self._highlighted_frame is not None:
            self._highlighted_frame.set_highlight(frame.FrameHighlight.none)
            self._highlighted_frame = None

        hit: bullet.BulletClosestHitRayResult = self._world.ray_test_closest(
            source, target, core.BitMask32.all_on()
        )
        if hit.has_hit():
            highlighted_frame = frame.Frame.frame_from_node(hit.node)
            if not highlighted_frame.is_selected:
                self._highlighted_frame = highlighted_frame
                self._highlighted_frame.set_highlight(frame.FrameHighlight.highlighted)

    def get_mouse_position(self):
        if not self._mouse_watcher.has_mouse():
            return core.Point2()

        return typing.cast(core.Point2, self._mouse_watcher.get_mouse())

    def _precheck_mouse(self):
        self._last_mouse_position = core.Point2(self.get_mouse_position())
        self._mouse_down = True

    def _handle_mouse_click(self):
        self._mouse_down = False

        new_mouse_position = core.Point2(self.get_mouse_position())
        mouse_delta: core.Vec2 = new_mouse_position - self._last_mouse_position
        if mouse_delta.length_squared() > 0.00001:
            return

        if self._selected_frame is not None:
            self._selected_frame.set_highlight(frame.FrameHighlight.none)
            self._selected_frame = None

        if self._highlighted_frame is not None:
            self._selected_frame = self._highlighted_frame
            self._selected_frame.set_highlight(frame.FrameHighlight.selected)
            self._highlighted_frame = None

    def _extrude_mouse_to_render_transform(
        self,
    ) -> typing.Tuple[typing.Optional[core.Point3], typing.Optional[core.Point3]]:
        if not self._mouse_watcher.has_mouse():
            return None, None

        mouse = self._mouse_watcher.get_mouse()
        source: core.Point3 = core.Point3()
        target: core.Point3 = core.Point3()

        self._lens.extrude(mouse, source, target)

        source = self._render.get_relative_point(self._camera, source)
        target = self._render.get_relative_point(self._camera, target)

        return source, target

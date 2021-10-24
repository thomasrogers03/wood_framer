import typing
import uuid

from panda3d import bullet, core


class FrameDisplay:
    _SPACE_BETWEEN_STUDS = 16

    def __init__(
        self,
        display_parent: core.NodePath,
        length: float,
        height: float,
        make_two_by_four: typing.Callable[[core.NodePath, float], core.NodePath],
    ):
        self._frame: core.NodePath = display_parent.attach_new_node("frame")
        self.destroy = self._frame.remove_node
        self.set_position = self._frame.set_pos
        self.set_rotation = self._frame.set_hpr

        bottom = make_two_by_four(self._frame, length)
        bottom.set_r(90)
        bottom.set_z(1)

        top = make_two_by_four(self._frame, length)
        top.set_r(90)
        top.set_z(height - 1)

        stud_count = int(length / self._SPACE_BETWEEN_STUDS)
        for stud_index in range(stud_count):
            stud = make_two_by_four(self._frame, height - 4)
            stud.set_z(2)
            stud.set_x(stud_index * self._SPACE_BETWEEN_STUDS + 1)

        if stud_count * self._SPACE_BETWEEN_STUDS <= length:
            stud = make_two_by_four(self._frame, height - 4)
            stud.set_z(2)
            stud.set_x(length - 1)


class Frame:
    def __init__(
        self,
        scene: core.NodePath,
        world: bullet.BulletWorld,
        length: float,
        height: float,
        make_two_by_four: typing.Callable[[core.NodePath, float], core.NodePath],
    ):
        self._length = length
        self._height = height
        self._make_two_by_four = make_two_by_four

        frame_id = uuid.uuid4()
        self._display_parent: core.NodePath = scene.attach_new_node(f"frame-{frame_id}")
        self.set_position = self._display_parent.set_pos
        self.set_rotation = self._display_parent.set_hpr

        frame_boundry_shape = bullet.BulletBoxShape(core.Vec3(0.5, 0.5, 0.5))
        frame_boundry_node = bullet.BulletRigidBodyNode(f"frame-{frame_id}")
        frame_boundry_node.add_shape(
            frame_boundry_shape,
            core.TransformState.make_pos(core.Vec3(0.5, 0, 0.5)),
        )
        frame_boundry_node.set_kinematic(True)
        frame_boundry_node.set_mass(0)

        world.attach(frame_boundry_node)
        self._frame_boundry: typing.Optional[
            core.NodePath
        ] = self._display_parent.attach_new_node(frame_boundry_node)

        self._frame_display: typing.Optional[FrameDisplay] = None
        self.update(self._length, self._height)

    def update(self, length: float, height: float):
        if self._frame_display is not None:
            self._frame_display.destroy()

        self._length = length
        self._height = height

        self._frame_boundry.set_scale(self._length, 4, self._height)
        self._frame_display = FrameDisplay(
            self._display_parent, self._length, self._height, self._make_two_by_four
        )

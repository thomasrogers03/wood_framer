import typing
import uuid

from panda3d import bullet, core


class FrameDisplay:
    _SPACE_BETWEEN_STUDS = 16

    def __init__(
        self,
        scene: core.NodePath,
        world: bullet.BulletWorld,
        length: float,
        height: float,
        make_two_by_four: typing.Callable[[core.NodePath, float], core.NodePath],
    ):
        frame_id = uuid.uuid4()

        frame_boundry_shape = bullet.BulletBoxShape(
            core.Vec3(length / 2, 2, height / 2)
        )
        frame_boundry_node = bullet.BulletRigidBodyNode(f"frame-{frame_id}")
        frame_boundry_node.add_shape(
            frame_boundry_shape,
            core.TransformState.make_pos(core.Vec3(length / 2, 0, height / 2)),
        )
        frame_boundry_node.set_kinematic(True)
        frame_boundry_node.set_mass(0)

        world.attach(frame_boundry_node)
        self._frame_boundry: typing.Optional[core.NodePath] = scene.attach_new_node(
            frame_boundry_node
        )

        bottom = make_two_by_four(self._frame_boundry, length)
        bottom.set_r(90)
        bottom.set_z(1)

        top = make_two_by_four(self._frame_boundry, length)
        top.set_r(90)
        top.set_z(height - 1)

        stud_count = int(length / self._SPACE_BETWEEN_STUDS)
        for stud_index in range(stud_count):
            stud = make_two_by_four(self._frame_boundry, height - 4)
            stud.set_z(2)
            stud.set_x(stud_index * self._SPACE_BETWEEN_STUDS + 1)

        if stud_count * self._SPACE_BETWEEN_STUDS <= length:
            stud = make_two_by_four(self._frame_boundry, height - 4)
            stud.set_z(2)
            stud.set_x(length - 1)

    def destroy(self):
        if self._frame_boundry is not None:
            self._frame_boundry.remove_node()
            self._frame_boundry = None


class Frame:
    def __init__(self, _frame_display: FrameDisplay):
        self._frame_display = _frame_display

    def update(self, frame_display: FrameDisplay):
        self._frame_display.destroy()
        self._frame_display = frame_display

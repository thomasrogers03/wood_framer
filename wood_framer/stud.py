import typing

from panda3d import core

INCHES_TO_FEET = 12


def add_studs(
    display_parent: core.NodePath,
    frame: core.NodePath,
    stud_width: float,
    stud_height: float,
    length: float,
    wall_stud_length: float,
    space_between_studs: float,
    bottom: float,
    make_stud: typing.Callable[[core.NodePath, float, float, float], core.NodePath],
):
    half_stud_width = stud_width / 2

    x = -half_stud_width
    length_left = length

    x += stud_width
    length_left -= stud_width
    left_stud = make_stud(frame, stud_width, stud_height, wall_stud_length)
    left_stud.set_z(bottom)
    left_stud.set_x(x)
    make_label(
        display_parent,
        left_stud,
        length_message(stud_width, stud_height, wall_stud_length),
    )
    x += space_between_studs

    while length_left >= space_between_studs + stud_width:
        stud = make_stud(frame, stud_width, stud_height, wall_stud_length)
        stud.set_z(bottom)
        stud.set_x(x)
        make_label(
            display_parent,
            stud,
            length_message(stud_width, stud_height, wall_stud_length),
        )
        x += space_between_studs
        length_left -= space_between_studs

    if length_left > 0:
        right_stud = make_stud(frame, stud_width, stud_height, wall_stud_length)
        right_stud.set_z(bottom)
        right_stud.set_x(length - half_stud_width)
        make_label(
            display_parent,
            right_stud,
            length_message(stud_width, stud_height, wall_stud_length),
        )


def length_message(stud_width: float, stud_height: float, inches: float):
    feet = 0
    while inches >= INCHES_TO_FEET:
        feet += 1
        inches -= INCHES_TO_FEET
    message = f'{stud_width}"x{stud_height}"x'
    if feet > 0:
        message += f"{feet}'"
    if inches > 0:
        message += f'{inches}"'
    return message


def make_label(display_parent: core.NodePath, parent: core.NodePath, text: str):
    text_node = core.TextNode("label")
    text_node.set_text(text)
    text_node.set_text_color(1, 1, 1, 1)
    text_node.set_text_scale(3)
    text_node.set_shadow_color(0, 0, 0, 1)
    text_node.set_card_color(1, 1, 1, 1)

    result: core.NodePath = parent.attach_new_node(text_node)
    result.set_pos(2, -4, 0.5)
    result.set_hpr(0, 0, -90)
    result.set_scale(display_parent, core.Vec3(1, 1, 1))
    result.set_two_sided(True)
    result.set_light_off(1)

    return result

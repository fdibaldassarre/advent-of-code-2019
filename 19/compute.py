#!/usr/bin/env python3

from src.interpreter import OptcodeInterpreter


DIRECTION_RIGHT = 1
DIRECTION_LEFT = -1

SQUARE_SIZE = 100


def read_input():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    return optcode


def get_bound(position, direction):
    x, y = position
    keep = True
    prev_point = None
    prev_status = None
    boundary = None
    while keep:
        optcode = read_input()
        interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
        interpreter.input.put(x)
        interpreter.input.put(y)
        interpreter.run()
        point_status = interpreter.output.get()
        # Check if we changed status
        if prev_point is not None and point_status != prev_status:
            # Found boundary
            keep = False
            if point_status == 1:
                boundary = y
            else:
                boundary = prev_point
        else:
            # Move x towards outside
            if point_status == 0:
                delta = -1
            else:
                delta = 1
            prev_point = y
            prev_status = point_status
            y = y + delta * direction
    return boundary


def get_bound_at_height(x, max_y, direction):
    if direction == DIRECTION_LEFT:
        y = 0
    else:
        y = max_y
    return get_bound((x, y), direction)


def get_square_corner():
    x = 1
    left_prev = None
    right_prev = None
    counter = 0
    boundaries = [(1, 1)]
    while True:
        # Find boundaries over y
        if left_prev is None or x < 4:
            bound_left = get_bound_at_height(x, 10, DIRECTION_LEFT)
        else:
            bound_left = get_bound((x, left_prev), DIRECTION_LEFT)
        if right_prev is None or x < 4:
            bound_right = get_bound_at_height(x, 10, DIRECTION_RIGHT)
        else:
            bound_right = get_bound((x, right_prev), DIRECTION_RIGHT)
        counter += bound_right - bound_left + 1
        left_prev = int(bound_left / x * x + 1)
        right_prev = int(bound_right / x * x + 1)
        boundaries.append((bound_left, bound_right))
        if x >= SQUARE_SIZE:
            # Check if the point may contain a square with side 10
            top = x - (SQUARE_SIZE - 1)
            top_left = bound_left
            top_right = bound_left + (SQUARE_SIZE - 1)
            top_bound_left, top_bound_right = boundaries[top]
            if top_bound_left <= top_right <= top_bound_right:
                # Rectangle found
                corner = (top, top_left)
                break
        x += 1
    return corner


def get_points_in_beam():
    counter = 0
    for x in range(50):
        for y in range(50):
            optcode = read_input()
            interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
            interpreter.input.put(x)
            interpreter.input.put(y)
            interpreter.run()
            res = interpreter.output.get()
            counter += res
    return counter


if __name__ == "__main__":
    points_counter = get_points_in_beam()
    print("There are", points_counter, "points in the beam")
    x, y = get_square_corner()
    print("Corner value is", x * 10000 + y)

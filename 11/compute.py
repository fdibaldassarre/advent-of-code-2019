#!/usr/bin/env python3

import numpy as np
from PIL import Image

from src.interpreter import OptcodeInterpreter

class HullRobot:

    def __init__(self, starting_point):
        self.position = starting_point
        self.delta = (-1, 0)

    def rotate_right(self):
        y, x = self.delta
        self.delta = (x, -1 * y)

    def rotate_left(self):
        y, x = self.delta
        self.delta = (-1 * x, y)

    def move(self):
        y, x = self.position
        dy, dx = self.delta
        self.position = (y + dy, x + dx)

    def get_position(self):
        return self.position


def is_duplicate(point, seen):
    a, b = point
    duplicated = False
    for el in seen:
        x, y = el
        if a == x and b == y:
            duplicated = True
            break
    return duplicated


"""
Return the delta needed to align the image to (0,0)
and the image size

"""
def get_image_shape(table):
    min_x = min(list(map(lambda el: el[1], table)))
    min_y = min(list(map(lambda el: el[0], table)))
    max_x = max(list(map(lambda el: el[1], table)))
    max_y = max(list(map(lambda el: el[0], table)))
    delta = (-1 * min_y, -1 * min_x)
    dy = max_y - min_y + 1
    dx = max_x - min_x + 1
    return delta, (dy, dx)


def compute(paint_start_point=False):
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))

    interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
    interpreter.run_async()
    start_point = (0, 0)
    robot = HullRobot(start_point)
    table = []
    if paint_start_point:
        table.append(start_point)
    painted_points = []
    while True:
        pos = robot.get_position()
        color = 1 if pos in table else 0
        interpreter.input.put(color)
        try:
            output_color = interpreter.output.get(timeout=1)
        except Exception:
            break
        turn = interpreter.output.get()
        if output_color == 1 and not is_duplicate(pos, table):
            table.append(pos)
        elif output_color == 0 and is_duplicate(pos, table):
            table.remove(pos)
        if not is_duplicate(pos, painted_points):
            painted_points.append(pos)
        if turn == 0:
            robot.rotate_left()
        else:
            robot.rotate_right()
        robot.move()
        # print("Debug", len(table))
    if paint_start_point:
        delta, size = get_image_shape(table)
        image = np.zeros(shape=size, dtype=np.uint8)
        dy, dx = delta
        for y, x in table:
            image[y+dy, x+dx] = 255
        dec_image = Image.fromarray(image)
        dec_image.save("res.png")
        print("Saved code to image res.png")
    else:
        print("Painted points: %d" % len(painted_points))


compute(paint_start_point=False)
compute(paint_start_point=True)

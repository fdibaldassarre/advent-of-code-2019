#!/usr/bin/env python3


def get_linfy_norm(point):
    x, y = point
    return abs(x) + abs(y)


class Segment:

    def __init__(self, start, delta):
        self.start = start
        self.delta = delta
        self.previous_steps = None

    def get_end_point(self):
        x0, y0 = self.start
        dx, dy = self.delta
        return (x0 + dx, y0 + dy)

    def is_vertical(self):
        dx, _ = self.delta
        return dx == 0

    def is_horizontal(self):
        _, dy = self.delta
        return dy == 0

    def contains_point(self, point):
        x, y = point
        x0, y0 = self.start
        dx, dy = self.delta
        if self.is_horizontal():
            return y == y0 and min(x0, x0 + dx) <= x and x <= max(x0, x0 + dx)
        else:
            return x == x0 and min(y0, y0 + dy) <= y and y <= max(y0, y0 + dy)

    def get_steps_to_point(self, point):
        if not self.contains_point(point):
            print("Point does not belong to segment")
            return None
        x, y = point
        x0, y0 = self.start
        return self.previous_steps + abs(x - x0) + abs(y - y0)

def get_intersection(a, b):
    intersection = [None, None]
    for sgm in [a, b]:
        if sgm.is_horizontal():
            _, y = sgm.start
            intersection[1] = y
        else:
            x, _ = sgm.start
            intersection[0] = x
    # Check intersection is admissible
    x, y = intersection
    if x is None or y is None:
        return None
    if a.contains_point(intersection) and b.contains_point(intersection):
        return intersection
    else:
        return None

def move(start_point, movement):
    start_x, start_y = start_point
    mov_type = movement[0]
    space = int(movement[1:])
    delta_x, delta_y = 0, 0
    if mov_type == "L":
        delta_x = delta_x - space
    elif mov_type == "R":
        delta_x = delta_x + space
    elif mov_type == "D":
        delta_y = delta_y - space
    elif mov_type == "U":
        delta_y = delta_y + space
    else:
        print("Unknown movement %s" % movement)
    delta = (delta_x, delta_y)
    return Segment(start_point, delta)


with open("input") as hand:
    mov1_raw = hand.readline()
    mov2_raw = hand.readline()

line1 = mov1_raw.split(",")
line2 = mov2_raw.split(",")

point_wire1 = [0, 0]
point_wire2 = [0, 0]
steps_wire1 = 0
steps_wire2 = 0


segments1 = []
current_point = (0, 0)
wire1_steps = 0
for movement in line1:
    segment = move(current_point, movement)
    segment.previous_steps = wire1_steps
    segments1.append(segment)
    current_point = segment.get_end_point()
    wire1_steps = segment.get_steps_to_point(current_point)

current_point = (0, 0)
wire2_steps = 0
min_steps = None
intersection_point = None
for movement in line2:
    segment = move(current_point, movement)
    segment.previous_steps = wire2_steps
    # Check intersections
    for line1segment in segments1:
        intersection = get_intersection(segment, line1segment)
        if intersection is not None:
            steps = segment.get_steps_to_point(intersection) + line1segment.get_steps_to_point(intersection)
            if steps > 0 and (min_steps is None or steps < min_steps):
                min_steps = steps
                intersection_point = intersection
    current_point = segment.get_end_point()
    wire2_steps = segment.get_steps_to_point(current_point)

print(min_steps)
print(intersection_point)

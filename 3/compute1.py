#!/usr/bin/env python3

class Segment:

    def __init__(self, start, delta):
        self.start = start
        self.delta = delta

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

def get_linfy_norm(point):
    x, y = point
    return abs(x) + abs(y)


with open("input") as hand:
    mov1_raw = hand.readline()
    mov2_raw = hand.readline()

line1 = mov1_raw.split(",")
line2 = mov2_raw.split(",")

segments1 = []
current_point = (0, 0)
for movement in line1:
    segment = move(current_point, movement)
    segments1.append(segment)
    current_point = segment.get_end_point()

current_point = (0, 0)
min_distance = None
intersection_point = None
for movement in line2:
    segment = move(current_point, movement)
    # Check intersections
    for line1segment in segments1:
        intersection = get_intersection(segment, line1segment)
        if intersection is not None:
            distance = get_linfy_norm(intersection)
            if distance > 0 and (min_distance is None or distance < min_distance):
                min_distance = distance
                intersection_point = intersection
    current_point = segment.get_end_point()

print(min_distance)
print(intersection_point)

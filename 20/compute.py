#!/usr/bin/env python3


POINT_WALL = "#"
POINT_MAZE = "."


def get_surrounding_points(point):
    if len(point) == 2:
        x, y = point
        z = None
    else:
        x, y, z = point
    north = (x, y + 1)
    south = (x, y - 1)
    east = (x + 1, y)
    west = (x - 1, y)
    surr = [north, south, east, west]
    if z is None:
        return surr
    else:
        return [(x, y, z) for x, y in surr]


class PlutoMaze:

    def __init__(self):
        self.enable_folding = False
        self.positions = {}
        self.warp_points = {}
        self.start_point = None
        self.end_point = None
        self.explored = {}
        self.outer_points = {}

    def set_folding(self, folding):
        self.enable_folding = folding

    def set(self, position, element):
        if element == "#":
            self.positions[position] = 0
        elif element == ".":
            self.positions[position] = 1

    def is_empty(self, position):
        if len(position) == 2:
            x, y = position
        else:
            x, y, _ = position
        if (x, y) not in self.positions:
            return False
        return self.positions[(x, y)] == 1

    def is_end_point(self, point):
        x, y, z = point
        ex, ey, ez = self.end_point
        return x == ex and y == ey and z == ez

    def set_warp_points(self, labels):
        # Setup the warp points
        for el in labels:
            surrounding = get_surrounding_points(el)
            label_name = labels[el]
            for point in surrounding:
                if self.is_empty(point):
                    sx, sy = point
                    self.warp_points[point] = label_name
                    if label_name == "AA":
                        self.start_point = (sx, sy, 0)
                    elif label_name == "ZZ":
                        self.end_point = (sx, sy, 0)
        # Set outer points
        self._set_outer_points()

    def _set_outer_points(self):
        # Find maze bound box
        max_x = 0
        max_y = 0
        for x, y in self.positions:
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
        for x, y in self.warp_points:
            if x == 2 or x == max_x or y == 2 or y == max_y:
                self.outer_points[(x, y)] = 1

    def get_surrounding_points(self, point):
        sx, sy, z = point
        surrounding = get_surrounding_points(point)
        if (sx, sy) in self.warp_points:
            label_name = self.warp_points[(sx, sy)]
            for el, warp_name in self.warp_points.items():
                if warp_name == label_name:
                    x, y = el
                    if sx != x and sy != y:
                        if (sx, sy) in self.outer_points:
                            sz = z - 1
                        else:
                            sz = z + 1
                        if self.enable_folding:
                            if sz >= 0:
                                surrounding.append((x, y, sz))
                        else:
                            surrounding.append((x, y, 0))
        return surrounding

    def get_start_point(self):
        return self.start_point

    def explore(self, point):
        self.explored[point] = 1


def get_label_name(point, label_positions):
    surrounding = get_surrounding_points(point)
    x1, y1 = point
    c1 = label_positions[point]
    label_name = None
    for el in surrounding:
        if el in label_positions:
            # Found pair
            x2, y2 = el
            c2 = label_positions[el]
            if x1 < x2 or y1 < y2:
                label_name = c1 + c2
            else:
                label_name = c2 + c1
            break
    return label_name


def read_input():
    labels_positions = {}
    underground_map = PlutoMaze()
    with open("input") as hand:
        y = 0
        for line in hand:
            for x, c in enumerate(line[:-1]):
                if c != " ":
                    underground_map.set((x, y), c)
                    if c != POINT_WALL and c != POINT_MAZE:
                        labels_positions[(x, y)] = c
            y += 1
    labels = dict()
    for point in labels_positions:
        label_name = get_label_name(point, labels_positions)
        labels[point] = label_name
    underground_map.set_warp_points(labels)
    return underground_map


def get_steps(folding=False):
    maze = read_input()
    if folding:
        maze.set_folding(True)
    distance = 0
    explored = dict()
    explored[maze.get_start_point()] = 1
    level = list()
    level.append(maze.get_start_point())
    end_distance = None
    while end_distance is None:
        next_level = []
        distance += 1
        for point in level:
            surrounding = maze.get_surrounding_points(point)
            for p in surrounding:
                if maze.is_empty(p) and p not in explored:
                    explored[p] = 1
                    next_level.append(p)
        for point in next_level:
            if maze.is_end_point(point):
                end_distance = distance
                break
        level = next_level
    return end_distance


if __name__ == "__main__":
    steps = get_steps()
    print("Steps from AA to ZZ", steps)
    steps_folding = get_steps(folding=True)
    print("Steps from AA to ZZ multilevel", steps_folding)
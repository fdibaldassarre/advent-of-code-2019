#!/usr/bin/env python3

from src.interpreter import OptcodeInterpreter

POINT_EMPTY = 0
POINT_WALL = 1
POINT_OXYGEN = 2

MOVE_NORTH = 1
MOVE_SOUTH = 2
MOVE_EAST = 3
MOVE_WEST = 4


def get_linfy_distance(a, b):
    x_a, y_a = a
    x_b, y_b = b
    return abs(x_a - x_b) + abs(y_a - y_b)


def get_surrounding_points(point):
    x, y = point
    north = (x, y + 1)
    south = (x, y - 1)
    east = (x + 1, y)
    west = (x - 1, y)
    return [(MOVE_NORTH, north), (MOVE_SOUTH, south), (MOVE_EAST, east), (MOVE_WEST, west)]


class SpacePath:

    def __init__(self, start, directions=None, end_point=None):
        self.start = start
        self.directions = directions if directions is not None else []
        self.end = end_point if end_point is not None else start

    def get_directions(self):
        return self.directions

    def get_end_point(self):
        return self.end

    def get_distance(self):
        return len(self.directions)

    def append_point(self, point, direction):
        self.directions.append((direction, point))
        self.end = point

    def clone(self):
        directions = [direction for direction in self.directions]
        return SpacePath(self.start, directions, self.end)


class SpaceMap:

    def __init__(self):
        self._space = dict()
        self._unknown = dict()
        self._distance_from_start = dict()
        self._distance_from_start[(0, 0)] = 0

    def _update_unknown_points(self, position):
        surrounding = get_surrounding_points(position)
        from_distance = self._distance_from_start[position]
        for _, point in surrounding:
            if point not in self._distance_from_start:
                self._distance_from_start[point] = from_distance + 1
                self._unknown[point] = 1

    def explore(self, position, point_type):
        self._space[position] = point_type
        if position in self._unknown:
            del self._unknown[position]
        if point_type != POINT_WALL:
            self._update_unknown_points(position)

    def get_empty_positions(self):
        positions = []
        for el in self._space:
            if self._space[el] == POINT_EMPTY:
                positions.append(el)
        return positions

    def get_unknown_points(self):
        return self._unknown

    def get_distance_from_start(self, position):
        return self._distance_from_start[position]

    def get_path(self, start, target):
        possible_paths = list()
        explored_points = list()
        starting_path = SpacePath(start)
        possible_paths.append(starting_path)
        path_to_target = None
        while path_to_target is None:
            # Get the next path to examine
            possible_paths = sorted(possible_paths, key=lambda path: path.get_distance() + get_linfy_distance(path.get_end_point(), target))
            best_path = possible_paths[0]
            end_point = best_path.get_end_point()
            # Expand the path
            surrounding = get_surrounding_points(end_point)
            for direction, point in surrounding:
                if point in explored_points:
                    continue
                new_path = best_path.clone()
                new_path.append_point(point, direction)
                if get_linfy_distance(point, target) == 0:
                    # This is my target path !
                    path_to_target = new_path
                    break
                elif point in self._space and self._space[point] != POINT_WALL:
                    possible_paths.append(new_path)
            if path_to_target is not None:
                break
            explored_points.append(end_point)
            # Remove the read path
            del possible_paths[0]
        return path_to_target


class RepairDroid:

    def __init__(self):
        self.position = (0, 0)
        self.oxygen_position = None
        self._path = None
        self._path_index = None
        self._requested_position = None

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def get_requested_position(self):
        return self._requested_position

    def set_oxigen_position(self, position):
        self.oxygen_position = position

    def get_oxygen_position(self):
        return self.oxygen_position

    def set_path(self, path):
        self._path = path
        self._path_index = 0

    def act(self, space):
        move, requested_position = self._pick_direction(space)
        self._requested_position = requested_position
        return move

    def _pick_direction(self, space):
        direction = self._follow_path()
        if direction is not None:
            return direction
        unknown_points = space.get_unknown_points()
        if len(unknown_points) == 0:
            return None, None
        sorted_unknown = sorted(unknown_points, key=lambda point: space.get_distance_from_start(point))
        target = sorted_unknown[0]
        path = space.get_path(self.get_position(), target)
        self.set_path(path)
        return self._follow_path()

    def _follow_path(self):
        if self._path is None:
            return None
        directions = self._path.get_directions()
        path_idx = self._path_index
        if path_idx < len(directions):
            self._path_index += 1
            return directions[path_idx]
        else:
            self._path = None
            self._path_index = None
            return None


def read_input():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    return optcode


def compute_oxygen_time(space, oxigen_position):
    # Find positions to fill
    oxigen_distance = dict()
    for pos in space.get_empty_positions():
        oxigen_distance[pos] = None
    oxigen_distance[oxigen_position] = 0
    current_positions = [oxigen_position]
    dist = 0
    while len(current_positions) > 0:
        # Fill the next
        next_positions = []
        dist += 1
        for position in current_positions:
            # Find surrounding
            surrounding = get_surrounding_points(position)
            for _, point in surrounding:
                if point in oxigen_distance and oxigen_distance[point] is None:
                    oxigen_distance[point] = dist
                    next_positions.append(point)
        current_positions = next_positions
    dist -= 1
    print("Time needed for oxygen fill:", dist)


def compute():
    space = SpaceMap()
    droid = RepairDroid()
    space.explore(droid.get_position(), POINT_EMPTY)
    optcode = read_input()
    interpreter = OptcodeInterpreter(optcode, quiet_mode=True)

    def on_input_requested():
        if not interpreter.output.empty():
            # Get status
            status = interpreter.output.get()
            requested_point = droid.get_requested_position()
            if status == 0:
                # Hit a wall
                space.explore(requested_point, POINT_WALL)
            elif status == 1:
                # Empty space, position updated
                space.explore(requested_point, POINT_EMPTY)
                droid.set_position(requested_point)
            elif status == 2:
                # Oxygen space, position updated
                space.explore(requested_point, POINT_OXYGEN)
                droid.set_oxigen_position(requested_point)
                droid.set_position(requested_point)
                print("Oxigen found at distance:", space.get_distance_from_start(requested_point))
        move = droid.act(space)
        if move is None:
            compute_oxygen_time(space, droid.get_oxygen_position())
            interpreter.input.put(0)
        else:
            interpreter.input.put(move)

    interpreter.set_input_request_listener(on_input_requested)
    interpreter.run()


compute()

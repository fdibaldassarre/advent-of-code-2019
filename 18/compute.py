#!/usr/bin/env python3

POINT_ENTRANCE = "@"
POINT_WALL = "#"
POINT_EMPTY = "."


class UndergroundPosition:

    def __init__(self, points, distance=0, keys=None):
        self.points = [point for point in points]
        self.distance = distance if distance is not None else distance
        self.keys = keys if keys is not None else []

    def update(self, source, update):
        self.points.remove(source)
        self.points.append(update)

    def add_key(self, key):
        if key not in self.keys:
            self.keys.append(key)

    def get_keys(self):
        return self.keys

    def get_n_keys(self):
        return len(self.keys)

    def has_key_for(self, door):
        return door.lower() in self.keys

    def get_distance(self):
        return self.distance

    def get_points(self):
        return self.points


class PossiblePath:

    def __init__(self, origin, current_point=None, distance=0):
        self.origin = origin
        self.point = current_point if current_point is not None else self.origin
        self.distance = distance
        self.needed_keys = []
        self.collected_keys = []
        self.seen = {}

    def get_origin(self):
        return self.origin

    def move(self, point):
        self.point = point
        self.distance += 1
        self.seen[point] = 1

    def get_point(self):
        return self.point

    def is_seen(self, point):
        return point in self.seen

    def get_size(self):
        return len(self.seen)

    def append_key(self, key):
        if key not in self.needed_keys:
            self.needed_keys.append(key)

    def collect_key(self, key):
        if key not in self.collected_keys:
            self.collected_keys.append(key)

    def get_distance(self):
        return self.distance

    def get_needed_keys(self):
        return self.needed_keys

    def get_collected_keys(self):
        return self.collected_keys

    def can_be_reached_from(self, position):
        needed_keys = self.get_needed_keys()
        missing_key = False
        for needed_key in needed_keys:
            if needed_key not in position.get_keys():
                missing_key = True
                break
        return not missing_key

    def clone(self):
        copy = PossiblePath(self.get_origin(), self.get_point(), distance=self.distance)
        for point in self.seen:
            copy.seen[point] = 1
        for key in self.needed_keys:
            copy.append_key(key)
        for key in self.collected_keys:
            copy.collect_key(key)
        return copy


class UndergroundMap:

    def __init__(self):
        self.positions = {}
        self.entrances = list()
        self.keys = {}
        self.doors = {}
        self.paths_cache = dict()

    def set(self, position, element):
        if element == "#":
            self.positions[position] = 0
        elif element == ".":
            self.positions[position] = 1
        elif element == "@":
            self.positions[position] = 1
            self.entrances.append(position)
        elif element == element.lower():
            self.positions[position] = 1
            self.keys[position] = element
        else:
            self.positions[position] = -1
            self.doors[position] = element

    def upgrade(self):
        x, y = self.entrances[0]
        self.entrances.clear()
        self.set((x, y), "#")
        self.set((x + 1, y), "#")
        self.set((x - 1, y), "#")
        self.set((x, y + 1), "#")
        self.set((x, y - 1), "#")
        self.set((x - 1, y - 1), "@")
        self.set((x + 1, y - 1), "@")
        self.set((x - 1, y + 1), "@")
        self.set((x + 1, y + 1), "@")

    def can_be_moved_to(self, position, keys):
        can_be_moved = self.positions[position]
        if can_be_moved == 0:
            return False
        elif can_be_moved == 1:
            return True
        else:
            needed_key = self.doors[position].lower()
            return needed_key in keys

    def is_not_wall(self, position):
        return self.positions[position] != 0

    def is_door(self, position):
        if position in self.doors:
            return self.doors[position]
        else:
            return None

    def get_entrances(self):
        return self.entrances

    def get_key(self, position):
        if position in self.keys:
            return self.keys[position]
        else:
            return None

    def get_keys(self):
        return self.keys

    def get_paths_to_keys(self, start):
        if start in self.paths_cache:
            return self.paths_cache[start]
        paths_to_keys = dict()
        possible_paths = list()
        possible_paths.append(PossiblePath(start))
        while len(possible_paths) > 0:
            next_path = possible_paths[0]
            current_point = next_path.get_point()
            for surronding in get_surrounding_points(current_point):
                if not next_path.is_seen(surronding) and self.is_not_wall(surronding):
                    possible_path = next_path.clone()
                    possible_path.move(surronding)
                    door = self.is_door(surronding)
                    if door is not None:
                        possible_path.append_key(door.lower())
                    new_key = self.get_key(surronding)
                    if new_key is not None:
                        # Possible path to key
                        possible_path.collect_key(new_key)
                        if new_key in paths_to_keys:
                            if possible_path.get_distance() < paths_to_keys[new_key].get_distance():
                                paths_to_keys[new_key] = possible_path
                        else:
                            paths_to_keys[new_key] = possible_path
                    possible_paths.append(possible_path)
            possible_paths.remove(next_path)
            possible_paths = sorted(possible_paths, key=lambda path: path.get_distance())
        if start not in self.paths_cache:
            self.paths_cache[start] = paths_to_keys
        return paths_to_keys


class PossiblePositions:

    def __init__(self, underground_map):
        self.underground_map = underground_map
        self.positions = dict()
        total_keys = underground_map.get_keys()
        for n in range(len(total_keys) + 1):
            self.positions[n] = []
        entrance = UndergroundPosition(underground_map.get_entrances())
        self.positions[0].append(entrance)
        self.priority_positions = list()

    def add(self, position):
        self.positions[position.get_n_keys()].append(position)
        self.priority_positions.append(position)

    def remove(self, position):
        if position is not None:
            self.positions[position.get_n_keys()].remove(position)

    def get_next(self):
        position = None
        if len(self.priority_positions) > 0:
            position = self.priority_positions[0]
        else:
            for n_keys in range(len(self.positions) - 1, -1, -1):
                positions = self.positions[n_keys]
                if len(positions) > 0:
                    position = positions[0]
                    break
        self.priority_positions.clear()
        return position

    def prune(self, final_path):
        for n in range(len(self.positions)):
            pruned = []
            for position in self.positions[n]:
                if guess_minimum_final_distance(position, self.underground_map) < final_path.get_distance():
                    pruned.append(position)
            self.positions[n] = pruned

    def has_positions(self):
        has_positions = False
        for _, paths in self.positions.items():
            if len(paths) > 0:
                has_positions = True
                break
        return has_positions


def read_input():
    underground_map = UndergroundMap()
    with open("input") as hand:
        y = 0
        for line in hand:
            for x, c in enumerate(line.strip()):
                underground_map.set((x, y), c)
            y += 1
    return underground_map


def get_surrounding_points(point):
    x, y = point
    north = (x, y + 1)
    south = (x, y - 1)
    east = (x + 1, y)
    west = (x - 1, y)
    return [north, south, east, west]


def guess_minimum_final_distance(position, underground_map):
    points = position.get_points()
    max_distance = 0
    for point in points:
        point_to_keys = underground_map.get_paths_to_keys(point)
        for key in point_to_keys:
            if key not in position.get_keys():
                key_position = point_to_keys[key]
                if key_position.get_distance() > max_distance:
                    max_distance = key_position.get_distance()
    return position.get_distance() + max_distance


def get_free_keys(underground_map):
    all_paths = dict()
    for point in underground_map.get_entrances():
        paths = underground_map.get_paths_to_keys(point)
        for key in paths:
            all_paths[key] = paths[key]

    all_needed_keys = list()
    for _, path in all_paths.items():
        for k in path.get_needed_keys():
            if k not in all_needed_keys:
                all_needed_keys.append(k)

    free_keys = list()
    for key in all_paths:
        if key not in all_needed_keys:
            # Check if it is collected somewhere else
            for other_key in all_paths:
                if other_key == key:
                    continue
                other_key_path = all_paths[other_key]
                if key in other_key_path.get_collected_keys():
                    free_keys.append(key)
                    break
    return free_keys


def move_to_keys(position, point_to_keys, free_keys):
    new_positions = list()
    for key in point_to_keys:
        if key not in free_keys and key not in position.get_keys():
            key_position = point_to_keys[key]
            if key_position.can_be_reached_from(position):
                # I can reach it this key
                total_distance = position.get_distance() + key_position.get_distance()
                new_position = UndergroundPosition(position.get_points(), distance=total_distance)
                new_position.update(key_position.get_origin(), key_position.get_point())
                for old_key in position.get_keys():
                    new_position.add_key(old_key)
                for collected_key in key_position.get_collected_keys():
                    new_position.add_key(collected_key)
                new_positions.append(new_position)
    return new_positions


def compute(upgrade=False):
    underground_map = read_input()
    if upgrade:
        underground_map.upgrade()

    total_keys = underground_map.get_keys()
    possible_positions = PossiblePositions(underground_map)
    free_keys = get_free_keys(underground_map)

    final_path = None
    while possible_positions.has_positions():
        position = possible_positions.get_next()
        if len(total_keys) == len(position.get_keys()):
            # Final path
            if final_path is None or position.get_distance() < final_path.get_distance():
                final_path = position
                possible_positions.prune(final_path)
        else:
            # Reach other keys
            point_to_keys = dict()
            for point in position.get_points():
                for key, path in underground_map.get_paths_to_keys(point).items():
                    point_to_keys[key] = path
            for new_position in move_to_keys(position, point_to_keys, free_keys):
                if final_path is None or \
                        guess_minimum_final_distance(new_position, underground_map) < final_path.get_distance():
                    possible_positions.add(new_position)
            possible_positions.remove(position)
    return final_path.get_distance()


if __name__ == "__main__":
    min_steps = compute()
    print("Shortest path has", min_steps, "steps")
    min_steps2 = compute(upgrade=True)
    print("Shortest path in upgraded map has", min_steps2, "steps")

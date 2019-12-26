#!/usr/bin/env python3

import sys

GRID_SIZE = 5


class FoldingGrid:

    def __init__(self):
        self.grids = dict()
        self.level_min = 0
        self.level_max = 0

    def initialize(self, grid):
        self.grids[0] = grid

    def _append_new_levels(self):
        # Append if there is at least one bug
        lowest_grid = self.grids[self.level_min]
        if count_bugs(lowest_grid) > 0:
            self.level_min -= 1
            self.grids[self.level_min] = create_empty_grid()
        highest_grid = self.grids[self.level_max]
        if count_bugs(highest_grid) > 0:
            self.level_max += 1
            self.grids[self.level_max] = create_empty_grid()

    def update(self):
        self._append_new_levels()
        new_grids = dict()
        for level in self.grids:
            new_grid = self._update_grid_ml(level)
            new_grids[level] = new_grid
        self.grids = new_grids

    def get_bugs(self):
        n_bugs = 0
        for _, grid in self.grids.items():
            n_bugs += count_bugs(grid)
        return n_bugs

    def _update_grid_ml(self, level):
        new_grid = dict()
        for pos in self.grids[level]:
            n_bugs = 0
            px, py = pos
            if px == 2 and py == 2:
                new_grid[2, 2] = 0
                continue

            for tile in get_surrounding_points_ml(pos, level):
                x, y, z = tile
                position = (x, y)
                if z in self.grids and position in self.grids[z] and self.grids[z][position] == 1:
                    n_bugs += 1
            if self.grids[level][pos] == 1 and n_bugs != 1:
                # Bug died
                new_grid[pos] = 0
            elif self.grids[level][pos] == 0 and (n_bugs == 1 or n_bugs == 2):
                # Infested
                new_grid[pos] = 1
            else:
                new_grid[pos] = self.grids[level][pos]
        return new_grid


def create_empty_grid():
    grid = dict()
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[(x, y)] = 0
    return grid


def count_bugs(grid):
    n_bugs = 0
    for pos in grid:
        if grid[pos] == 1:
            n_bugs += 1
    return n_bugs


def get_surrounding_points(point):
    x, y = point
    north = (x, y + 1)
    south = (x, y - 1)
    east = (x + 1, y)
    west = (x - 1, y)
    return [north, south, east, west]


def get_surrounding_points_ml(point, z):
    x, y = point
    north = (x, y + 1)
    south = (x, y - 1)
    east = (x + 1, y)
    west = (x - 1, y)
    surr = list()
    for sx, sy in [north, south, east, west]:
        # Do not include the center point
        if sx != 2 or sy != 2:
            surr.append((sx, sy, z))
    if x == 0:
        # Add tile from level up
        top_left = (1, 2, z - 1)
        surr.append(top_left)
    elif x == 4:
        top_right = (3, 2, z - 1)
        surr.append(top_right)
    if y == 0:
        top_top = (2, 1, z - 1)
        surr.append(top_top)
    elif y == 4:
        top_bot = (2, 3, z - 1)
        surr.append(top_bot)
    if x == 2:
        # Add all 5 from bottom
        if y == 1:
            bottom_top_line = [(n, 0, z + 1) for n in range(GRID_SIZE)]
            surr.extend(bottom_top_line)
        elif y == 3:
            bottom_bottom_line = [(n, 4, z + 1) for n in range(GRID_SIZE)]
            surr.extend(bottom_bottom_line)
    elif y == 2:
        # Add all 5 from bottom
        if x == 1:
            bottom_top_line = [(0, n, z + 1) for n in range(GRID_SIZE)]
            surr.extend(bottom_top_line)
        elif x == 3:
            bottom_bottom_line = [(4, n, z + 1) for n in range(GRID_SIZE)]
            surr.extend(bottom_bottom_line)
    return surr


def read_input():
    grid = dict()
    with open("input") as hand:
        y = 0
        for line in hand:
            line = line.strip()
            for x, c in enumerate(line):
                grid[(x, y)] = 1 if c == "#" else 0
            y += 1
    return grid


def update_grid(grid):
    new_grid = dict()
    for pos in grid:
        n_bugs = 0
        for tile in get_surrounding_points(pos):
            if tile in grid and grid[tile] == 1:
                n_bugs += 1
        if grid[pos] == 1 and n_bugs != 1:
            # Bug died
            new_grid[pos] = 0
        elif grid[pos] == 0 and (n_bugs == 1 or n_bugs == 2):
            # Infested
            new_grid[pos] = 1
        else:
            new_grid[pos] = grid[pos]
    return new_grid


def get_biodiversity_rating(grid):
    rating = 0
    for i in range(25):
        x = i % 5
        y = int(i / 5)
        if grid[(x, y)] == 1:
            rating += (2 ** i)
    return rating


def print_grid(grid):
    for y in range(5):
        for x in range(5):
            if grid[(x, y)] == 1:
                sys.stdout.write("#")
            else:
                sys.stdout.write(".")
        sys.stdout.write("\n")
    sys.stdout.flush()
    input()


def compute_biodiversity_rating():
    grid = read_input()
    biodiversity_ratings = set()
    while True:
        rating = get_biodiversity_rating(grid)
        if rating in biodiversity_ratings:
            repeated_rating = rating
            break
        biodiversity_ratings.add(rating)
        grid = update_grid(grid)
    return repeated_rating


def get_bugs_count():
    grid = read_input()
    folding_grid = FoldingGrid()
    folding_grid.initialize(grid)
    for i in range(200):
        folding_grid.update()
    return folding_grid.get_bugs()


# Start the main class
if __name__ == "__main__":
    rating = compute_biodiversity_rating()
    print("Biodiversity rating is", rating)
    bugs = get_bugs_count()
    print("After 200 minutes we have", bugs, "bugs")

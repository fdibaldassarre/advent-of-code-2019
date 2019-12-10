#!/usr/bin/env python3

import math
import numpy as np


def read_input():
    asteroids_map = []
    with open("input")as hand:
        for line in hand:
            line_map = list(map(lambda n: 1 if n == "#" else 0, line.strip()))
            asteroids_map.append(line_map)
    return np.asarray(asteroids_map, dtype=np.int)


def get_line_of_sight(point1, point2):
    x, y = point1
    a, b = point2
    diff_a = a - x
    diff_b = b - y
    G = math.gcd(diff_a, diff_b)
    if G > 0:
        da = int(diff_a / G)
        db = int(diff_b / G)
    else:
        da = np.sign(diff_a)
        db = np.sign(diff_b)
        G = max(da, db)
    line_of_sight = []
    for k in range(1, G + 1):
        la = x + k * da
        lb = y + k * db
        line_of_sight.append((la, lb))
    return line_of_sight


def is_duplicate(point, seen):
    a, b = point
    duplicated = False
    for el in seen:
        x, y = el
        if a == x and b == y:
            duplicated = True
            break
    return duplicated

def count_asteroids(point, ast_map):
    h, w = ast_map.shape
    seen = []
    for b in range(h):
        for a in range(w):
            line_of_sight = get_line_of_sight(point, (b, a))
            # Find asteroids in sight
            for el in line_of_sight:
                sy, sx = el
                if ast_map[sy, sx] == 1:
                    if not is_duplicate(el, seen):
                        seen.append(el)
                    break
    return len(seen)


def reduce_standard(point):
    x, y = point
    G = math.gcd(x, y)
    return int(x/G), int(y/G)


def get_possible_inclinations(center, corner):
    y, x = center
    b, a = corner
    delta_x = a - x
    delta_y = b - y
    inclinations = [] #[(1, 0)]
    for i in range(1, abs(delta_x) + 1):
        for j in range(1, abs(delta_y) + 1):
            point = reduce_standard((np.sign(delta_y) * j, np.sign(delta_x) * i))
            if not is_duplicate(point, inclinations):
                inclinations.append(point)
    inclinations = sorted(inclinations, key=lambda point: -1 * point[1] / point[0])
    result = [] #[(0, 1)]
    result.extend(inclinations)
    return result


def get_points_at_inclination(center, inclination, shape):
    dy, dx = inclination
    y, x = center
    max_y, max_x = shape
    keep = True
    points = []
    k = 1
    while keep:
        px = x + k * dx
        py = y + k * dy
        if 0 <= px < max_x and 0 <= py < max_y:
            point = (py, px)
            points.append(point)
            k += 1
        else:
            keep = False
    return points

def compute1():
    ast_map = read_input()
    h, w = ast_map.shape
    max_asteroids = 0
    best_point = None
    for y in range(h):
        for x in range(w):
            if ast_map[y, x] == 1:
                n = count_asteroids((y, x), ast_map)
                if n > max_asteroids:
                    max_asteroids = n
                    best_point = (y, x)
    print("Max number of visible asteroids:", max_asteroids)
    return best_point



def get_all_possible_inclinations(center, shape):
    max_y, max_x = shape
    max_x -= 1
    max_y -= 1
    inclinations = [(-1, 0)]
    inclinations.extend(get_possible_inclinations(center, (0, max_x)))
    inclinations.append((0, 1))
    inclinations.extend(get_possible_inclinations(center, (max_y, max_x)))
    inclinations.append((1, 0))
    inclinations.extend(get_possible_inclinations(center, (max_y, 0)))
    inclinations.append((0, -1))
    inclinations.extend(get_possible_inclinations(center, (0, 0)))
    return inclinations


CORNERS = [(0, 9), (9, 9), (9, 0), (0, 0)]
def test():
    ast_map = read_input()
    line_map = np.zeros(shape=ast_map.shape)
    center = (3, 4)
    for n_corner, corner in enumerate(CORNERS):
        inclinations = get_possible_inclinations(center, corner)
        for n_inclination, inclination in enumerate(inclinations):
            line = get_points_at_inclination(center, inclination, ast_map.shape)
            for el in line:
                line_map[el] = (n_corner + 1) * 100 + n_inclination
    line_map[center] = 10


def test2():
    ast_map = read_input()
    line_map = np.zeros(shape=ast_map.shape)
    center = (3, 4)
    inclinations = get_all_possible_inclinations(center, ast_map.shape)
    for n_inclination, inclination in enumerate(inclinations):
        line = get_points_at_inclination(center, inclination, ast_map.shape)
        for el in line:
            line_map[el] = n_inclination + 1
    line_map[center] = -1
    print(line_map)


def compute2(center):
    ast_map = read_input()
    center = (29, 23)
    inclinations = get_all_possible_inclinations(center, ast_map.shape)
    destroyed_asteroids = 0
    keep = True
    while keep:
        for inclination in inclinations:
            line = get_points_at_inclination(center, inclination, ast_map.shape)
            for el in line:
                # Destroy the first asteroid in line
                if ast_map[el] == 1:
                    ast_map[el] = -1 * ((destroyed_asteroids % 9) + 1 + (math.floor(destroyed_asteroids/9) * 10))
                    destroyed_asteroids += 1
                    if destroyed_asteroids == 200:
                        print("200th destroyed asteroid:", el)
                        keep = False
                        pass
                    break

center = compute1()
compute2(center)
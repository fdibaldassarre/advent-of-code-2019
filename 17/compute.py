#!/usr/bin/env python3

from functools import reduce
import sys

from src.interpreter import OptcodeInterpreter

POINT_EMPTY = 46
POINT_SCAFFOLD = 35

NORTH = (0, -1)
SOUTH = (0, 1)
EAST = (1, 0)
WEST = (-1, 0)

MAX_ROUTINE_SIZE = 20


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
    return [north, south, east, west]


class Space:

    def __init__(self):
        self.space = {}
        self.scaffolds = []
        self.droid_start = None

    def draw(self, position, element):
        self.space[position] = element
        if element == POINT_SCAFFOLD:
            self.scaffolds.append(position)
        elif chr(element) == "^":
            self.droid_start = position

    def get_scaffolds(self):
        return self.scaffolds

    def is_scaffold(self, point):
        return point in self.space and self.space[point] == POINT_SCAFFOLD

    def get_droid_start(self):
        return self.droid_start

    def print(self):
        y = 0
        while True:
            if (0, y) not in self.space:
                break
            x = 0
            while True:
                pos = (x, y)
                if pos not in self.space:
                    sys.stdout.write("\n")
                    break
                sys.stdout.write(chr(self.space[pos]))
                x += 1
            y += 1
        sys.stdout.flush()


class Camera:

    def __init__(self, space):
        self.x = 0
        self.y = 0
        self.space = space

    def view(self, element):
        if element == 10:
            self.x = 0
            self.y += 1
        else:
            self.space.draw((self.x, self.y), element)
            self.x += 1


class Droid:

    def __init__(self, position, direction=NORTH):
        self.position = position
        self.direction = direction

    def get_direction(self):
        return self.direction

    def get_position(self):
        return self.position

    def _get_right(self):
        dx, dy = self.direction
        return -1 * dy, dx

    def _get_left(self):
        dx, dy = self.direction
        return dy, -1 * dx

    def peek_right(self):
        dx, dy = self._get_right()
        x, y = self.position
        return x + dx, y + dy

    def peek_left(self):
        dx, dy = self._get_left()
        x, y = self.position
        return x + dx, y + dy

    def peek_front(self):
        dx, dy = self.direction
        x, y = self.position
        return x + dx, y + dy

    def turn_right(self):
        self.direction = self._get_right()

    def turn_left(self):
        self.direction = self._get_left()

    def move(self, steps=1):
        x, y = self.position
        dx, dy = self.direction
        self.position = (x + dx * steps, y + dy * steps)


def read_input():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    return optcode


def get_space_configuration():
    space = Space()
    camera = Camera(space)
    optcode = read_input()
    interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
    interpreter.run()
    while not interpreter.output.empty():
        element = interpreter.output.get()
        camera.view(element)
    return space


def compute_intersections():
    space = get_space_configuration()
    intersections = list()
    for scaffold in space.get_scaffolds():
        surrounding = get_surrounding_points(scaffold)
        all_scaffolds = reduce(lambda x, y: x and y, map(lambda point: space.is_scaffold(point), surrounding))
        if all_scaffolds:
            intersections.append(scaffold)
    total = 0
    for el in intersections:
        x, y = el
        total = total + x * y
    return total


def get_all_moves(space):
    droid = Droid(space.get_droid_start())
    moves = []
    while True:
        # Find a point left or right to turn
        turned = False
        left = droid.peek_left()
        if space.is_scaffold(left):
            droid.turn_left()
            moves.append('L')
            turned = True
        right = droid.peek_right()
        if space.is_scaffold(right):
            droid.turn_right()
            moves.append('R')
            turned = True
        if not turned:
            break
        # Find steps to move
        steps = 0
        while space.is_scaffold(droid.peek_front()):
            steps += 1
            droid.move()
        moves.append(steps)
    return moves


def sequence_at(sequence, steps, k, filled=None):
    contained = True
    if filled is None:
        filled = [0] * len(steps)
    for i, n in enumerate(sequence):
        j = k + i
        if j >= len(steps) or steps[j] != n or filled[j] != 0:
            contained = False
            break
    return contained


def get_first_gap(moves, filled):
    gap = []
    gap_started = False
    for i, is_filled in enumerate(filled):
        if gap_started:
            if is_filled:
                break
            else:
                gap.append(moves[i])
        elif not is_filled:
            gap_started = True
            gap.append(moves[i])
    return gap


def fill_with(sequence, seq_number, moves, filled=None):
    if filled is None:
        filled = [0] * len(moves)
    else:
        filled = [status for status in filled]
    k = 0
    while k < len(moves):
        if sequence_at(sequence, moves, k, filled):
            for i in range(len(sequence)):
                if i == 0:
                    filled[k + i] = seq_number
                else:
                    filled[k + i] = 1
            k = k + len(sequence)
        else:
            k = k + 1
    return filled


def split_moves(moves):
    final_sequence = None
    for size_a in range(MAX_ROUTINE_SIZE + 1, 1, -1):
        a = moves[:size_a]
        filled_a = fill_with(a, 10, moves)
        gap_a = get_first_gap(moves, filled_a)
        max_b = min(len(gap_a), MAX_ROUTINE_SIZE)
        for size_b in range(max_b + 1, 1, -1):
            b = gap_a[:size_b]
            filled_b = fill_with(b, 20, moves, filled_a)
            gap_b = get_first_gap(moves, filled_b)
            max_c = min(len(gap_b), MAX_ROUTINE_SIZE)
            for size_c in range(max_c + 1, 1, -1):
                c = gap_b[:size_c]
                filled_c = fill_with(c, 30, moves, filled_b)
                if min(filled_c) == 1:
                    # Get pattern used to fill
                    pattern = []
                    for el in filled_c:
                        if el == 10:
                            pattern.append('A')
                        elif el == 20:
                            pattern.append('B')
                        elif el == 30:
                            pattern.append('C')
                    final_sequence = [a, b, c], pattern
                    break
    return final_sequence


def convert_sequence(sequence):
    return ','.join(map(lambda el: str(el), sequence)) + "\n"


def alert_all_droids():
    space = get_space_configuration()
    moves = get_all_moves(space)
    moves, sequence = split_moves(moves)
    a, b, c = moves
    # Run
    optcode = read_input()
    optcode[0] = 2
    interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
    # Input sequence
    sequence_str = convert_sequence(sequence)
    for el in sequence_str:
        interpreter.input.put(ord(el))
    # Configure routines
    for el in convert_sequence(a):
        interpreter.input.put(ord(el))
    for el in convert_sequence(b):
        interpreter.input.put(ord(el))
    for el in convert_sequence(c):
        interpreter.input.put(ord(el))
    interpreter.input.put(ord('n'))
    interpreter.input.put(ord('\n'))
    interpreter.run()
    last_val = None
    while not interpreter.output.empty():
        last_val = interpreter.output.get()
    return last_val


if __name__ == "__main__":
    intersections = compute_intersections()
    print("Intersections", intersections)
    collected_dust = alert_all_droids()
    print("Dust collected", collected_dust)

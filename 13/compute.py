#!/usr/bin/env python3

import os
import sys

import numpy as np
from time import sleep

from src.interpreter import OptcodeInterpreter
from src.utils import get_input

TILE_EMPTY = 0
TILE_WALL = 1
TILE_BLOCK = 2
TILE_PADDLE = 3
TILE_BALL = 4

RENDER_MAP = {
    TILE_EMPTY: ' ',
    TILE_WALL: '🎄',
    TILE_BLOCK: '❄️',
    TILE_PADDLE: '🛷',
    TILE_BALL: '🌟',
}

MOVE_LEFT = -1
MOVE_RIGHT = 1
WAIT = 0


def get_image_shape(table):
    min_x = min(list(map(lambda el: el[1], table)))
    min_y = min(list(map(lambda el: el[0], table)))
    max_x = max(list(map(lambda el: el[1], table)))
    max_y = max(list(map(lambda el: el[0], table)))
    delta = (-1 * min_y, -1 * min_x)
    dy = max_y - min_y + 1
    dx = max_x - min_x + 1
    return delta, (dy, dx)


class Player:

    def __init__(self, grid):
        self.grid = grid

    def act(self):
        ball_x, _ = self.get_element_position(TILE_BALL)
        paddle_x, _ = self.get_element_position(TILE_PADDLE)
        if paddle_x < ball_x:
            return MOVE_RIGHT
        elif ball_x < paddle_x:
            return MOVE_LEFT
        else:
            return WAIT

    def get_element_position(self, target):
        for pos in self.grid:
            if self.grid[pos] == target:
                return pos


class Grid:

    def __init__(self):
        self.grid = {}
        self.segment_display = 0

    def draw(self, position, tile):
        x, y = position
        if x == -1 and y == 0:
            self.segment_display = tile
        else:
            self.grid[position] = tile

    def get_screen(self):
        return self.grid

    def get_score(self):
        return self.segment_display

    def render(self):
        delta, size = get_image_shape(self.grid)
        image = np.zeros(shape=size, dtype=np.uint8)
        dy, dx = delta
        for y, x in self.grid:
            image[y + dy, x + dx] = self.grid[y, x]
        os.system("clear")  # Linux only
        print("Score:", self.segment_display)
        max_y, max_x = size
        for x in range(max_x):
            for y in range(max_y):
                sys.stdout.write(RENDER_MAP[self.grid[y, x]])
            sys.stdout.write("\n")
        sys.stdout.flush()


def compute():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))

    interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
    thread = interpreter.run_async()
    grid = Grid()
    while thread.is_alive():
        try:
            x = interpreter.output.get(timeout=2)
        except Exception:
            continue
        y = interpreter.output.get()
        tile = interpreter.output.get()
        grid.draw((x, y), tile)
    # Count blocks
    screen = grid.get_screen()
    count = 0
    for el in screen:
        if screen[el] == TILE_BLOCK:
            count += 1
    return count


def draw_input(interpreter, grid):
    while not interpreter.output.empty():
        try:
            x = interpreter.output.get(timeout=2)
        except Exception:
            pass
        y = interpreter.output.get()
        tile = interpreter.output.get()
        grid.draw((x, y), tile)


def compute_play(interactive=True):
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))

    interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
    interpreter.memory[0] = 2
    grid = Grid()
    player = Player(grid.get_screen())

    def on_input_requested():
        draw_input(interpreter, grid)
        if interactive:
            grid.render()
            int_input = get_input()
        else:
            int_input = player.act()
        interpreter.input.put(int_input)

    interpreter.set_input_request_listener(on_input_requested)
    thread = interpreter.run_async()
    while thread.is_alive():
        sleep(0.5)
    draw_input(interpreter, grid)
    if interactive:
        grid.render()
    return grid.get_score()


tiles = compute()
print("Tiles", tiles)
score = compute_play(interactive=True)
print("Final score:", score)

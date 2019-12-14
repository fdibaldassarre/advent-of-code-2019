#!/usr/bin/env python3

import os
import sys

import numpy as np

from src.interpreter import OptcodeInterpreter
from src.utils import get_input

TILE_EMPTY = 0
TILE_WALL = 1
TILE_BLOCK = 2
TILE_PADDLE = 3
TILE_BALL = 4

RENDER_MAP_EMOJI = {
    TILE_EMPTY: ' ',
    TILE_WALL: '🎄',
    TILE_BLOCK: '❄️',
    TILE_PADDLE: '🛷',
    TILE_BALL: '🌟',
}

RENDER_MAP = {
    TILE_EMPTY: ' ',
    TILE_WALL: 'X',
    TILE_BLOCK: '#',
    TILE_PADDLE: '=',
    TILE_BALL: 'o',
}


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

    def __init__(self, arcade_screen):
        self.arcade_screen = arcade_screen

    def act(self):
        ball_x, _ = self.arcade_screen.get_ball_position()
        paddle_x, _ = self.arcade_screen.get_paddle_position()
        return np.sign(ball_x - paddle_x)


class ArcadeScreen:

    def __init__(self):
        self.screen = {}
        self.segment_display = 0
        self._shape = None
        self._position_ball = None
        self._position_paddle = None

    def draw(self, position, tile):
        x, y = position
        if x == -1 and y == 0:
            self.segment_display = tile
        else:
            self.screen[position] = tile
            if tile == TILE_PADDLE:
                self._position_paddle = position
            elif tile == TILE_BALL:
                self._position_ball = position

    def get_ball_position(self):
        return self._position_ball

    def get_paddle_position(self):
        return self._position_paddle

    def get_screen(self):
        return self.screen

    def get_score(self):
        return self.segment_display

    def _get_shape(self):
        if self._shape is None:
            _, self._shape = get_image_shape(self.screen)
        return self._shape

    def render(self):
        os.system("clear")  # Linux only
        print("\tScore:", self.segment_display)
        max_y, max_x = self._get_shape()
        for x in range(max_x):
            for y in range(max_y):
                sys.stdout.write(RENDER_MAP[self.screen[y, x]])
            sys.stdout.write("\n")
        sys.stdout.flush()


def read_input():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    return optcode


def draw_instructions(interpreter, arcade_screen):
    try:
        x = interpreter.output.get(timeout=1)
    except Exception:
        pass
    y = interpreter.output.get()
    tile = interpreter.output.get()
    arcade_screen.draw((x, y), tile)


def compute():
    optcode = read_input()
    interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
    thread = interpreter.run_async()
    arcade_screen = ArcadeScreen()
    while thread.is_alive():
        draw_instructions(interpreter, arcade_screen)
    while not interpreter.output.empty():
        draw_instructions(interpreter, arcade_screen)
    screen = arcade_screen.get_screen()
    return len(list(filter(lambda pos: screen[pos] == TILE_BLOCK, screen)))


def compute_play(interactive=True):
    if interactive:
        print("Press A to move left, D to move right")
        print("Press ENTER to start")
        input()
    optcode = read_input()
    interpreter = OptcodeInterpreter(optcode, quiet_mode=True)
    interpreter.memory[0] = 2
    arcade_screen = ArcadeScreen()
    player = Player(arcade_screen)

    def on_input_requested():
        while not interpreter.output.empty():
            draw_instructions(interpreter, arcade_screen)
        if interactive:
            arcade_screen.render()
            int_input = get_input()
        else:
            int_input = player.act()
        interpreter.input.put(int_input)

    interpreter.set_input_request_listener(on_input_requested)
    interpreter.run()
    while not interpreter.output.empty():
        draw_instructions(interpreter, arcade_screen)
    if interactive:
        arcade_screen.render()
    return arcade_screen.get_score()


tiles = compute()
print("Block tiles:", tiles)
score = compute_play(interactive=False)
print("Final score:", score)

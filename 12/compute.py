#!/usr/bin/env python3

import re
import numpy as np

POSITION_RE = re.compile('<x=([-0-9]*), y=([-0-9]*), z=([-0-9]*)>')


class Moon:

    def __init__(self, position):
        self.position = np.asarray(position, dtype=np.int)
        self.velocity = np.asarray([0, 0, 0], dtype=np.int)

    def get_position(self):
        return self.position

    def get_velocity(self):
        return self.velocity

    def update_velocity(self, delta):
        self.velocity += delta

    def apply_velocity(self):
        self.position += self.velocity

    def get_energy(self):
        return np.sum(np.abs(self.position)) * np.sum(np.abs(self.velocity))

    def __str__(self):
        return "pos=<x=%d, y=%d, z=%d>, vel=<x=%d, y=%d, z=%d>" % (self.position[0], self.position[1], self.position[2], self.velocity[0], self.velocity[1], self.velocity[2])


def read_data():
    moons = []
    with open("input", "r") as hand:
        for line in hand:
            positions = POSITION_RE.match(line.strip()).groups()
            moons.append(Moon(list(positions)))
    return moons


def apply_gravity(moons):
    for current_moon in moons:
        for moon in moons:
            if moon == current_moon:
                continue
            diff = np.sign(moon.get_position() - current_moon.get_position())
            current_moon.update_velocity(diff)


def apply_velocity(moons):
    for moon in moons:
        moon.apply_velocity()


def get_total_energy(moons):
    energy = 0
    for moon in moons:
        energy += moon.get_energy()
    return energy


def get_current_state(moons, axis):
    data = []
    for moon in moons:
        pos = moon.get_position()[axis]
        vel = moon.get_velocity()[axis]
        data.extend([pos, vel])
    return np.asarray(data, dtype=np.int)


def compute():
    moons = read_data()
    for step in range(1000):
        apply_gravity(moons)
        apply_velocity(moons)
    return get_total_energy(moons)


def compute_repeat():
    moons = read_data()
    starting_states = [get_current_state(moons, axis) for axis in range(3)]
    steps = [None, None, None]
    step = 0
    while None in steps:
        step += 1
        apply_gravity(moons)
        apply_velocity(moons)
        for axis in range(3):
            if steps[axis] is None:
                current_state = get_current_state(moons, axis)
                diff = np.sum(np.abs(current_state - starting_states[axis]))
                if diff == 0:
                    steps[axis] = step
    return np.lcm.reduce(np.asarray(steps, dtype=np.int))


total_energy = compute()
print("Total energy:", total_energy)
min_steps = compute_repeat()
print("Minimum steps: ", min_steps)

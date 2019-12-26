#!/usr/bin/env python3

import sys

from src.interpreter import OptcodeInterpreter


def read_input():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    return optcode


def get_hull_damage(extended_mode=False):
    optcode = read_input()
    interpreter = OptcodeInterpreter(optcode, ascii_mode=True, quiet_mode=True)

    if not extended_mode:
        springscript = [
            "NOT A J",
            "NOT B T",
            "AND D T",
            "OR T J",
            "NOT C T",
            "AND D T",
            "OR T J",
            "WALK"
        ]
    else:
        springscript = [
            "NOT H T",
            "OR E T",
            "AND F T",
            "NOT E J",
            "AND J T",
            "OR C T",
            "NOT T J",
            "NOT C J",
            "AND C J",
            "OR B J",
            "OR E J",
            "AND T J",
            "AND A J",
            "NOT J J",
            "AND D J",
            "RUN"
        ]
    ascii_instructions = "\n".join(springscript) + "\n"
    for el in ascii_instructions:
        interpreter.input.put(el)

    interpreter.run()
    return interpreter.output.get()


if __name__ == '__main__':
    hull_damage = get_hull_damage()
    print("Hull damage", hull_damage)
    hull_damage_ext = get_hull_damage(extended_mode=True)
    print("Hull damage in extended mode", hull_damage_ext)
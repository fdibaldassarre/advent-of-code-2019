#!/usr/bin/env python3

import sys

with open("input", "r") as hand:
    optcode_raw = hand.read()

def run_optcode(noun, verb):
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))

    optcode[1] = noun
    optcode[2] = verb

    keep = True
    cursor = 0
    while keep:
        operation = optcode[cursor]
        if operation == 99:
            keep = False
        elif operation == 1 or operation == 2:
            first_el = optcode[optcode[cursor + 1]]
            second_el = optcode[optcode[cursor + 2]]
            new_position = optcode[cursor + 3]
            if operation == 1:
                # sum
                optcode[new_position] = first_el + second_el
            else:
                # multiply
                optcode[new_position] = first_el * second_el
        else:
            print("Unknown operation %d" % operation)
            sys.exit(1)
        # Move the cursor
        cursor += 4
    return optcode[0]


for noun in range(146):
    for verb in range(146):
        try:
            result = run_optcode(noun, verb)
            if result == 19690720:
                print(noun, verb)
        except Exception:
            continue

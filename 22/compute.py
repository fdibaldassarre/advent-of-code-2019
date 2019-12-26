#!/usr/bin/env python3

import numpy as np


OP_CUT = 0  # "cut"
OP_DEAL_INCREMENT = 1  # "deal with increment"
OP_DEAL_STACK = 2  # "deal into new stack"

TOT_CARDS = 10007
TOT_CARDS2 = 119315717514047

SHUFFLE_REPEAT = 101741582076661


def read_input():
    operations = []
    with open("input") as hand:
        for line in hand:
            line = line.strip()
            if line.startswith("cut"):
                n = int(line[len("cut") + 1:])
                operations.append({"op": OP_CUT, "n": n})
            elif line.startswith("deal with increment"):
                n = int(line[len("deal with increment") + 1:])
                operations.append({"op": OP_DEAL_INCREMENT, "n": n})
            else:
                operations.append({"op": OP_DEAL_STACK, "n": 0})
    return operations


def apply_operation(operation, card):
    name = operation["op"]
    n = operation["n"]
    if name == OP_DEAL_STACK:
        result = (-1 * (card+1)) % TOT_CARDS
    elif name == OP_DEAL_INCREMENT:
        result = (n * card) % TOT_CARDS
    else:
        result = (card - n) % TOT_CARDS
    return result


def apply_operation2d(operation, card, tot_cards):
    name = operation["op"]
    n = operation["n"]
    if name == OP_DEAL_STACK:
        result = -1 * (card + np.asarray([0, 1], dtype=int))
    elif name == OP_DEAL_INCREMENT:
        result = n * card
    else:
        result = card - np.asarray([0, n], dtype=int)
    result = result % tot_cards
    return result


def get_position_after_shuffling_once():
    operations = read_input()
    shuffled_card = 2019
    for operation in operations:
        shuffled_card = apply_operation(operation, shuffled_card)
    return shuffled_card


def get_position_after_shuffling():
    operations = read_input()
    shuffled_card = np.asarray([1, 0])
    tot_cards = TOT_CARDS2
    sr = SHUFFLE_REPEAT

    for operation in operations:
        shuffled_card = apply_operation2d(operation, shuffled_card, tot_cards)
    m1, q1 = shuffled_card

    m1 = int(m1)
    q1 = int(q1)

    f = lambda n: (n * m1 + q1) % tot_cards

    origin = 2020

    n_rep = ((-1 * sr) % tot_cards) - 1

    n_f = int(np.log2(n_rep))
    fs = list()
    fs.append(f)
    mt = [m1]
    qt = [q1]
    for i in range(n_f):
        new_q = (mt[i] * qt[i] + qt[i]) % tot_cards
        new_m = (mt[i] * mt[i]) % tot_cards
        mt.append(new_m)
        qt.append(new_q)

    fs = lambda i, n: (n * mt[i] + qt[i]) % tot_cards

    result = origin
    while n_rep > 0:
        rep_l = int(np.log2(n_rep))
        result = fs(rep_l, result)
        n_rep = n_rep - 2 ** rep_l
    return result


if __name__ == "__main__":
    pos2019 = get_position_after_shuffling_once()
    pos2020 = get_position_after_shuffling()
    print("Position of card 2019", pos2019)
    print("Card in position 2020", pos2020)
#!/usr/bin/env python3

import numpy as np

PATTERN = [0, 1, 0, -1]


def fft(data):
    K = len(data)
    start = 0
    result = []
    for k in range(start + 1, K + 1):
        digit = 0
        for n, val in enumerate(data):
            val = int(val)
            pat = int((n+1) / k) % 4
            digit += val * PATTERN[pat]
        result.append(abs(digit) % 10)
    return result


def compute_sum_list(data):
    sum_list = [0] * (len(data) + 1)
    for i in range(len(data)):
        sum_list[i + 1] = sum_list[i] + int(data[i])
    return sum_list


def apply_pattern(start, k, data, sum_list, max_size):
    x_0 = start + k - 1
    x_1 = x_0 + k
    x_2 = x_1 + k
    x_3 = x_2 + k

    p_0 = min(x_0, max_size) % len(data)
    p_1 = min(x_1, max_size) % len(data)
    p_2 = min(x_2, max_size) % len(data)
    p_3 = min(x_3, max_size) % len(data)

    multiplier = 0
    if k > len(data):
        multiplier = int(k / len(data))

    pos = multiplier * sum_list[-1]
    if p_0 <= p_1:
        pos += sum_list[p_1] - sum_list[p_0]
    else:
        pos += sum_list[-1] - sum_list[p_0] + sum_list[p_1]

    neg = multiplier * sum_list[-1]
    if p_2 <= p_3:
        neg += sum_list[p_3] - sum_list[p_2]
    else:
        neg += sum_list[-1] - sum_list[p_2] + sum_list[p_3]
    return int(pos - neg)


def apply_phase(data, sum_list, repeat=1, offset=1):
    tot_size = len(data) * repeat
    decoded = [0] * tot_size
    for k in range(offset, tot_size + 1):
        repetitions = np.ceil(tot_size / (4*k))
        res = 0
        for t in range(int(repetitions)):
            start = t * k * 4
            delta = apply_pattern(start, k, data, sum_list, tot_size)
            res = res + delta
        decoded[k-1] = abs(res) % 10
    return decoded


def read_input():
    with open("input") as hand:
        data = hand.read().strip()
    return data


def compute1():
    data = read_input()
    for _ in range(100):
        sum_list = compute_sum_list(data)
        data = apply_phase(data, sum_list)
    return data[:8]


def compute2():
    data = read_input()
    offset = int(data[:7])
    sum_list = compute_sum_list(data)
    data = apply_phase(data, sum_list, repeat=10000, offset=offset)
    for i in range(99):
        sum_list = compute_sum_list(data)
        data = apply_phase(data, sum_list, offset=offset)
    return data[offset:offset + 8]


fft_1 = compute1()
print(fft_1)

fft_10000 = compute2()
print(fft_10000)

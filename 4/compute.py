#!/usr/bin/env python3

min_raw = "171309"
max_raw = "643603"


def get_next_candidate(n):
    # Return the min integer with all non-descending digits
    # greater or equal than n
    values = list(map(lambda d: int(d), list(str(n))))
    for index in range(1, 6):
        if values[index] < values[index - 1]:
            for cursor in range(index, 6):
                values[cursor] = values[index - 1]
    result = 0
    for d in range(6):
        result = result + values[5 - d] * (10 ** d)
    return result

def check_double_digit_rule(n):
    values = list(map(lambda d: int(d), list(str(n))))
    good = False
    for index in range(1, 6):
        if values[index] == values[index - 1]:
            if (index == 1 or values[index - 2] != values[index]) and \
                    (index == 5 or values[index + 1] != values[index]):
                good = True
                break
    return good


print(check_double_digit_rule(111234))
print(check_double_digit_rule(112233))
print(check_double_digit_rule(123444))
print(check_double_digit_rule(111122))
print(check_double_digit_rule(123334))

min_value = int(min_raw)
max_value = int(max_raw)

valid = 0
current = min_value
keep = True
while keep:
    # Take the next possible candidate
    candidate = get_next_candidate(current)
    if current == candidate:
        candidate = get_next_candidate(current + 1)
    current = candidate
    if current > max_value:
        keep = False
        break
    print(current, valid)
    # Check if the double digits rule is true
    if check_double_digit_rule(current):
        valid += 1

print(valid)


#!/usr/bin/env python3

import sys


MODE_POSITION = 0
MODE_PARAMETER = 1

class OptcodeParameter:

    def __init__(self, value, mode):
        self.value = value
        self.mode = mode

    def get_actual_value(self, memory):
        if self.mode == MODE_POSITION:
            return memory[self.value]
        elif self.mode == MODE_PARAMETER:
            return self.value
        else:
            raise Exception("Invalid mode %s" % self.mode)


class OptcodeOperation:

    n_parameters = 0

    def __init__(self):
        self.parameters = None

    """
        Execute the operation and return the number of 
        values in the instruction
        
        :return steps to move and if to keep the execution
    """
    def execute(self, optcode):
        self.execute_internal(optcode)
        return 1 + len(self.parameters), True

    def execute_internal(self, optcode):
        raise NotImplementedError


class SumOperation(OptcodeOperation):
    n_parameters = 3

    def execute_internal(self, optcode):
        first_el = self.parameters[0].get_actual_value(optcode.memory)
        second_el = self.parameters[1].get_actual_value(optcode.memory)
        write_position = self.parameters[2].value
        optcode.memory[write_position] = first_el + second_el


class MultiplyOperation(OptcodeOperation):
    n_parameters = 3

    def execute_internal(self, optcode):
        first_el = self.parameters[0].get_actual_value(optcode.memory)
        second_el = self.parameters[1].get_actual_value(optcode.memory)
        write_position = self.parameters[2].value
        optcode.memory[write_position] = first_el * second_el


class InputOperation(OptcodeOperation):
    n_parameters = 1

    def execute_internal(self, optcode):
        write_position = self.parameters[0].value
        input_value = optcode.get_input()
        if input_value is None:
            return False
        optcode.memory[write_position] = input_value
        return True

    def execute(self, optcode):
        success = self.execute_internal(optcode)
        if success:
            return 2, True
        else:
            return None, False  # Pause execution


class OutputOperation(OptcodeOperation):
    n_parameters = 1

    def execute_internal(self, optcode):
        value = self.parameters[0].get_actual_value(optcode.memory)
        optcode.set_output(value)
        print(value)


class JumpIfTrue(OptcodeOperation):
    n_parameters = 2

    def execute(self, optcode):
        value = self.parameters[0].get_actual_value(optcode.memory)
        if value != 0:
            optcode.cursor = self.parameters[1].get_actual_value(optcode.memory)
            return None, True
        else:
            return 1 + len(self.parameters), True


class JumpIfFalse(OptcodeOperation):
    n_parameters = 2

    def execute(self, optcode):
        value = self.parameters[0].get_actual_value(optcode.memory)
        if value == 0:
            optcode.cursor = self.parameters[1].get_actual_value(optcode.memory)
            return None, True
        else:
            return 1 + len(self.parameters), True


class LessThan(OptcodeOperation):
    n_parameters = 3

    def execute_internal(self, optcode):
        first_val = self.parameters[0].get_actual_value(optcode.memory)
        second_val = self.parameters[1].get_actual_value(optcode.memory)
        write_position = self.parameters[2].value
        if first_val < second_val:
            optcode.memory[write_position] = 1
        else:
            optcode.memory[write_position] = 0


class EqualCheck(OptcodeOperation):
    n_parameters = 3

    def execute_internal(self, optcode):
        first_val = self.parameters[0].get_actual_value(optcode.memory)
        second_val = self.parameters[1].get_actual_value(optcode.memory)
        write_position = self.parameters[2].value

        if first_val == second_val:
            optcode.memory[write_position] = 1
        else:
            optcode.memory[write_position] = 0


def split_code(code):
    data = ("0000" + str(code))[-5:]
    op_code = int(data[-2:])
    modes_raw = data[:3]
    modes = list(map(lambda c: int(c), modes_raw))[::-1]
    return op_code, modes


class Optcode:

    def __init__(self, optcode):
        self.memory = optcode
        self.input = []
        self.output = []
        self.cursor = 0

    def get_input(self):
        if len(self.input) == 0:
            return None
        self.input.reverse()
        current_input = self.input.pop()
        self.input.reverse()
        return current_input

    def set_output(self, n):
        self.output.append(n)

    def get_parameters(self, number, modes):
        parameters = []
        for i in range(number):
            mode = modes[i] if len(modes) > i else MODE_POSITION
            value = self.memory[self.cursor + 1 + i]
            parameters.append(OptcodeParameter(value, mode))
        return parameters

    def get_operation(self):
        code = self.memory[self.cursor]
        op_code, modes = split_code(code)
        if op_code == 99:
            return None
        elif op_code == 1:
            operation = SumOperation()
        elif op_code == 2:
            operation = MultiplyOperation()
        elif op_code == 3:
            operation = InputOperation()
        elif op_code == 4:
            operation = OutputOperation()
        elif op_code == 5:
            operation = JumpIfTrue()
        elif op_code == 6:
            operation = JumpIfFalse()
        elif op_code == 7:
            operation = LessThan()
        elif op_code == 8:
            operation = EqualCheck()
        else:
            raise NotImplementedError
        operation.parameters = self.get_parameters(operation.n_parameters, modes)
        return operation

    def run(self, input):
        self.input = input
        self.output = []
        keep = True
        while keep:
            is_terminated, keep_execution = self._iter_once()
            keep = (not is_terminated) and keep_execution
        return is_terminated

    def _iter_once(self):
        operation = self.get_operation()
        is_terminated = False
        keep_execution = True
        if operation is None:
            is_terminated = True
        else:
            diff, keep_execution = operation.execute(self)
            if diff is not None:
                self.cursor += diff
        return is_terminated, keep_execution


class Amplifier(Optcode):

    def __init__(self, optcode, phase_setting):
        super().__init__(optcode)
        self.phase_setting = phase_setting
        self.phase_setting_feeded = False

    def get_input(self):
        if not self.phase_setting_feeded:
            self.phase_setting_feeded = True
            return self.phase_setting
        else:
            return super().get_input()


def run_amplifiers(optcode_raw, phase_settings):
    # Load amplifiers
    amplifiers = []
    for phase_setting in phase_settings:
        optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
        amplifier = Amplifier(optcode, phase_setting)
        amplifiers.append(amplifier)
    amp_input = [0, ]
    keep = True
    while keep:
        for amplifier in amplifiers:
            is_terminated = amplifier.run(amp_input)
            if is_terminated:
                # Stop the loop after calling the amplifiers
                keep = False
            amp_input = amplifier.output
    return amp_input


def convert_to_base(n, b, min_length=5):
    digits = []
    while n > 0:
        digits.append(int(n % b))
        n //= b
    while len(digits) < min_length:
        digits.append(0)
    return digits[::-1]


def phase_is_valid(phase_setting):
    has_duplicates = False
    n = len(phase_setting)
    for i in range(n):
        for j in range(n):
            if phase_setting[i] == phase_setting[j] and i != j:
                has_duplicates = True
                break
    return not has_duplicates

def test():
    # Run the program
    with open("test5", "r") as hand:
        optcode_raw = hand.read()
    amp_input = run_amplifiers(optcode_raw, [9,7,8,5,6])
    print("Test result", amp_input)

# Run the program
with open("input", "r") as hand:
    optcode_raw = hand.read()

max_output = None
max_phase = None
for n in range(5 ** 5):
    phase_settings = convert_to_base(n, 5)
    if not phase_is_valid(phase_settings):
        continue
    # Increase to move range to 5 - 9
    phase_settings = list(map(lambda i: i + 5, phase_settings))
    amp_input = run_amplifiers(optcode_raw, phase_settings)
    if max_output is None or amp_input > max_output:
        max_output = amp_input
        max_phase = phase_settings
        print("max", amp_input, phase_settings)

print("Max output", max_output)
print("Phase", max_phase)
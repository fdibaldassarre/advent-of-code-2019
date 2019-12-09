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
    """
    def execute(self, optcode):
        self.execute_internal(optcode)
        return 1 + len(self.parameters)

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
        optcode.memory[write_position] = optcode.input


class OutputOperation(OptcodeOperation):
    n_parameters = 1

    def execute_internal(self, optcode):
        value = self.parameters[0].get_actual_value(optcode.memory)
        optcode.output = value
        print(optcode.output)


class JumpIfTrue(OptcodeOperation):
    n_parameters = 2

    def execute(self, optcode):
        value = self.parameters[0].get_actual_value(optcode.memory)
        if value != 0:
            optcode.cursor = self.parameters[1].get_actual_value(optcode.memory)
            return None
        else:
            return 1 + len(self.parameters)


class JumpIfFalse(OptcodeOperation):
    n_parameters = 2

    def execute(self, optcode):
        value = self.parameters[0].get_actual_value(optcode.memory)
        if value == 0:
            optcode.cursor = self.parameters[1].get_actual_value(optcode.memory)
            return 0
        else:
            return 1 + len(self.parameters)


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
        self.input = None
        self.output = None
        self.cursor = 0

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
        keep = True
        while keep:
            operation = self.get_operation()
            if operation is None:
                keep = False
            else:
                diff = operation.execute(self)
                if diff is not None:
                    self.cursor += diff


with open("input", "r") as hand:
    optcode_raw = hand.read()

#optcode_raw = """3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99"""
optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
executor = Optcode(optcode)
executor.run(5)

def run_optcode(noun, verb):
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))

    optcode[1] = noun
    optcode[2] = verb

    executor = Optcode(optcode)
    executor.run(0)

    return executor.memory[0]
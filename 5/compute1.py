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

    def __init__(self, parameters):
        self.parameters = parameters

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

    def execute_internal(self, optcode):
        first_el = self.parameters[0].get_actual_value(optcode.memory)
        second_el = self.parameters[1].get_actual_value(optcode.memory)
        write_position = self.parameters[2].value
        optcode.memory[write_position] = first_el + second_el

class MultiplyOperation(OptcodeOperation):

    def execute_internal(self, optcode):
        first_el = self.parameters[0].get_actual_value(optcode.memory)
        second_el = self.parameters[1].get_actual_value(optcode.memory)
        write_position = self.parameters[2].value
        optcode.memory[write_position] = first_el * second_el

class InputOperation(OptcodeOperation):

    def execute_internal(self, optcode):
        write_position = self.parameters[0].value
        optcode.memory[write_position] = optcode.input

class OutputOperation(OptcodeOperation):

    def execute_internal(self, optcode):
        value = self.parameters[0].get_actual_value(optcode.memory)
        optcode.output = value
        print(optcode.output)


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
        if op_code == 1 or op_code == 2:
            n_parameters = 3
        elif op_code == 3 or op_code == 4:
            n_parameters = 1
        else:
            raise NotImplementedError
        parameters = self.get_parameters(n_parameters, modes)
        if op_code == 1:
            operation = SumOperation(parameters)
        elif op_code == 2:
            operation = MultiplyOperation(parameters)
        elif op_code == 3:
            operation = InputOperation(parameters)
        elif op_code == 4:
            operation = OutputOperation(parameters)
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
                self.cursor += diff


with open("input", "r") as hand:
    optcode_raw = hand.read()

optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
executor = Optcode(optcode)
executor.run(1)

def run_optcode(noun, verb):
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))

    optcode[1] = noun
    optcode[2] = verb

    executor = Optcode(optcode)
    executor.run(0)

    return executor.memory[0]
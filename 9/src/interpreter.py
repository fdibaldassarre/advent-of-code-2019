#!/usr/bin/env python3

from queue import Queue
import threading
from threading import Thread

from .operations import OptcodeParameter
from .operations import SumOperation
from .operations import MultiplyOperation
from .operations import InputOperation
from .operations import OutputOperation
from .operations import JumpIfFalse
from .operations import JumpIfTrue
from .operations import LessThan
from .operations import EqualCheck
from .operations import RelativeBaseAdjust


def split_code(code):
    data = ("0000" + str(code))[-5:]
    op_code = int(data[-2:])
    modes_raw = data[:3]
    modes = list(map(lambda c: int(c), modes_raw))[::-1]
    return op_code, modes


class OptcodeMemory:

    def __init__(self, optcode):
        self.memory = optcode

    def __getitem__(self, idx):
        if idx < len(self.memory):
            return self.memory[idx]
        else:
            return 0

    def __setitem__(self, idx, item):
        delta = idx - len(self.memory)
        if delta >= 0:
            self.memory.extend([0] * (delta + 1))
        #print("Memr: Set memory[%d] = %d" % (idx, item))
        self.memory[idx] = item


class OptcodeInterpreter:

    def __init__(self, optcode, input_queue=None, output_queue=None):
        self.memory = OptcodeMemory(optcode)
        self.input = input_queue if input_queue is not None else Queue()
        self.output = output_queue if output_queue is not None else Queue()
        self.cursor = 0
        self.relative_base = 0

    def get_input(self):
        n = self.input.get()
        # print("<-- %d [%s]" % (n, threading.currentThread().getName()))
        return n

    def set_output(self, n):
        #print("--> %d [%s] [%s]" % (n, threading.currentThread().getName(), str(self.output)))
        self.output.put(n)

    def get_parameters(self, number, modes):
        parameters = []
        for i in range(number):
            mode = modes[i] if len(modes) > i else None
            value = self.memory[self.cursor + 1 + i]
            parameters.append(OptcodeParameter(value, mode))
        return parameters

    def get_operation(self):
        code = self.memory[self.cursor]
        op_code, modes = split_code(code)
        #print("========================")
        #print("Cursor: %d, Base %d" % (self.cursor, self.relative_base))
        #print("[%d] Code: %d" % (code, op_code))
        #print(" Params %s" % str(modes))
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
        elif op_code == 9:
            operation = RelativeBaseAdjust()
        else:
            raise NotImplementedError("Operation %d" % op_code)
        operation.parameters = self.get_parameters(operation.n_parameters, modes)
        # print("Params: %s" % ",".join(list(map(lambda op: str(op), operation.parameters))))
        return operation

    def run(self):
        # Clean output?, maybe not
        keep = True
        while keep:
            operation = self.get_operation()
            if operation is None:
                keep = False
            else:
                diff = operation.execute(self)
                if diff is not None:
                    self.cursor += diff


class Amplifier:

    def __init__(self, name, optcode, phase_setting):
        self.name = name
        self.optcode = optcode
        self.phase_setting = phase_setting
        self.output = Queue()

    def get_output(self):
        return self.output

    def set_input(self, input):
        self.input = input
        self.input.put(self.phase_setting)

    def run(self, input_signal=None):
        if input_signal is not None:
            self.input.put(input_signal)
        interpreter = OptcodeInterpreter(self.optcode, self.input, self.output)
        thread = Thread(target=interpreter.run)
        thread.start()
        return thread

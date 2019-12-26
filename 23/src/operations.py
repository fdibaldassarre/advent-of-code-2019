#!/usr/bin/env python3

MODE_POSITION = 0
MODE_PARAMETER = 1
MORE_RELATIVE = 2


class OptcodeParameter:

    def __init__(self, value, mode=None):
        self.value = value
        self.mode = mode if mode is not None else MODE_POSITION

    def __str__(self):
        return "%d [%d]" % (self.value, self.mode)

    def get_actual_value(self, optcode):
        if self.mode == MODE_POSITION or self.mode == MORE_RELATIVE:
            delta = 0
            if self.mode == MORE_RELATIVE:
                delta = optcode.relative_base
            return optcode.memory[delta + self.value]
        elif self.mode == MODE_PARAMETER:
            return self.value
        else:
            raise Exception("Invalid mode %s" % self.mode)

    def get_write_value(self, optcode):
        if self.mode == MORE_RELATIVE:
            return optcode.relative_base + self.value
        else:
            return self.value


class OptcodeOperation:

    n_parameters = 0

    def __init__(self):
        self.parameters = None

    """
        Execute the operation and return the number of 
        values in the instruction

        :return steps to move
    """
    def execute(self, optcode):
        self.execute_internal(optcode)
        return 1 + len(self.parameters)

    def execute_internal(self, optcode):
        raise NotImplementedError


class SumOperation(OptcodeOperation):
    n_parameters = 3

    def execute_internal(self, optcode):
        first_el = self.parameters[0].get_actual_value(optcode)
        second_el = self.parameters[1].get_actual_value(optcode)
        write_position = self.parameters[2].get_write_value(optcode)
        # print("%d + %d at position %d" % (first_el, second_el, write_position))
        optcode.memory[write_position] = first_el + second_el


class MultiplyOperation(OptcodeOperation):
    n_parameters = 3

    def execute_internal(self, optcode):
        first_el = self.parameters[0].get_actual_value(optcode)
        second_el = self.parameters[1].get_actual_value(optcode)
        write_position = self.parameters[2].get_write_value(optcode)
        optcode.memory[write_position] = first_el * second_el


class InputOperation(OptcodeOperation):
    n_parameters = 1

    def execute_internal(self, optcode):
        write_position = self.parameters[0].get_write_value(optcode)
        if optcode.input_request_listener is not None:
            optcode.input_request_listener()
        val = optcode.get_input()
        optcode.memory[write_position] = val



class OutputOperation(OptcodeOperation):
    n_parameters = 1

    def execute_internal(self, optcode):
        value = self.parameters[0].get_actual_value(optcode)
        if not optcode.quiet_mode:
            print("--> %d" % value)
        if optcode.output_request_listener is not None:
            optcode.output_request_listener(value)
        else:
            optcode.set_output(value)


class JumpIfTrue(OptcodeOperation):
    n_parameters = 2

    def execute(self, optcode):
        value = self.parameters[0].get_actual_value(optcode)
        if value != 0:
            optcode.cursor = self.parameters[1].get_actual_value(optcode)
            return None
        else:
            return 1 + len(self.parameters)


class JumpIfFalse(OptcodeOperation):
    n_parameters = 2

    def execute(self, optcode):
        value = self.parameters[0].get_actual_value(optcode)
        if value == 0:
            optcode.cursor = self.parameters[1].get_actual_value(optcode)
            return None
        else:
            return 1 + len(self.parameters)


class LessThan(OptcodeOperation):
    n_parameters = 3

    def execute_internal(self, optcode):
        first_val = self.parameters[0].get_actual_value(optcode)
        second_val = self.parameters[1].get_actual_value(optcode)
        write_position = self.parameters[2].get_write_value(optcode)
        if first_val < second_val:
            optcode.memory[write_position] = 1
        else:
            optcode.memory[write_position] = 0


class EqualCheck(OptcodeOperation):
    n_parameters = 3

    def execute_internal(self, optcode):
        first_val = self.parameters[0].get_actual_value(optcode)
        second_val = self.parameters[1].get_actual_value(optcode)
        write_position = self.parameters[2].get_write_value(optcode)

        if first_val == second_val:
            optcode.memory[write_position] = 1
        else:
            optcode.memory[write_position] = 0


class RelativeBaseAdjust(OptcodeOperation):
    n_parameters = 1

    def execute_internal(self, optcode):
        val = self.parameters[0].get_actual_value(optcode)
        optcode.relative_base += val

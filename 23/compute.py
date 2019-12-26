#!/usr/bin/env python3

from src.interpreter import OptcodeInterpreter

from time import sleep


class OptcodeNetwork:

    def __init__(self, monitor_idle=False):
        self.monitor_idle = monitor_idle
        self.network = []
        self.nat_packet = [None, None]
        self._packets = []
        self._run = False

    def add_nic(self, optcode):
        address = len(self.network)
        instructions = [code for code in optcode]
        interpreter = OptcodeInterpreter(instructions, quiet_mode=True)

        def on_input_requested():
            if interpreter.input.empty():
                interpreter.input.put(-1)
                sleep(0.5)

        interpreter.set_input_request_listener(on_input_requested)

        def on_output_sent(value):
            packet = self._packets[address]
            if packet is None:
                self._packets[address] = [value, None, None]
            elif packet[1] is None:
                packet[1] = value
            else:
                packet[2] = value
                target, x, y = packet
                if target == 255:
                    if not self.monitor_idle:
                        self._run = False
                    self.nat_packet = [x, y]
                else:
                    self.network[target].input.put(x)
                    self.network[target].input.put(y)
                self._packets[address] = None

        interpreter.set_output_request_listener(on_output_sent)
        # Assign address
        interpreter.input.put(address)
        self.network.append(interpreter)
        self._packets.append(None)

    def start(self):
        self._run = True
        threads = []
        for nic in self.network:
            thread = nic.run_async()
            threads.append(thread)
        iteration = 0
        prev_y_send = None
        while self._run:
            all_idle = False
            if self.monitor_idle:
                # Check if network is idle
                all_idle = True
                if iteration < 10:
                    all_idle = False
                for i, nic in enumerate(self.network):
                    if nic.input.qsize() <= 1 and nic.output.empty():
                        is_idle = True
                    else:
                        is_idle = False
                    all_idle = all_idle and is_idle
                    if not all_idle:
                        break
            if all_idle:
                input_queue = self.network[0].input
                x, y = self.nat_packet
                input_queue.put(x)
                input_queue.put(y)
                if y == prev_y_send:
                    self._run = False
                prev_y_send = y
                iteration = 0
            iteration += 1
            sleep(0.5)
        # Stop all
        for nic in self.network:
            nic.input.put(-1)
            nic.stop()


def read_input():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    return optcode


def run_cat6(monitor_idle=False):
    optcode = read_input()
    nw = OptcodeNetwork(monitor_idle=monitor_idle)
    for _ in range(50):
        nw.add_nic(optcode)
    nw.start()
    return nw.nat_packet[1]


if __name__ == '__main__':
    y = run_cat6()
    print("First Y value send to NAT", y)
    y_twice = run_cat6(monitor_idle=True)
    print("First Y value send to NAT twice in a row", y_twice)

#!/usr/bin/env python3

from src.interpreter import OptcodeInterpreter


def compute():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    interpreter = OptcodeInterpreter(optcode)
    interpreter.input.put(2)
    interpreter.run()


def test():
    print("Test 1: Should print itself")
    optcode_raw = "109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99"
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    interpreter = OptcodeInterpreter(optcode)
    interpreter.run()

def test2():
    print("Test 2: Should print 16 bit number")
    optcode_raw = "1102,34915192,34915192,7,4,7,99,0"
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    interpreter = OptcodeInterpreter(optcode)
    interpreter.run()

def test3():
    print("Test 3: Should print large number in the middle")
    optcode_raw = "104,1125899906842624,99"
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    interpreter = OptcodeInterpreter(optcode)
    interpreter.run()

#test()
#test2()
#test3()

compute()

#!/usr/bin/env python3

from src.interpreter import OptcodeInterpreter


def read_input():
    # Run the program
    with open("input", "r") as hand:
        optcode_raw = hand.read()
    optcode = list(map(lambda el: int(el), optcode_raw.split(",")))
    return optcode


def explore():
    optcode = read_input()
    interpreter = OptcodeInterpreter(optcode, ascii_mode=True)

    def on_input_requested():
        if interpreter.input.empty():
            instructions = input("Input:")
            if instructions == "help":
                print("""

Possible commands are
- Movement via north, south, east, or west
- To take an item the droid sees in the environment, use the command take <name of item>. For example, if the droid reports seeing a red ball, you can pick it up with take red ball.
- To drop an item the droid is carrying, use the command drop <name of item>. For example, if the droid is carrying a green ball, you can drop it with drop green ball.
- To get a list of all of the items the droid is currently carrying, use the command inv (for "inventory").

Extra spaces or other characters aren't allowed - instructions must be provided precisely.


                """)
                on_input_requested()
            else:
                if not instructions.endswith("\n"):
                    instructions += "\n"
                    for el in instructions:
                        interpreter.input.put(el)

    interpreter.set_input_request_listener(on_input_requested)
    interpreter.run()

"""

    Security check     ==   Science Lab
        ||                      ||
        End                     Crew
                                ||
                                Holodom?
                                 ||
Escape pod == Engeneering  ==  Arcade               ??
                                ||                    ||
                              Corridor              Sick bay
                                ||                    ||
                              Warp Drive     ==      Hallway
                                ||                    ||
                               Hull  ==  [X]        Navigation
                                ||                     ||
               Passages  =   Storage                Chocolate factory
                  ||
                Stables

Needed items:
- antenna
- astrolabe
- space law space brochure
- weather machine


"""

if __name__ == "__main__":
    explore()
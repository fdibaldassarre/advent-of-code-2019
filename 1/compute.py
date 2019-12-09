#!/usr/bin/env python3

def get_fuel(weight):
   return int(int(weight) / 3) - 2

def get_fuel_iter(weight):
   total = 0
   keep = True
   while keep:
      fuel = get_fuel(weight)
      if fuel <= 0:
         keep = False
      else:
         total += fuel
         weight = fuel
   return total

print(get_fuel(12))
print(get_fuel(14))
print(get_fuel(1969))
print(get_fuel(100756))

print("===========")

print(get_fuel_iter(14))
print(get_fuel_iter(1969))
print(get_fuel_iter(100756))

print("==================")

total = 0
with open("input", "r") as hand:
   for weight in hand:
      weight = weight.strip()
      total += get_fuel_iter(weight)

print(total)

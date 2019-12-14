#!/usr/bin/env python3

import numpy as np


def get_element_levels(formulas):
    prices = {
        'ORE': 1
    }
    for el in formulas:
        prices[el] = None
    found_prices = 1
    while found_prices < len(prices):
        for target_name in formulas:
            if prices[target_name] is not None:
                continue
            element = formulas[target_name]
            sources = element['sources']
            max_source_price = 0
            for source in sources:
                if prices[source] is None:
                    max_source_price = None
                    break
                elif prices[source] > max_source_price:
                    max_source_price = prices[source]
            if max_source_price is not None:
                prices[target_name] = max_source_price + 1
                found_prices += 1
    return prices


def read_input():
    # Run the program
    formulas = {}
    with open("input", "r") as hand:
        for line in hand:
            source_raw, target_raw = line.strip().split("=>")
            target_qty, target_name = target_raw.strip().split(" ")
            sources_str = list(map(lambda el: el.split(" "), source_raw.strip().split(", ")))
            sources = {}
            for source_raw in sources_str:
                source_qty, source_name = source_raw[0], source_raw[1]
                sources[source_name] = int(source_qty)
            element = {
                'target': target_name,
                'qty': int(target_qty),
                'sources': sources
            }
            formulas[target_name] = element
    return formulas


def compute(formulas=None, elements_levels=None, target_fuel=1):
    formulas = read_input() if formulas is None else formulas
    elements_levels = get_element_levels(formulas) if elements_levels is None else elements_levels
    basket = {'FUEL': target_fuel}
    top_priced_el = None
    while top_priced_el != 'ORE':
        # Find the most costly element
        top_priced_el = sorted(basket.keys(), key=lambda el: elements_levels[el])[-1]
        if top_priced_el == 'ORE':
            break
        # Decompose the element
        formula = formulas[top_priced_el]
        formula_qty = formula['qty']
        sources = formula['sources']
        needed_qty = basket[top_priced_el]
        formula_multiplier = int(np.ceil(needed_qty / formula_qty))
        # Add all sources
        for source_name in sources:
            source_qty = sources[source_name] * formula_multiplier
            if source_name in basket:
                basket[source_name] += source_qty
            else:
                basket[source_name] = source_qty
        # Remove the element
        del basket[top_priced_el]
    return basket['ORE']


def get_mid_point(prev_point, fuel_interval):
    min_f, max_f = fuel_interval
    if max_f is None:
        return prev_point * 2
    else:
        return min_f + int((np.floor(max_f - min_f) / 2))


TARGET_ORE = 1000000000000


def compute2():
    formulas = read_input()
    elements_levels = get_element_levels(formulas)
    max_fuel = None
    fuel_interval = [1, None]
    current_fuel = 1
    while True:
        current_fuel = get_mid_point(current_fuel, fuel_interval)
        ore = compute(formulas, elements_levels, target_fuel=current_fuel)
        if ore <= TARGET_ORE:
            fuel_interval[0] = current_fuel
        else:
            fuel_interval[1] = current_fuel
        # Check interruption
        if fuel_interval[1] is not None:
            delta = fuel_interval[1] - fuel_interval[0]
            if delta == 1:
                max_fuel = fuel_interval[0]
                break
    return max_fuel


ores = compute()
print("Min ore:", ores)
result_fuel = compute2()
print("Max fuel", result_fuel)


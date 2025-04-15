# This file contains the function to generate the equation system for the stochastic cross product.
import re
import logging
from sympy import Eq, solve, Symbol

logging.getLogger().setLevel(logging.DEBUG)

def get_equation_system(cross_product, initial_state, final_state):
    """
    This function generates the equation system for the stochastic cross product.
    :param cross_product:
    :param initial_state:
    :param final_state:
    :return: the symbolic representation of trace probability from the slpn
    """
    eqs = []
    variables = []
    state_to_variable_map = {}
    state_idx = 1
    for state in cross_product.connected_states:
        if state == initial_state:
            variable_name = Symbol(f'a0', positive=True)
            variables.append(variable_name)
            state_to_variable_map[state] = variable_name
            continue
        variable_name = Symbol(f'a{state_idx}')
        variables.append(variable_name)
        state_to_variable_map[state] = variable_name
        state_idx += 1

    for transition in cross_product.transitions:
        if transition.to_state in cross_product.connected_states and transition.from_state in cross_product.connected_states:
            variable_name = Symbol(f'{transition.new_transition_name}')
            state_to_variable_map[transition] = variable_name

    for state in cross_product.connected_states:
        right_hand = 0
        for transition in cross_product.transitions:
            if transition.from_state == state and transition.to_state in cross_product.connected_states:
                right_hand += state_to_variable_map[transition] * state_to_variable_map[transition.to_state]
        if state == final_state:
            right_hand = 1
        eq = Eq(state_to_variable_map[state], right_hand)
        eqs.append(eq)

    sols = solve(eqs, variables)
    if len(sols) == 0:
        return str(0)

    variable_name = Symbol(f'a0', positive=True)
    input_string = str(sols[variable_name])
    # for transition in cross_product.transitions:
    return input_string


def expand_powers(s):
    """
    This function expands the powers in the string.
    :param s:
    :return:
    """
    # Function to replace match with expanded form
    def replacer(match):
        var = match.group(1)
        power = int(match.group(2))
        return '*'.join([var] * power)

    # Regex to match t<digit>**<power>
    pattern = re.compile(r"(t\d+)\*\*(\d+)")

    # Replace all occurrences using replacer function
    expanded_string = pattern.sub(replacer, s)
    return expanded_string
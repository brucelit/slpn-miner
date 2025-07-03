import numba
import numpy as np


plus_idx = -1
minus_idx = -2
prod_idx = -3
div_idx = -4


@numba.njit("float64(int16[::1], float64[::1], float64[::1])", inline='always', cache=True)
def calculate_inverse_poland_expression_numba(inverse_poland_expression, constants_dict, var_lst):
    calculate_stack = np.zeros(len(inverse_poland_expression), dtype=np.float64) # preallocate the stack
    stack_ptr = int(0)
    len_var_lst = len(var_lst)

    for idx in inverse_poland_expression:
        if idx == plus_idx:
            p2 = calculate_stack[stack_ptr - 2]
            p1 = calculate_stack[stack_ptr - 1]
            calculate_stack[stack_ptr - 2] = p2 + p1
            stack_ptr -= 1
        elif idx == minus_idx:
            p2 = calculate_stack[stack_ptr - 2]
            p1 = calculate_stack[stack_ptr - 1]
            calculate_stack[stack_ptr - 2] = p2 - p1
            stack_ptr -= 1
        elif idx == prod_idx:
            p2 = calculate_stack[stack_ptr - 2]
            p1 = calculate_stack[stack_ptr - 1]
            calculate_stack[stack_ptr - 2] = p2 * p1
            stack_ptr -= 1
        elif idx == div_idx:
            p2 = calculate_stack[stack_ptr - 2]
            p1 = calculate_stack[stack_ptr - 1]
            calculate_stack[stack_ptr - 2] = p2 / p1
            stack_ptr -= 1
        else:
            if idx < len_var_lst:
                val = var_lst[idx]
                calculate_stack[stack_ptr] = val
            else:
                constant_idx = idx - len_var_lst
                calculate_stack[stack_ptr] = constants_dict[constant_idx]
            stack_ptr += 1

    return calculate_stack[0]


def calculate_inverse_poland_expression(inverse_poland_expression, str_to_idx, var_lst):
    result = 0
    calculate_stack = []
    for str_val in inverse_poland_expression:
        if str_val in {'+', '-', '*', '/'}:
            # Do the calculation for two variables.
            p1 = calculate_stack.pop()
            p2 = calculate_stack.pop()
            result = simple_calculate(p2, p1, str_val)
            calculate_stack.append(result)
        else:
            if str_val in str_to_idx:
                calculate_stack.append(var_lst[str_to_idx[str_val]])
            else:
                calculate_stack.append(float(str_val))
    return result


def simple_calculate(p1, p2, operator):
    if operator == '+':
        return p1 + p2
    elif operator == '-':
        return p1 - p2
    elif operator == '*':
        return p1 * p2
    elif operator == '/':
        return p1 / p2
    else:
        raise ValueError("Invalid operator")


def get_inverse_poland_expression(exp):
    if exp is None:
        return None

    result2 = []
    len_exp = len(exp)
    operator = ['#']
    reverse_polish = []

    i = 0
    while i < len_exp:
        while i < len_exp and exp[i] == ' ':
            i += 1
        if i == len_exp:
            break

        if exp[i].isalpha():
            num = "n"
            i += 1
            while i < len_exp and exp[i].isdigit():
                num += exp[i]
                i += 1
            reverse_polish.append(num)
        elif exp[i].isdigit():
            num = ""
            while i < len_exp and exp[i].isdigit():
                num += exp[i]
                i += 1
            reverse_polish.append(num)
        elif exp[i] in {'+', '-', '*', '/', '(', ')'}:
            op = exp[i]
            if op == '(':
                operator.append(op)
            elif op == ')':
                while operator[-1] != '(':
                    reverse_polish.append(operator.pop())
                operator.pop()
            elif op in {'+', '-'}:
                if operator[-1] == '(':
                    operator.append(op)
                else:
                    while operator[-1] != '#' and operator[-1] != '(':
                        reverse_polish.append(operator.pop())
                    operator.append(op)
            elif op in {'*', '/'}:
                if operator[-1] == '(':
                    operator.append(op)
                else:
                    while operator[-1] != '#' and operator[-1] not in ['+', '-', '(']:
                        reverse_polish.append(operator.pop())
                    operator.append(op)
            i += 1

    while operator[-1] != '#':
        reverse_polish.append(operator.pop())

    while reverse_polish:
        temp1 = reverse_polish.pop()
        result2.insert(0, temp1)
    return result2

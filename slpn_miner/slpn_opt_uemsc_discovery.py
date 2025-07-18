from itertools import chain

import scipy
import numba
import pm4py

from pm4py.objects.petri_net.utils import final_marking, initial_marking
from pm4py.objects.log.importer.xes import importer as xes_importer
from slpn_miner.symbolic_conversion import *
from slpn_miner.util import setup, get_slpn
from slpn_miner.slpn_exporter import export_slpn, export_slpn_xml


def optimize_with_uemsc(log, pn, im, fm):
    # setup the preliminaries
    obj2add, var_name2idx_map, var_idx2name_map, var_lst = setup(log, pn, im, fm)

    # optimize for the uemsc objective function
    objective_function = get_uemsc_obj_func(obj2add, var_name2idx_map)
    trans_prob_result = optimize_with_basin_hopping(var_lst, objective_function)
    trans2weight = {}
    for i in range(len(var_lst)):
        trans2weight[str(var_idx2name_map[i])] = trans_prob_result[i]
    return trans2weight


def optimize_with_basin_hopping(x0, obj_func):
    """
    This function is used to optimize the objective function with basin hopping method,
    Regarding basin hopping global optimiser, refer to https://en.wikipedia.org/wiki/Basin-hopping
    :param x0: the initial gusee for variables
    :param obj_func: the objective function
    :return: the variable list that maximize er or uemsc-based measure
    """
    # add constraint such that every var is between 0 and 1
    bds = [(0.0001, 1) for i in range(len(x0))]
    # define the method and bound
    minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bds}
    # solve problem
    res = scipy.optimize.basinhopping(obj_func, x0, minimizer_kwargs=minimizer_kwargs)
    return res.x


@numba.njit()
def uemsc_objective_function(inverse_poland_exprs, trace_probs, constants_lookup, x):
    obj_func = 0
    for idx, inverse_poland_expr in enumerate(inverse_poland_exprs):
        trace_prob = trace_probs[idx]
        trace_in_slpn_prob = calculate_inverse_poland_expression_numba(inverse_poland_expr, constants_lookup, x)
        after_inverse = max(trace_prob - trace_in_slpn_prob, 0)
        obj_func += after_inverse
    # print("obj_func:",obj_func)
    return obj_func


def get_uemsc_obj_func(obj2add, var_name2idx_map):
    """
    This is the obj func to optimize for unit-Earth Mover's Stochastic Conformance (uEMSC) measure
    :param obj2add: each element is a list [trace_symbolic_prob, trace_real_prob]
    :param var_name2idx_map: map transition to value in var_lst
    :return: the calculated objective function for uEMSC
    """
    inverse_obj2add = [
        (get_inverse_poland_expression(trace_symbolic_prob), trace_real_prob)
        for trace_symbolic_prob, trace_real_prob in obj2add
    ]

    # Now map the expressions to indices:
    #   - Negative for operators
    #   - Positive < len(var_list) for variables
    #   - Positive >= len(var_list) for constants
    #       - Create a lookup array for these symbols
    # For this to work, IDs must be continuously assigned
    assert len(var_name2idx_map) == max(var_name2idx_map.values()) + 1, "IDs must be continuously assigned"

    operator_indexes = {'+': plus_idx, '-': minus_idx, '*': prod_idx, '/': div_idx}

    constant_symbols = {*chain(*(inverse_poland for inverse_poland, _ in inverse_obj2add))}
    constant_symbols = constant_symbols - var_name2idx_map.keys() - operator_indexes.keys()
    constant_symbols = list(constant_symbols)  # Put them on a list to order them

    constant_indexes = {symbol: len(var_name2idx_map) + idx for idx, symbol in enumerate(constant_symbols)}
    constants_lookup = np.array([float(symbol) for symbol in constant_symbols])

    symbol_to_idx = {**var_name2idx_map, **constant_indexes, **operator_indexes}
    inverse_obj2add = [
        ([symbol_to_idx[symbol] for symbol in inverse_poland], trace_prob)
        for inverse_poland, trace_prob in inverse_obj2add
    ]

    # Pack it into data types that are more friendly to numba
    # The most important is packing the poland expressions into a numpy array
    inverse_poland_exprs = [np.array(inverse_poland_exprs, dtype=np.int16)
                            for inverse_poland_exprs, _ in inverse_obj2add]
    inverse_poland_exprs = numba.typed.List(inverse_poland_exprs)
    trace_probs = [trace_prob for _, trace_prob in inverse_obj2add]
    trace_probs = np.array(trace_probs, dtype=np.float64)

    # Capture the variables
    def _uemsc_objective_function(x):
        return uemsc_objective_function(inverse_poland_exprs, trace_probs, constants_lookup, x)

    return _uemsc_objective_function


if __name__ == '__main__':
    # import log
    log = xes_importer.apply('../data/prepaid/prepaid_variants.xes')

    #  import petri nets
    pn, im, fm = pm4py.read_pnml('../data/prepaid/prepaid_heuristic.pnml', auto_guess_final_marking=True)
    fm = final_marking.discover_final_marking(pn)
    im = initial_marking.discover_initial_marking(pn)

    # optimize by maximizing the uEMSC objective function
    trans_weight_dict = optimize_with_uemsc(log, pn, im, fm)
    place_in_im_num, place2num, t2l, t2op_num, t2ip_num = get_slpn(pn, im)

    # visualize the slpn
    # gviz = visualize_slpn(pn, trans_weight_dict, initial_marking=im,final_marking=fm)
    # view(gviz)

    # export .slpn formart slpn
    # export_slpn("../data/hospital/hospital_id02_uemsc.slpn", place_in_im_num, place2num, t2l, t2ip_num, t2op_num, trans_weight_dict)

    # export .xml format slpn
    export_slpn_xml("../data/prepaid/prepaid_heuristic_uemsc.pnml", pn,im, trans_weight_dict)

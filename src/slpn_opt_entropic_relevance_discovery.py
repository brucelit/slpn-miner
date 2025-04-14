import math
import sys

import pm4py
import scipy

from pm4py.objects.log.importer.xes import importer as xes_importer

from src.slpn_visualiser import visualize_slpn, view
from src.symbolic_conversion import calculate_inverse_poland_expression, get_inverse_poland_expression
from src.util import setup, get_slpn
from src.slpn_exporter import export_slpn, export_slpn_xml


def optimize_with_er(log, pn, im, fm):
    # setup the preliminaries
    obj2add, var_name2idx_map, var_idx2name_map, var_lst = setup(log, pn, im, fm)

    # optimize for the entropic relevance objective function
    objective_function = get_er_obj_func(obj2add, var_name2idx_map)
    trans_prob_result = optimize_with_basin_hopping(var_lst, objective_function)
    trans2weight = {}
    for i in range(len(var_lst)):
        trans2weight[str(var_idx2name_map[i])] = trans_prob_result[i]
    return trans2weight


def get_er_obj_func(obj2add, var_name2idx_map):
    '''
    This is the obj func to optimize for entropic-relevance measure
    :param obj2add: each element is a list [trace_symbolic_prob, trace_real_prob]
    :param var_name2idx_map: map transition to value in var_lst
    :return: the calculated objective function for er
    '''

    def er_objective_function(var_lst):
        obj_func = 0
        for trace_symbolic_prob, trace_real_prob in obj2add:
            trace_in_slpn_prob = calculate_inverse_poland_expression(get_inverse_poland_expression(trace_symbolic_prob),
                                                                     var_name2idx_map, var_lst)
            if trace_in_slpn_prob == 0:
                continue
            obj_func -= math.log(trace_in_slpn_prob, 2) * trace_real_prob
        return obj_func

    return er_objective_function


def optimize_with_basin_hopping(var_lst, obj_func):
    '''
    This function is used to optimize the objective function with basin hopping method,
    Regarding basin hopping global optimiser, refer to https://en.wikipedia.org/wiki/Basin-hopping
    :param var:
    :param obj_func:
    :return: the variable list that maximize er or uemsc-based measure
    '''
    # add constraint such that every var is between 0 and 1
    bds = [(0.0001, 1) for i in range(len(var_lst))]
    # define the method and bound
    minimizer_kwargs = {"method": "L-BFGS-B", "bounds": bds}
    # solve problem
    res = scipy.optimize.basinhopping(obj_func, var_lst, minimizer_kwargs=minimizer_kwargs, niter=100, stepsize=0.00001)
    print(res)
    return res.x


if __name__ == '__main__':
    # import log
    log = xes_importer.apply('../data/hospital/Hospital Billing - Event Log.xes')

    #  import petri nets
    pn, im, fm = pm4py.read_pnml('../data/hospital/hospital_df09.pnml', auto_guess_final_marking=True)

    # optimize by maximizing the uEMSC objective function
    trans_weight_dict = optimize_with_er(log, pn, im, fm)
    place_in_im_num, place2num, t2l, t2op_num, t2ip_num = get_slpn(pn, im)

    # # visualize the slpn
    gviz = visualize_slpn(pn, trans_weight_dict, initial_marking=im, final_marking=fm)
    view(gviz)

    # export the slpn
    export_slpn("../data/hospital/hospital_df09_er.slpn", place_in_im_num, place2num, t2l, t2ip_num, t2op_num, trans_weight_dict)

    # export xml slpn
    # export_slpn_xml("../data/hospital/hospital_df09_er.pnml", pn, im, trans_weight_dict)
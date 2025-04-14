import pm4py
import scipy

from pm4py.objects.petri_net.utils import final_marking, initial_marking
from pm4py.objects.log.importer.xes import importer as xes_importer

from src.slpn_visualiser import visualize_slpn, view
from src.symbolic_conversion import calculate_inverse_poland_expression, get_inverse_poland_expression
from src.util import setup, get_slpn
from src.slpn_exporter import export_slpn, export_slpn_xml


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


def get_uemsc_obj_func(obj2add, var_name2idx_map):
    '''
    This is the obj func to optimize for unit-Earth Mover's Stochastic Conformance (uEMSC) measure
    :param obj2add: each element is a list [trace_symbolic_prob, trace_real_prob]
    :param var_name2idx_map: map transition to value in var_lst
    :return: the calculated objective function for uEMSC
    '''
    def uemsc_objective_function(x):
        obj_func = 0
        for trace_symbolic_prob, trace_real_prob in obj2add:
            trace_in_slpn_prob = calculate_inverse_poland_expression(
                get_inverse_poland_expression(trace_symbolic_prob), var_name2idx_map, x)
            after_inverse = max(trace_real_prob - trace_in_slpn_prob, 0)
            obj_func += after_inverse
        # print("uemsc:", obj_func)

        return obj_func
    return uemsc_objective_function


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

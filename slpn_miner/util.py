import re
import logging
import multiprocessing
import queue
from slpn_miner.log_util import get_stochastic_language
from slpn_miner.stochastic_cross_product import ConstructCP
from slpn_miner.stochastic_reachability_graph import construct_stochastic_reachability_graph
from slpn_miner.trace_dfa import create_dfa_from_list
logging.getLogger().setLevel(logging.DEBUG)


def get_cross_product_worker(args):
    """Worker function for multiprocessing"""
    trace_it, trace_ot, srg_it, srg_ot = args
    try:
        CP = ConstructCP()
        return CP.get_cross_product(trace_it, trace_ot, srg_it, srg_ot)
    except Exception as e:
        raise e

def run_with_timeout(trace_it, trace_ot, srg_it, srg_ot, timeout=3):
    """Run function with timeout using multiprocessing"""
    with multiprocessing.Pool(1) as pool:
        try:
            result = pool.apply_async(
                get_cross_product_worker,
                ((trace_it, trace_ot, srg_it, srg_ot),)
            )
            return result.get(timeout=timeout)
        except multiprocessing.TimeoutError:
            return "0"
        except Exception as e:
            print(f"Function error: {e}")
            return "0"

def get_cross_product_func(trace_it, trace_ot, srg_it, srg_ot):
    CP = ConstructCP()
    return CP.get_cross_product(trace_it, trace_ot, srg_it, srg_ot)


def setup(log, pn, im, fm):
    # get trace and its probability
    stochastic_lang = get_stochastic_language(log)

    # get the transition to weight mapping
    var_name2idx_map = {}
    var_idx2name_map = {}
    var_idx = 0
    var_lst = []
    for trans in pn.transitions:
        var_lst.append(1)
        var_name2idx_map[trans.name] = var_idx
        var_idx2name_map[var_idx] = trans.name
        var_idx += 1

    # construct rsg from petri net
    srg_it, srg_ot = construct_stochastic_reachability_graph(pn, im)

    # define obj function uemsc
    obj2add = []

    for trace, weight in stochastic_lang.items():
        weight_result = float(weight)
        trace_ot, trace_it = create_dfa_from_list(trace)

        symbolic_trace_prob = run_with_timeout(trace_it, trace_ot, srg_it, srg_ot, timeout=15)

        if symbolic_trace_prob == "0":
            print("trace with 0 prob: ", trace)
            continue
        print("find trace with prob:", trace)
        sub_obj = [symbolic_trace_prob, weight_result]
        obj2add.append(sub_obj)
    # iterate each trace
    # for trace, weight in stochastic_lang.items():
    #     # get trace probability
    #     weight_result = float(weight)
    #     # get trace incoming and outgoing transitions
    #     trace_ot, trace_it = create_dfa_from_list(trace)
    #     CP = ConstructCP()
    #     symbolic_trace_prob = CP.get_cross_product(trace_it, trace_ot, srg_it, srg_ot)
    #     print("symbolic: ", symbolic_trace_prob, type(symbolic_trace_prob))
    #     if symbolic_trace_prob == "0":
    #         continue
    #     print("find trace with prob:", trace, symbolic_trace_prob)
    #     sub_obj = [symbolic_trace_prob, weight_result]
    #     obj2add.append(sub_obj)

    covered_trace = sum(float(sublist[1]) for sublist in obj2add)
    if len(obj2add) == 0:
        logging.warning("No traces fit the model, the stochastic discovery will fail. "
                        "Please check the log and the model.")
    else:
        logging.info(f"The stochastic discovery covers {covered_trace:.2f} of the traces from the log.")

    return obj2add, var_name2idx_map, var_idx2name_map, var_lst


def get_slpn(pn, im):
    # place to number
    idx = 0
    place2num = {}
    for place in pn.places:
        place2num[place.name] = idx
        idx += 1

    # get initial marking
    place_in_im = extract_n_variables(str(im))
    place_in_im_num = [place2num[each] for each in place_in_im]

    # transition to weight
    t2l = {}
    t2ip_name = {}
    t2op_name = {}
    t2ip_num = {}
    t2op_num = {}
    for transition in pn.transitions:
        if transition.label is not None:
            t2l[transition.name] = transition.label
        else:
            t2l[transition.name] = "silent"
        t2ip_name[transition.name] = set()
        t2op_name[transition.name] = set()
        t2ip_num[transition.name] = set()
        t2op_num[transition.name] = set()

    for arc in pn.arcs:
        # is source is place, then it is the incoming for transition
        if arc.source in pn.places:
            transition_name = extract_n_variables(str(arc.target))[0]
            t2ip_name[transition_name].add(str(arc.source))
    for arc in pn.arcs:
        # is source is place, then it is the incoming for transition
        if arc.source in pn.transitions:
            transition_name = extract_n_variables(str(arc.source))[0]
            t2op_name[transition_name].add(str(arc.target))

    for k, v in t2op_name.items():
        for each in v:
            t2op_num[k].add(place2num[each])
    for k, v in t2ip_name.items():
        for each in v:
            t2ip_num[k].add(place2num[each])

    return place_in_im_num, place2num, t2l, t2op_num, t2ip_num


def extract_n_variables(s):
    pattern = r"n\d+"
    # Find all matches in the string
    return re.findall(pattern, s)

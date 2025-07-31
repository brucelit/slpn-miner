import pm4py

from pm4py.objects.petri_net.utils import final_marking, initial_marking
from slpn_miner.util import setup, get_slpn
from slpn_miner.slpn_exporter import export_slpn, export_slpn_xml


def get_unit_weights(pn):
    var_name2idx_map = {}
    var_idx2name_map = {}
    var_idx = 0
    var_lst = []
    for trans in pn.transitions:
        var_lst.append(1)
        var_name2idx_map[trans.name] = var_idx
        var_idx2name_map[var_idx] = trans.name
        var_idx += 1
    trans2weight = {}
    for i in range(len(var_lst)):
        trans2weight[str(var_idx2name_map[i])] = 1.0
    for k, v in trans2weight.items():
        print("Transition:", k, "Weight:", v)
    return trans2weight


if __name__ == '__main__':
    #  import petri nets
    pn, im, fm = pm4py.read_pnml('../data/domestic/domestic_id0.2.pnml', auto_guess_final_marking=True)
    fm = final_marking.discover_final_marking(pn)
    im = initial_marking.discover_initial_marking(pn)

    # optimize by maximizing the uEMSC objective function
    trans_weight_dict = get_unit_weights(pn)
    place_in_im_num, place2num, t2l, t2op_num, t2ip_num = get_slpn(pn, im)

    # visualize the slpn
    # gviz = visualize_slpn(pn, trans_weight_dict, initial_marking=im,final_marking=fm)
    # view(gviz)

    # export .slpn formart slpn
    export_slpn("../data/domestic/domestic_id0.2_unit.slpn", place_in_im_num, place2num, t2l, t2ip_num, t2op_num, trans_weight_dict)

    # export .xml format slpn
    # export_slpn_xml("../data/prepaid/prepaid_heuristic_uemsc.pnml", pn,im, trans_weight_dict)

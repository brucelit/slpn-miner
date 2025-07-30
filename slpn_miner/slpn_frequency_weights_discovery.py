import pm4py

from pm4py.objects.petri_net.utils import final_marking, initial_marking
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.attributes.log.get import get_attribute_values
from slpn_miner.util import setup, get_slpn
from slpn_miner.slpn_exporter import export_slpn, export_slpn_xml


def get_frequency_weights(pn, activity_frequencies):
    trans2weight = {}

    for trans in pn.transitions:
        if trans.label is None:
            print("trans labe")
            trans2weight[trans.name] = 1.0
        else:
            trans2weight[trans.name] = activity_frequencies[trans.label]

    for k,v in trans2weight.items():
        print("k: ",k, " v: ", v)

    return trans2weight


if __name__ == '__main__':
    log = xes_importer.apply('../data/road/road.xes')

    activity_frequencies = get_attribute_values(log, "concept:name")
    print(activity_frequencies)

    #  import petri nets
    pn, im, fm = pm4py.read_pnml('../data/road/road_df0.9.pnml', auto_guess_final_marking=True)
    for trans in pn.transitions:
        print(trans.label, trans.name)
    fm = final_marking.discover_final_marking(pn)
    im = initial_marking.discover_initial_marking(pn)

    # optimize by maximizing the uEMSC objective function
    trans_weight_dict = get_frequency_weights(pn,activity_frequencies)
    place_in_im_num, place2num, t2l, t2op_num, t2ip_num = get_slpn(pn, im)

    # visualize the slpn
    # gviz = visualize_slpn(pn, trans_weight_dict, initial_marking=im,final_marking=fm)
    # view(gviz)

    # export .slpn formart slpn
    export_slpn("../data/road/road_df09_freq.slpn", place_in_im_num, place2num, t2l, t2ip_num, t2op_num, trans_weight_dict)

    # export .xml format slpn
    # export_slpn_xml("../data/prepaid/prepaid_heuristic_uemsc.pnml", pn,im, trans_weight_dict)

import pm4py

from pm4py.objects.log.importer.xes import importer as xes_importer
from slpn_exporter import export_slpn
from src.log_util import get_stochastic_language
from util import prep, get_slpn

if __name__ == '__main__':
    # import log
    log = xes_importer.apply('../data/road/rtf_2000.xes')
    #  import petri nets
    pn, im, fm = pm4py.read_pnml('../data/road/road_id0.2.pnml', auto_guess_final_marking=True)

    trace_prob_map = get_stochastic_language(log)

    obj2add, var_name2idx_map, var_idx2name_map, var_lst = prep(log, pn, im, fm, trace_prob_map)

    # optimize by minimizing the uEMSC objective function
    # trans2weight = optimize_with_uemsc(obj2add, var_name2idx_map, var_idx2name_map, var_lst)

    # optimize by maximizing the Entropic Relevance objective function
    trans2weight = optimize_with_er(obj2add, var_name2idx_map, var_idx2name_map, var_lst)
    place_in_im_num, place2num, t2l, t2op_num, t2ip_num = get_slpn(pn, im)


    # export_slpn("../data/domestic/domestic_id02_uemsc_with_python.slpn", place_in_im_num, place2num, t2l, t2ip_num, t2op_num, trans2weight)

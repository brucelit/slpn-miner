import pm4py
import logging

from pm4py.objects.petri_net.utils import final_marking, initial_marking
from slpn_miner.src.slpn_opt_uemsc_discovery import optimize_with_uemsc
from slpn_miner.src.slpn_visualiser import visualize_slpn, view
from pm4py.objects.log.importer.xes import importer as xes_importer
from .util import get_slpn
from .slpn_exporter import export_slpn, export_slpn_xml
from pm4py.objects.petri_net.utils import check_soundness
from pm4py.visualization.transition_system import visualizer as ts_visualizer

logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    # import log
    log = xes_importer.apply('../data/road/Road_Traffic_Fine_Management_Process.xes')

    #  import petri nets
    pn, im, fm = pm4py.read_pnml('../data/road/road_id0.2.pnml', auto_guess_final_marking=True)
    fm = final_marking.discover_final_marking(pn)
    im = initial_marking.discover_initial_marking(pn)

    # perform soundness and wof analysis for the imported model
    soundness_result = check_soundness.check_easy_soundness_of_wfnet(pn)
    wof_result = check_soundness.check_wfnet(pn)
    if not soundness_result:
        logging.error("The imported model is not easy sound")
    if not wof_result:
        logging.error("The imported model is not a work flow net")

    # optimize by maximizing the uEMSC objective function
    trans_weight_dict = optimize_with_uemsc(log, pn, im, fm)
    place_in_im_num, place2num, t2l, t2op_num, t2ip_num = get_slpn(pn, im)

    # visualize the slpn
    gviz = visualize_slpn(pn, trans_weight_dict, initial_marking=im, final_marking=fm)
    view(gviz)

    # export .slpn formart slpn
    export_slpn("../data/road/road_id0.2_uemsc.slpn", place_in_im_num, place2num, t2l, t2ip_num, t2op_num, trans_weight_dict)

    # export .xml format slpn
    export_slpn_xml("../data/road/rtf_heuristic_uemsc.pnml", pn,im, trans_weight_dict)
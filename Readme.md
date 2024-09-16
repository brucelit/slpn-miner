# SLPNMiner

SLPNMiner is a ProM package for the discovery of Stochastic Labelled Petri net, which provides plugin-ins for stochastic process discovery. The input are an event log and a Petri net model, and the output is a stochastic labelled petri net. The two current implemented plugins adopt the techniques introduced in the following to assist weight estimation. 

* Entropic relevance:
[Hanan Alkhammash, Artem Polyvyanyy, Alistair Moffat, Luciano García-Bañuelos: Entropic relevance: A mechanism for measuring stochastic process models discovered from event data. Inf. Syst. 107: 101922 (2022)](https://www.sciencedirect.com/science/article/pii/S0306437921001277)

* Unit Earth Mover Stochastic Conformance:
[Sander J. J. Leemans, Wil M. P. van der Aalst, Tobias Brockhoff, Artem Polyvyanyy: Stochastic process mining: Earth movers' stochastic conformance. Inf. Syst. 102: 101724 (2021)](https://www.sciencedirect.com/science/article/pii/S0306437921001277)

## Note
This is a re-implementation of ProM plugin-in for stochastic labelled Petri net discovery. We use a better global optimisation solver that produces better results than the original implementation.

For large event log, the converging time for the optimisation may be long. We recommend starting from a smaller model for testing.

## Usage
Take the Entropic Relevance-based stochastic discovery algorithm as an example, the input are an event log and a Petri net model, and the output is a stochastic labelled Petri net. The following is the code snippet to use the Entropic Relevance-based stochastic discovery algorithm. 

Change the input and output path for your log and petri net, and slpn in the main.py file.

```python
import pm4py

from pm4py.objects.petri_net.utils import final_marking, initial_marking
from src.slpn_opt_uemsc_discovery import optimize_with_uemsc
from src.slpn_visualiser import visualize_slpn, view
from pm4py.objects.log.importer.xes import importer as xes_importer
from util import get_slpn
from slpn_exporter import export_slpn, export_slpn_xml


if __name__ == '__main__':
    # import log
    log = xes_importer.apply('../data/road/Road_Traffic_Fine_Management_Process.xes')

    #  import petri nets
    pn, im, fm = pm4py.read_pnml('../data/road/rtfm_hm_abe.pnml', auto_guess_final_marking=True)
    fm = final_marking.discover_final_marking(pn)
    im = initial_marking.discover_initial_marking(pn)

    # optimize by maximizing the uEMSC objective function
    trans_weight_dict = optimize_with_uemsc(log, pn, im, fm)
    place_in_im_num, place2num, t2l, t2op_num, t2ip_num = get_slpn(pn, im)

    # visualize the slpn
    gviz = visualize_slpn(pn, trans_weight_dict, initial_marking=im,final_marking=fm)
    view(gviz)

    # export .slpn formart slpn
    # export_slpn("../data/hospital/hospital_id02_uemsc.slpn", place_in_im_num, place2num, t2l, t2ip_num, t2op_num, trans_weight_dict)

    # export .xml format slpn
    export_slpn_xml("../data/road/rtf_heuristic_uemsc.pnml", pn,im, trans_weight_dict)
```

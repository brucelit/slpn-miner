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

Change the path for your input and output.

```python
    # import log
    log = xes_importer.apply('../data/domestic/BPI_Challenge_2020_DomesticDeclarations.xes')

    #  import petri nets
    pn, im, fm = pm4py.read_pnml('../data/domestic/domestic_df0.9.pnml', auto_guess_final_marking=True)

    # optimize by maximizing the uEMSC objective function
    trans_weight_dict = optimize_with_er(log, pn, im, fm)
    place_in_im_num, place2num, t2l, t2op_num, t2ip_num = get_slpn(pn, im)

    # visualize the slpn
    gviz = visualize_slpn(pn, trans_weight_dict, initial_marking=im, final_marking=fm)
    view(gviz)

    # export the .slpn format slpn
    export_slpn("../data/domestic/domestic_df09_er.slpn", place_in_im_num, place2num, t2l, t2ip_num, t2op_num,
                trans_weight_dict)

    # export the .pnml format slpn
    export_slpn_xml("../data/domestic/domestic_df09_er.pnml", pn, im, trans_weight_dict)
```

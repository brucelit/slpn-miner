import time
from enum import Enum

from pm4py.objects import petri_net
from pm4py.objects.petri_net.utils import align_utils
from pm4py.objects.transition_system import obj as ts
from pm4py.util import exec_utils

from src.stochastic_transition_system import StochasticTransitionSystem


class Parameters(Enum):
    MAX_ELAB_TIME = "max_elab_time"
    PETRI_SEMANTICS = "petri_semantics"


def marking_flow_petri(net, im, return_eventually_enabled=False, parameters=None):
    """
    Construct the marking flow of a Petri net

    Parameters
    -----------------
    net
        Petri net
    im
        Initial marking
    return_eventually_enabled
        Return the eventually enabled (visible) transitions
    """
    if parameters is None:
        parameters = {}

    # set a maximum execution time of 1 day (it can be changed by providing the parameter)
    max_exec_time = exec_utils.get_param_value(Parameters.MAX_ELAB_TIME, parameters, 86400)
    semantics = exec_utils.get_param_value(Parameters.PETRI_SEMANTICS, parameters,
                                           petri_net.semantics.ClassicSemantics())

    start_time = time.time()

    incoming_transitions = {im: set()}
    outgoing_transitions = {}
    eventually_enabled = {}

    active = [im]
    while active:
        if (time.time() - start_time) >= max_exec_time:
            # interrupt the execution
            return incoming_transitions, outgoing_transitions, eventually_enabled
        m = active.pop()
        enabled_transitions = semantics.enabled_transitions(net, m)
        if return_eventually_enabled:
            eventually_enabled[m] = align_utils.get_visible_transitions_eventually_enabled_by_marking(net, m)
        outgoing_transitions[m] = {}
        for t in enabled_transitions:
            nm = semantics.weak_execute(t, net, m)
            outgoing_transitions[m][t] = nm
            if nm not in incoming_transitions:
                incoming_transitions[nm] = set()
                if nm not in active:
                    active.append(nm)
            incoming_transitions[nm].add(t)

    return incoming_transitions, outgoing_transitions, eventually_enabled


def construct_stochatic_reachability_graph_from_flow(incoming_transitions, outgoing_transitions,
                                                     use_trans_name=False, parameters=None):
    """
    Construct the reachability graph from the marking flow

    Parameters
    ----------------
    incoming_transitions
        Incoming transitions
    outgoing_transitions
        Outgoing transitions
    use_trans_name
        Use the transition name

    Returns
    ----------------
    re_gr
        Transition system that represents the reachability graph of the input Petri net.
    """
    if parameters is None:
        parameters = {}

    re_gr = StochasticTransitionSystem()
    map_states = {}

    for s in incoming_transitions:
        map_states[s] = ts.TransitionSystem.State(s)
        re_gr.states.add(map_states[s])
        #     get the initial state:
        if len(incoming_transitions[s]) == 0:
            re_gr.init_state = map_states[s]

    new_t_id = 0
    for s1 in outgoing_transitions:
        total_trans_weight = ""
        count = 0
        for t in outgoing_transitions[s1]:
            if count == 0:
                total_trans_weight += "(" + str(t.name)
            else:
                total_trans_weight += "+" + str(t.name)
            count += 1
        total_trans_weight += ")"

        for t in outgoing_transitions[s1]:
            s2 = outgoing_transitions[s1][t]
            if t.label is None:
                if count == 1:
                    add_arc_from_to(new_t_id, t.name, t.label, "1", map_states[s1], map_states[s2], re_gr)
                else:
                    add_arc_from_to(new_t_id, t.name, t.label, t.name + "/" + total_trans_weight, map_states[s1],
                                    map_states[s2], re_gr)
            else:
                if count == 1:
                    add_arc_from_to(new_t_id, t.name, t.label, "1", map_states[s1], map_states[s2], re_gr)
                else:
                    add_arc_from_to(new_t_id, t.name, t.label, t.name + "/" + total_trans_weight, map_states[s1],
                                    map_states[s2], re_gr)
            new_t_id += 1
    return re_gr


def construct_srg(incoming_transitions, outgoing_transitions, parameters=None):
    """
    Construct the reachability graph from the marking flow

    Parameters
    ----------------
    incoming_transitions
        Incoming transitions
    outgoing_transitions
        Outgoing transitions
    use_trans_name
        Use the transition name

    Returns
    ----------------
    incoming_transitions
        Incoming transitions
    outgoing_transitions
        Outgoing transitions.
    """
    if parameters is None:
        parameters = {}

    re_gr = StochasticTransitionSystem()

    map_states = {}
    srg_incoming_transitions = {}

    for s in incoming_transitions:
        map_states[s] = ts.TransitionSystem.State(s)
        re_gr.states.add(map_states[s])
        #     get the initial state:
        srg_incoming_transitions[map_states[s]] = incoming_transitions[s]

    srg_outgoing_transitions = {}

    new_t_id = 0
    for s1 in outgoing_transitions:
        srg_outgoing_transitions[map_states[s1]] = {}
        total_trans_weight = ""
        count = 0
        for t in outgoing_transitions[s1]:
            if count == 0:
                total_trans_weight += "(" + str(t.name)
            else:
                total_trans_weight += "+" + str(t.name)
            count += 1
        total_trans_weight += ")"

        for t in outgoing_transitions[s1]:
            s2 = outgoing_transitions[s1][t]
            if count == 1:
                transition = ("t" + str(new_t_id), t.name, t.label, "1")
            else:
                transition = ("t" + str(new_t_id), t.name, t.label, t.name + "/" + total_trans_weight)
            srg_outgoing_transitions[map_states[s1]][transition] = map_states[s2]
            new_t_id += 1
    return srg_incoming_transitions, srg_outgoing_transitions


def add_arc_from_to(new_t_id, original_t_id, t_label, t_prob, fr, to, stochastic_ts, data=None):
    """
    Adds a transition from a state to another state in some transition system.
    Assumes from and to are in the transition system!

    Parameters
    ----------
    name: name of the transition
    fr: state from
    to:  state to
    ts: transition system to use
    data: data associated to the Transition System

    Returns
    -------
    None
    """
    tran = StochasticTransitionSystem.Transition("t" + str(new_t_id), original_t_id,
                                                 t_label, t_prob, fr, to, data)
    stochastic_ts.transitions.add(tran)

    fr.outgoing.add(tran)
    to.incoming.add(tran)


def construct_stochastic_reachability_graph(net, initial_marking, parameters=None):
    """
    Creates a reachability graph of a certain Petri net.
    DO NOT ATTEMPT WITH AN UNBOUNDED PETRI NET, EVER.

    Parameters
    ----------
    net: Petri net
    initial_marking: initial marking of the Petri net.

    Returns
    -------
    re_gr: Transition system that represents the reachability graph of the input Petri net.
    """
    incoming_transitions, outgoing_transitions, eventually_enabled = marking_flow_petri(net, initial_marking, parameters=parameters)
    srg_incoming_transitions, srg_outgoing_transitions = construct_srg(incoming_transitions, outgoing_transitions, parameters=parameters)
    return srg_incoming_transitions, srg_outgoing_transitions


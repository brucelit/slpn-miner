# construct a cross product between stochastic reachability graph of the petri net and a trace dfa

import copy
import logging
import re
import stochastic_transition_system

from stochastic_equation_system import get_equation_system, expand_powers
from stochastic_transition_system import StochasticTransitionSystem

logging.getLogger().setLevel(logging.DEBUG)


def set_and_get_initial_state(trace_incoming_transitions,
                              srg_incoming_transitions
                              ):
    '''

    :param trace_incoming_transitions:
    :param srg_incoming_transitions:
    :param cross_product:
    :return: the initial states in trace and srg
    '''
    for s1 in trace_incoming_transitions:
        if trace_incoming_transitions[s1] is None:
            for s2 in srg_incoming_transitions:
                if len(srg_incoming_transitions[s2]) == 0:
                    return s1, s2


class ConstructCP:
    boundary_states_in_rsg = dict()
    cross_product = StochasticTransitionSystem()
    connected_to_initial_state_set = set()
    connected_to_final_state_set = set()
    connected_states = set()

    def get_cross_product(self,
                          trace_incoming_transitions,
                          trace_outgoing_transitions,
                          srg_incoming_transitions,
                          srg_outgoing_transitions):
        '''

        :param trace_incoming_transitions:
        :param trace_outgoing_transitions:
        :param srg_incoming_transitions:
        :param srg_outgoing_transitions:
        :return: a cross product as a stochastic transition system between trace and srg
        '''
        self.cross_product.connected_states = set()
        self.boundary_states_in_rsg = dict()
        self.cross_product = StochasticTransitionSystem()
        self.connected_to_initial_state_set = set()
        self.connected_to_final_state_set = set()
        self.connected_states = set()

        try:
            # set the initial state for cross product system
            trace_init_state, srg_init_state = set_and_get_initial_state(trace_incoming_transitions, srg_incoming_transitions)
        except TypeError:
            raise SystemExit(
                "No initial state found for the stochastic reachability graph. Please check the input petri net.")

        # set current state to be the initial state
        trace_current_state = trace_init_state

        # add the initial state to the boundary states
        self.boundary_states_in_rsg[srg_init_state] = True

        # loop until reaching the final state in trace
        while trace_outgoing_transitions[trace_current_state] is not None:
            # get the transition label from trace
            trace_transition_label = trace_outgoing_transitions[trace_current_state][0]
            temp_boundary_in_rsg = copy.copy(self.boundary_states_in_rsg)

            for srg_state_to_explore, flag in self.boundary_states_in_rsg.items():
                # if the transition is fired in this state
                if flag is False:
                    del temp_boundary_in_rsg[srg_state_to_explore]
                    continue
                temp_boundary_in_rsg[srg_state_to_explore] = False

            for srg_state_to_explore, flag in temp_boundary_in_rsg.items():
                # if the transition is fired in this state
                self.get_match_states(trace_outgoing_transitions,
                                      trace_transition_label,
                                      trace_current_state,
                                      srg_outgoing_transitions,
                                      srg_state_to_explore
                                      )

            # continue with the next state in trace
            trace_current_state = trace_outgoing_transitions[trace_current_state][1]

        trace_final_state = ""
        for state, key in trace_outgoing_transitions.items():
            if key is None:
                trace_final_state = state

        rsg_final_state_set = set()
        rsg_final_state = ""
        for state, key in srg_outgoing_transitions.items():
            if len(key) == 0:
                rsg_final_state = state.name
                rsg_final_state_set.add(rsg_final_state)

        trace_init_state = ""
        for state, key in trace_incoming_transitions.items():
            if key is None:
                trace_initial_state = state

        connected_states = set()
        rsg_initial_state = ""
        for state, key in srg_incoming_transitions.items():
            if len(key) == 0:
                rsg_initial_state = state.name
        trace_prob = "0"

        for rsg_final_state in rsg_final_state_set:
            if (self.cross_product.get_state_by_name(str(trace_final_state) + str(rsg_final_state))) is not None:
                # print("have a final state: ", str(trace_final_state) + str(rsg_final_state))
                cross_product_final_state = str(trace_final_state) + str(rsg_final_state)
            else:
                trace_prob = "0"
                continue

            if (self.cross_product.get_state_by_name(str(trace_initial_state) + str(rsg_initial_state))) is not None:
                cross_product_initial_state = str(trace_initial_state) + str(rsg_initial_state)
            else:
                trace_prob = "0"
                continue

            # construc_equation_system()
            initial_state = self.cross_product.get_state_by_name(cross_product_initial_state)
            final_state = self.cross_product.get_state_by_name(cross_product_final_state)

            self.connected_to_initial_state(initial_state)
            self.connected_to_final_state(final_state)
            self.connected(initial_state, final_state)

            trace_prob = get_equation_system(self.cross_product, initial_state, final_state)
            if trace_prob != "0":
                break

        if trace_prob != "0":
            pattern = r't\d+'
            # Replace substrings using re.sub with the replace_match function
            s = re.sub(pattern, self.replace_variables, expand_powers(trace_prob))
            updated_trace_prob = s.replace("1*", "")
            return updated_trace_prob

        logging.debug("Cannot derive the probability of this trace from model.")
        return "0"

    def replace_variables(self, match):
        variable_name = match.group(0)
        for transition in self.cross_product.transitions:
            if transition.new_transition_name == variable_name:
                return transition.transition_prob

    def connected(self, initial_state, final_state):
        '''
        :return: update cross product
        '''
        self.cross_product.connected_states = self.connected_to_initial_state_set & self.connected_to_final_state_set
        self.cross_product.connected_states.add(initial_state)
        self.cross_product.connected_states.add(final_state)

    def connected_to_initial_state(self, state_to_explore):
        '''

        :return: update cross product
        '''
        for transition in self.cross_product.transitions:
            if transition.from_state == state_to_explore:
                self.connected_to_initial_state_set.add(transition.to_state)
                self.connected_to_initial_state(transition.to_state)

    def connected_to_final_state(self, state_to_explore):
        '''

        :return: update cross product
        '''
        for transition in self.cross_product.transitions:
            if transition.to_state == state_to_explore:
                self.connected_to_final_state_set.add(transition.from_state)
                self.connected_to_final_state(transition.from_state)

    def get_match_states(self,
                         trace_outgoing_transitions,
                         trace_transition_label,
                         trace_current_state,
                         srg_outgoing_transitions,
                         srg_current_state,
                         ):
        '''

        :param trace_outgoing_transitions:
        :param trace_transition_label:
        :param trace_current_state:
        :param srg_outgoing_transitions:
        :param srg_current_state:
        :param non_silent_tansition_num: count the time we observe non-silent transitions
        :return: no return
        '''
        state_name = str(trace_current_state) + str(srg_current_state)

        # iterate until find the matching state with same transition_label
        for srg_out_trans, srg_next_state in srg_outgoing_transitions[srg_current_state].items():

            # if the srg transition is no-silent and equals the trace transition label
            if srg_out_trans[2] == trace_transition_label:
                # cross_product.add_state(state_name)
                cross_state = self.cross_product.get_state_by_name(state_name)
                if cross_state is None:
                    cross_state = StochasticTransitionSystem.State(name=state_name)
                    # add the state to cp
                    self.cross_product.states.add(cross_state)

                # add state to boundary
                self.boundary_states_in_rsg[srg_next_state] = True
                trace_next_state = trace_outgoing_transitions[trace_current_state][1]
                # aim to add transition
                self.get_future_matching_states(trace_outgoing_transitions,
                                                srg_outgoing_transitions,
                                                trace_transition_label,
                                                trace_next_state,
                                                srg_next_state,
                                                srg_out_trans,
                                                cross_state)

            # if the srg transition is silent, we continue to explore the next state
            elif srg_out_trans[2] is None:

                cross_state = self.cross_product.get_state_by_name(state_name)
                if cross_state is None:
                    cross_state = StochasticTransitionSystem.State(name=state_name)
                    # add the state to cp
                    self.cross_product.states.add(cross_state)
                # visited_state_set.add(state_name)
                if srg_next_state not in self.boundary_states_in_rsg:
                    self.boundary_states_in_rsg[srg_next_state] = False
                    self.get_future_matching_states(trace_outgoing_transitions,
                                                    srg_outgoing_transitions,
                                                    trace_transition_label,
                                                    trace_current_state,
                                                    srg_next_state,
                                                    srg_out_trans,
                                                    cross_state)

    def get_future_matching_states(self,
                                   trace_outgoing_transitions,
                                   srg_outgoing_transitions,
                                   trace_transition_label,
                                   trace_current_state,
                                   srg_current_state,
                                   srg_previous_trans,
                                   cross_state_previous):
        state_name = str(trace_current_state) + str(srg_current_state)
        cross_state = self.cross_product.get_state_by_name(state_name)

        # if the arc is already in, then we do not add a transition
        if cross_state is not None:
            if not (
                    self.cross_product.transition_exists(srg_previous_trans[2], cross_state_previous.name,
                                                         cross_state.name)):
                self.add_arc_from_to(srg_previous_trans[0],
                                     srg_previous_trans[1],
                                     srg_previous_trans[2],
                                     srg_previous_trans[3],
                                     cross_state_previous,
                                     cross_state
                                     )

        #  if the cross state is None
        else:
            cross_state = StochasticTransitionSystem.State(name=state_name)
            self.cross_product.add_state(state_name)
            # add the state to cp
            self.cross_product.states.add(cross_state)
            # if the current state is already in cross product, we do not add it again
            # add the state to already visited_state_set
            self.add_arc_from_to(srg_previous_trans[0],
                                 srg_previous_trans[1],
                                 srg_previous_trans[2],
                                 srg_previous_trans[3],
                                 cross_state_previous,
                                 cross_state
                                 )

        # continue the search
        for srg_out_trans, srg_next_state in srg_outgoing_transitions[srg_current_state].items():

            # continue if firing non-silent transition for next state
            if self.boundary_states_in_rsg[srg_current_state] is False and srg_out_trans[2] == trace_transition_label:
                self.boundary_states_in_rsg[srg_next_state] = True
                self.get_future_matching_states(trace_outgoing_transitions,
                                                srg_outgoing_transitions,
                                                trace_transition_label,
                                                trace_outgoing_transitions[trace_current_state][1],
                                                srg_next_state,
                                                srg_out_trans,
                                                cross_state)

            elif self.boundary_states_in_rsg[srg_current_state] is False and srg_out_trans[2] is None:
                self.boundary_states_in_rsg[srg_next_state] = False
                self.get_future_matching_states(trace_outgoing_transitions,
                                                srg_outgoing_transitions,
                                                trace_transition_label,
                                                trace_current_state,
                                                srg_next_state,
                                                srg_out_trans,
                                                cross_state)

            # continue if firing silent transition for next state
            elif self.boundary_states_in_rsg[srg_current_state] is True and srg_out_trans[2] is None:
                self.boundary_states_in_rsg[srg_next_state] = True
                self.get_future_matching_states(trace_outgoing_transitions,
                                                srg_outgoing_transitions,
                                                trace_transition_label,
                                                trace_current_state,
                                                srg_next_state,
                                                srg_out_trans,
                                                cross_state)

    def add_arc_from_to(self, new_t_name, original_t_name, t_label, t_prob, fr, to):
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
        :param original_t_name:
        :param new_t_name:
        """
        tran = stochastic_transition_system.StochasticTransitionSystem.Transition(
            str(new_t_name),
            original_t_name,
            t_label,
            t_prob,
            fr,
            to
        )
        self.cross_product.transitions.add(tran)

        fr.outgoing.add(tran)
        to.incoming.add(tran)
from pm4py.objects.transition_system import constants

class StochasticTransitionSystem(object):
    def __init__(self, name=None, states=None, transitions=None):
        self.states_set = set()
        self.__name = "" if name is None else name
        self.__states = set() if states is None else states
        self.__transitions = set() if transitions is None else transitions

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    def __get_states(self):
        return self.__states

    def __get_transitions(self):
        return self.__transitions

    def __set_transitions(self, transitions):
        self.__transitions = transitions

    def get_init_state(self):
        return self.init_state

    def add_state(self, state):
        self.states_set.add(state)

    def get_state_by_name(self,state_name):
        for state in self.states:
            if state.name == state_name:
                return state
        return None

    def transition_exists(self, transition_label, from_state, to_state):
        for transition in self.transitions:
            if transition_label == transition.transition_label and str(transition.from_state)== str(from_state) and str(transition.to_state) == str(to_state):
                return True
        return False

    name = property(__get_name, __set_name)
    transitions = property(__get_transitions, __set_transitions)
    states = property(__get_states)
    init_state = None
    cross_state_counter = 0
    cross_state_counter_map = dict()
    connected_states = set()

    class State(object):
        def __init__(self, name, incoming=None, outgoing=None, data=None,is_start=False, is_accept=False,):
            self.__name = name
            self.__incoming = set() if incoming is None else incoming
            self.__outgoing = set() if outgoing is None else outgoing
            self.__data = {constants.INGOING_EVENTS: [], constants.OUTGOING_EVENTS: []} if data is None else data

        def __get_name(self):
            return self.__name

        def __set_name(self, name):
            self.__name = name

        def __get_outgoing(self):
            return self.__outgoing

        def __set_outgoing(self, outgoing):
            self.__outgoing = outgoing

        def __get_incoming(self):
            return self.__incoming

        def __set_incoming(self, incoming):
            self.__incoming = incoming

        def __get_data(self):
            return self.__data

        def __set_data(self, data):
            self.__data = data

        def __repr__(self):
            return str(self.name)


        name = property(__get_name, __set_name)
        incoming = property(__get_incoming, __set_incoming)
        outgoing = property(__get_outgoing, __set_outgoing)
        data = property(__get_data, __set_data)

    class Transition(object):

        def __init__(self, new_transition_name, original_transition_name, transition_label, transition_prob, from_state, to_state, data=None):
            self.__new_transition_name = new_transition_name
            self.__original_transition_name = original_transition_name
            self.__transition_label = transition_label
            self.__transition_prob = transition_prob
            self.__from_state = from_state
            self.__to_state = to_state

        
        def __get_new_transition_name(self):
            return self.__new_transition_name

        def __set_new_transition_name(self,new_transition_name):
            self.__new_transition_name = new_transition_name

        def __get_original_transition_name(self):
            return self.__original_transition_name

        def __set_original_transition_name(self,original_transition_name):
            self.__original_transition_name = original_transition_name

        def __get_transition_label(self):
            return self.__transition_label

        def __set_transition_label(self,transition_label):
            self.__transition_label = transition_label

        def __get_transition_prob(self):
            return self.__transition_prob

        def __set_transition_prob(self,transition_prob):
            self.__transition_prob = transition_prob

        def __get_to_state(self):
            return self.__to_state

        def __set_to_state(self, to_state):
            self.__to_state = to_state

        def __get_from_state(self):
            return self.__from_state

        def __set_from_state(self, from_state):
            self.__from_state = from_state

        def __repr__(self):
            return str(self.transition_label)

        new_transition_name = property(__get_new_transition_name, __set_new_transition_name)
        original_transition_name = property(__get_original_transition_name, __set_original_transition_name)
        transition_label = property(__get_transition_label, __set_transition_label)
        transition_prob = property(__get_transition_prob, __set_transition_prob)
        from_state = property(__get_from_state, __set_from_state)
        to_state = property(__get_to_state, __set_to_state)

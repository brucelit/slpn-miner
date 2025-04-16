def create_dfa_from_list(symbol_list):
    return get_outgoing(symbol_list), get_incoming(symbol_list)


def get_outgoing(symbol_list):
    outgoing_transitions = {}
    for i in range(len(symbol_list)):
        outgoing_transitions[i] = (symbol_list[i], i + 1)
    outgoing_transitions[i + 1] = None
    return outgoing_transitions


def get_incoming(symbol_list):
    incoming_transitions = {0: None}
    for i in range(1, len(symbol_list) + 1):
        incoming_transitions[i] = (symbol_list[i - 1], i - 1)
    return incoming_transitions

# This .py file provide two types of exporter for stochastic labeled petri net
# The first output format is an .slpn file
# The second output format is an .xml file

import uuid
from lxml import etree
from pm4py.objects.petri_net.obj import Marking
from pm4py.objects.petri_net.obj import PetriNet, ResetNet, InhibitorNet
from pm4py.objects.petri_net import properties as petri_properties
from pm4py.util import constants, exec_utils
from enum import Enum


class Parameters(Enum):
    ENCODING = "encoding"


def export_slpn_xml(output_path, petrinet, marking, trans2weight, final_marking=None, export_prom5=False, parameters=None):
    """
    Export a stochastic labeled Petri net (slpn) to an XML tree. In the exported xml file, each transition in the slpn has a weight information.
    Parameters
    ----------
       output_path: output path of the slpn file
    petrinet: :class:`pm4py.entities.petri.petrinet.PetriNet`
        Petri net
    marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Marking
    final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
        Final marking (optional)
    export_prom5
        Enables exporting PNML files in a format that is ProM5-friendly
    parameters
        Other parameters of the algorithm

    Returns
    ----------
    tree
        XML tree
    """
    if parameters is None:
        parameters = {}

    if final_marking is None:
        final_marking = Marking()

    root = etree.Element("pnml")
    net = etree.SubElement(root, "net")
    net.set("id", petrinet.name)
    netname = etree.SubElement(net, "name")
    netnametext = etree.SubElement(netname, "text")
    netnametext.text = petrinet.name
    net.set("type", "http://www.pnml.org/version-2009/grammar/pnmlcoremodel")
    if export_prom5 is True:
        page = net
    else:
        page = etree.SubElement(net, "page")
        page.set("id", "n0")
    places_map = {}
    for place in petrinet.places:
        places_map[place] = place.name
        pl = etree.SubElement(page, "place")
        pl.set("id", place.name)
        pl_name = etree.SubElement(pl, "name")
        pl_name_text = etree.SubElement(pl_name, "text")
        pl_name_text.text = place.properties[
            constants.PLACE_NAME_TAG] if constants.PLACE_NAME_TAG in place.properties else place.name
        if place in marking:
            pl_initial_marking = etree.SubElement(pl, "initialMarking")
            pl_initial_marking_text = etree.SubElement(pl_initial_marking, "text")
            pl_initial_marking_text.text = str(marking[place])
        if constants.LAYOUT_INFORMATION_PETRI in place.properties:
            graphics = etree.SubElement(pl, "graphics")
            position = etree.SubElement(graphics, "position")
            position.set("x", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            position.set("y", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][0][1]))
            dimension = etree.SubElement(graphics, "dimension")
            dimension.set("x", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][1][0]))
            dimension.set("y", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][1][1]))
    transitions_map = {}
    for transition in petrinet.transitions:
        transitions_map[transition] = transition.name
        trans = etree.SubElement(page, "transition")
        trans.set("id", transition.name)
        trans_name = etree.SubElement(trans, "name")
        trans_text = etree.SubElement(trans_name, "text")
        stochastic_information = etree.SubElement(trans, "toolspecific")
        stochastic_information.set("tool", "StochasticPetriNet")
        stochastic_information.set("version", "0.2")
        distribution_type = etree.SubElement(stochastic_information, "property")
        distribution_type.set("key", "distributionType")
        distribution_type.text = "UNIFORM"
        distribution_parameters = etree.SubElement(stochastic_information, "property")
        distribution_parameters.set("key", "distributionParameters")
        distribution_parameters.text = "0.0;200.0"
        distribution_priority = etree.SubElement(stochastic_information, "property")
        distribution_priority.set("key", "priority")
        distribution_priority.text = "0"
        distribution_invisible = etree.SubElement(stochastic_information, "property")
        distribution_invisible.set("key", "invisible")
        distribution_invisible.text = str(True if transition.label is None else False).lower()
        distribution_weight = etree.SubElement(stochastic_information, "property")
        distribution_weight.set("key", "weight")
        distribution_weight.text = str(format(trans2weight[transition.name], '.10f'))
        if constants.LAYOUT_INFORMATION_PETRI in transition.properties:
            graphics = etree.SubElement(trans, "graphics")
            position = etree.SubElement(graphics, "position")
            position.set("x", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            position.set("y", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][0][1]))
            dimension = etree.SubElement(graphics, "dimension")
            dimension.set("x", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][1][0]))
            dimension.set("y", str(transition.properties[constants.LAYOUT_INFORMATION_PETRI][1][1]))
        if constants.STOCHASTIC_DISTRIBUTION in transition.properties:
            random_variable = transition.properties[constants.STOCHASTIC_DISTRIBUTION]
            stochastic_information = etree.SubElement(trans, "toolspecific")
            stochastic_information.set("tool", "StochasticPetriNet")
            stochastic_information.set("version", "0.2")
            distribution_type = etree.SubElement(stochastic_information, "property")
            distribution_type.set("key", "distributionType")
            distribution_type.text = random_variable.get_distribution_type()
            if not random_variable.get_distribution_type() == "IMMEDIATE":
                distribution_parameters = etree.SubElement(stochastic_information, "property")
                distribution_parameters.set("key", "distributionParameters")
                distribution_parameters.text = random_variable.get_distribution_parameters()
            distribution_priority = etree.SubElement(stochastic_information, "property")
            distribution_priority.set("key", "priority")
            distribution_priority.text = str(random_variable.get_priority())
            distribution_invisible = etree.SubElement(stochastic_information, "property")
            distribution_invisible.set("key", "invisible")
            distribution_invisible.text = str(True if transition.label is None else False).lower()
            distribution_weight = etree.SubElement(stochastic_information, "property")
            distribution_weight.set("key", "weight")
            distribution_weight.text = str(random_variable.get_weight())
        if transition.label is not None:
            trans_text.text = transition.label
        else:
            trans_text.text = transition.name
            tool_specific = etree.SubElement(trans, "toolspecific")
            tool_specific.set("tool", "ProM")
            tool_specific.set("version", "6.4")
            tool_specific.set("activity", "$invisible$")
            tool_specific.set("localNodeID", str(uuid.uuid4()))
        if export_prom5 is True:
            if transition.label is not None:
                prom5_specific = etree.SubElement(trans, "toolspecific")
                prom5_specific.set("tool", "ProM")
                prom5_specific.set("version", "5.2")
                log_event_prom5 = etree.SubElement(prom5_specific, "logevent")
                event_name = transition.label.split("+")[0]
                event_transition = transition.label.split("+")[1] if len(
                    transition.label.split("+")) > 1 else "complete"
                log_event_prom5_name = etree.SubElement(log_event_prom5, "name")
                log_event_prom5_name.text = event_name
                log_event_prom5_type = etree.SubElement(log_event_prom5, "type")
                log_event_prom5_type.text = event_transition
        # specific for data Petri nets
        if petri_properties.TRANS_GUARD in transition.properties:
            trans.set(petri_properties.TRANS_GUARD, transition.properties[petri_properties.TRANS_GUARD])
        if petri_properties.READ_VARIABLE in transition.properties:
            read_variables = transition.properties[petri_properties.READ_VARIABLE]
            for rv in read_variables:
                rv_el = etree.SubElement(trans, petri_properties.READ_VARIABLE)
                rv_el.text = rv
        if petri_properties.WRITE_VARIABLE in transition.properties:
            write_variables = transition.properties[petri_properties.WRITE_VARIABLE]
            for wv in write_variables:
                wv_el = etree.SubElement(trans, petri_properties.WRITE_VARIABLE)
                wv_el.text = wv
    for arc in petrinet.arcs:
        arc_el = etree.SubElement(page, "arc")
        arc_el.set("id", str(hash(arc)))
        if type(arc.source) is PetriNet.Place:
            arc_el.set("source", str(places_map[arc.source]))
            arc_el.set("target", str(transitions_map[arc.target]))
        else:
            arc_el.set("source", str(transitions_map[arc.source]))
            arc_el.set("target", str(places_map[arc.target]))

        if arc.weight > 1:
            inscription = etree.SubElement(arc_el, "inscription")
            arc_weight = etree.SubElement(inscription, "text")
            arc_weight.text = str(arc.weight)

        if isinstance(arc, ResetNet.ResetArc):
            element = etree.SubElement(arc_el, petri_properties.ARCTYPE)
            element_text = etree.SubElement(element, "text")
            element_text.text = petri_properties.RESET_ARC
        elif isinstance(arc, InhibitorNet.InhibitorArc):
            element = etree.SubElement(arc_el, petri_properties.ARCTYPE)
            element_text = etree.SubElement(element, "text")
            element_text.text = petri_properties.INHIBITOR_ARC

        for prop_key in arc.properties:
            if prop_key != petri_properties.ARCTYPE:
                element = etree.SubElement(arc_el, prop_key)
                element_text = etree.SubElement(element, "text")
                element_text.text = str(arc.properties[prop_key])

    if len(final_marking) > 0:
        finalmarkings = etree.SubElement(net, "finalmarkings")
        marking = etree.SubElement(finalmarkings, "marking")

        for place in final_marking:
            placem = etree.SubElement(marking, "place")
            placem.set("idref", place.name)
            placem_text = etree.SubElement(placem, "text")
            placem_text.text = str(final_marking[place])

    # specific for data Petri nets
    if petri_properties.VARIABLES in petrinet.properties:
        variables = etree.SubElement(net, "variables")
        for prop in petrinet.properties[petri_properties.VARIABLES]:
            variable = etree.SubElement(variables, "variable")
            variable.set("type", prop["type"])
            variable_name = etree.SubElement(variable, "name")
            variable_name.text = prop["name"]

    tree = etree.ElementTree(root)

    # Step 4: Write the petri net tree to an XML file
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def export_slpn(output_path, place_in_im_num, place2num, tran2label, tran2ip, tran2op, tran2weight):
    """
       Export a stochastic labeled Petri net (slpn) to an slpn format. The exported slpn file is the input for Ebi
       Parameters
       ----------
       output_path: output path of the slpn file
       marking: :class:`pm4py.entities.petri.petrinet.Marking`
           Marking
       final_marking: :class:`pm4py.entities.petri.petrinet.Marking`
           Final marking (optional)
       export_prom5
           Enables exporting PNML files in a format that is ProM5-friendly
       parameters
           Other parameters of the algorithm

       Returns
       ----------
       tree
           XML tree
       """
    with open(output_path, "w") as file:
        file.write("stochastic labelled Petri net\n")
        file.write("# number of places\n")
        file.write(str(len(place2num)))
        file.write("\n# initial marking")
        for i in range(len(place2num)):  # need adjustment
            if i in place_in_im_num:
                file.write("\n" + str(1))
            else:
                file.write("\n" + str(0))
        file.write("\n# number of transitions\n")
        file.write(str(len(tran2label)))
        idx = 0
        for trans, v in tran2label.items():
            file.write("\n# transition " + str(idx))
            if tran2label[trans] == "silent":
                file.write("\nsilent")
            else:
                file.write("\nlabel " + tran2label[trans])
            file.write("\n# weight")
            number_str = format(tran2weight[trans], '.3f')
            file.write("\n" + number_str)
            file.write("\n# number of input places")
            file.write("\n" + str(len(tran2ip[trans])))
            for i in tran2ip[trans]:
                file.write("\n" + str(i))
            file.write("\n# number of output places")
            file.write("\n" + str(len(tran2op[trans])))
            for k in tran2op[trans]:
                file.write("\n" + str(k))
            idx += 1
    file.close()

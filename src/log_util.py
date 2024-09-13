import pandas as pd
import fractions

from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from typing import Dict, Union, List, Any
from typing import Optional
from pm4py.objects.log.obj import EventStream, EventLog, Trace
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.statistics.variants.log.get import get_variants_from_log_trace_idx, convert_variants_trace_idx_to_trace_obj, \
    Parameters
from pm4py.util import variants_util


def get_variant(import_path, export_path):
    log = xes_importer.apply(import_path)
    variants = variants_filter.get_variants(log)

    new_log = EventLog()
    for variant, traces in variants.items():
        for trace in traces:
            new_trace = Trace()
            for event in trace:
                new_trace.append(event)
            new_log.append(new_trace)
            break
    xes_exporter.apply(new_log, export_path)


def get_stochastic_language(*args, **kwargs) -> Dict[List[str], fractions.Fraction]:
    if isinstance(args[0], EventLog) or isinstance(args[0], EventStream) or isinstance(args[0], pd.DataFrame):
        from pm4py.objects.conversion.log import converter as log_converter
        log = log_converter.apply(args[0])
        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)
        vars = get_variants(log)
        vars = {variants_util.get_activities_from_variant(x): len(y) for x, y in vars.items()}

        all_values_sum = sum(vars.values())
        for x in vars:
            vars[x] = fractions.Fraction(vars[x], all_values_sum)
            # vars[x] = vars[x] / all_values_sum
        return vars


def get_trace_weight_dict(*args, **kwargs) -> Dict[List[str], fractions.Fraction]:
    if isinstance(args[0], EventLog) or isinstance(args[0], EventStream) or isinstance(args[0], pd.DataFrame):
        from pm4py.objects.conversion.log import converter as log_converter
        log = log_converter.apply(args[0])
        log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG)
        vars = get_variants(log)
        vars = {variants_util.get_activities_from_variant(x): len(y) for x, y in vars.items()}

        all_values_sum = sum(vars.values())
        for x in vars:

            vars[x] = fractions.Fraction(vars[x], all_values_sum)
        return vars

def get_variants(log: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Union[
    Dict[List[str], List[Trace]], Dict[str, List[Trace]]]:
    """
    Gets a dictionary whose key is the variant and as value there
    is the list of traces that share the variant

    Parameters
    ----------
    log
        Trace log
    parameters of the algorithm, including:
            Parameters.ACTIVITY_KEY -> Attribute identifying the activity in the log

    Returns
    ----------
    variant
        Dictionary with variant as the key and the list of traces as the value
    """
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    variants_trace_idx = get_variants_from_log_trace_idx(log, parameters=parameters)

    all_var = convert_variants_trace_idx_to_trace_obj(log, variants_trace_idx)

    return all_var


def export_stochastic_language(import_path, export_path):
    log = xes_importer.apply(import_path)
    variants = get_stochastic_language(log)

    with open(export_path, "w") as file:
        file.write("finite stochastic language\n")
        file.write("# number of traces\n")
        file.write(str(len(variants)))

        i = 0
        for key, val in variants.items():
            file.write("\n# trace " + str(i))
            file.write("\n# weight")
            file.write("\n" + str(val.numerator) + "/" + str(val.denominator))
            file.write("\n# number of events")
            file.write("\n" + str(len(key)))
            for j in range(len(key)):
                file.write("\n" + key[j])
            i += 1
    file.close()


# get a main function
if __name__ == '__main__':
    # export_stochastic_language("../data/road/rtf_2000.xes", "../data/road/rtf2000.slang")

    get_variant("../data/prAm6/prAm6.xes", "../data/prAm6/prAm6_variants.xes")

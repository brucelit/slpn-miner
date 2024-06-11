def read_slang_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content


def parse_slang_file(slang_content):
    """
    Parse the slang content and return the traces and their probability
    :param slang_content:
    :return:
    """
    traces = {}
    lines = slang_content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("# trace"):
            trace_number = int(line.split()[2])
            i += 1  # Move to the weight line

            weight_line = lines[i].strip()
            assert weight_line == "# weight"
            i += 1  # Move to the actual weight

            weight = lines[i].strip()
            i += 1  # Move to the number of events line

            number_of_events_line = lines[i].strip()
            assert number_of_events_line == "# number of events"
            i += 1  # Move to the events

            number_of_events = int(lines[i].strip())
            i += 1  # Move to the first event

            events = []
            for _ in range(number_of_events):
                events.append(lines[i].strip())
                i += 1

            traces[str(events)] = weight

        else:
            i += 1

    return traces


def main():
    file_path = 'data/rtf_2000.slang'
    slang_content = read_slang_file(file_path)
    traces = parse_slang_file(slang_content)

    for trace,weight in traces.items():
        print(f'{trace}: Weight = {weight}')


if __name__ == "__main__":
    main()

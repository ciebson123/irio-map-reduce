from collections import defaultdict
from pathlib import Path
from typing import List, DefaultDict


def _update_kval_from_file(kvals: DefaultDict[str, List[int]], path: Path) -> None:
    with open(path, "r") as input_file:
        for line in input_file:
            key_val = line.strip().split()
            kvals[key_val[0]].append(int(key_val[1]))


def process_reduce_task(intermediate_paths: List[Path], output_path: Path) -> None:
    """
    Processes the reduce task. Its input is split into num_mapper files of format

    "word <count of occurences of word>"

    For now, it represents just a simple, predetermined word counting functionality.

    It shall create a single file (under output_path) having n lines of the same format as input, but n is the number
    of **unique** words/keys.

    Simplifying assumption

    * inputs can fit in memory

    :param intermediate_paths:
    :param output_path:
    :return:
    """
    kvals = defaultdict(list)
    for intermediate_path in intermediate_paths:
        _update_kval_from_file(kvals, intermediate_path)

    # reduce
    result = {}
    for key, values in kvals.items():
        result[key] = sum(values)

    # save
    with output_path.open("w") as output_file:
        for key, value in result.items():
            output_file.write(f"{key} {value}\n")

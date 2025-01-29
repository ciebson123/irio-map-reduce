import sys
from typing import List, DefaultDict
from pathlib import Path
from collections import defaultdict


def _update_kval_from_file(kvals: DefaultDict[str, List[int]], path: Path) -> None:
    with open(path, "r") as input_file:
        for line in input_file:
            key_val = line.strip().split()
            kvals[key_val[0]].append(int(key_val[1]))


def main():
    """
    Example implementation of a reducer for a word-counting mapper.

    Its input is split into num_mapper files of format

    "word <count of occurences of word>"

    It shall create a single file (under output_path) having n lines of the same format as input, but n is the number
    of **unique** words/keys.
    """
    args = sys.argv[1:]

    if not args or len(args) < 2:
        print("No arguments received. Please provide some arguments.")
        return

    output_path = args[1]
    intermediate_paths = args[2:]

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


if __name__ == "__main__":
    main()

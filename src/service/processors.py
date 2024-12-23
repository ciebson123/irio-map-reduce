from collections import Counter
from pathlib import Path
from typing import List

from xxhash import xxh32_intdigest


def _get_partition_idx(word: str, num_partitions: int) -> int:
    return xxh32_intdigest(word) % num_partitions


def process_map_task(input_path: Path, num_partitions: int, output_dir: Path) -> List[Path]:
    """
    Processes the map task. Since it's output is split into num_partitions files, it
    returns the output paths in a list of paths (in ascending order with regard to the partition num).

    Each of the num_partitions output files will have n lines of form

    "word <count of occurences of word>"

    where i-th file will contain words such that xxh32_intdigest(word) % num_partitions == i
    and n is the number of words

    For now, it represents just a simple, predetermined word counting functionality.

    Simplifying assumption

    * a single line of the file can fit in memory
    * output dir must be empty at the start of this function

    :param input_path:
    :param num_partitions:
    :param output_dir:
    :return: list of paths with intermediate outputs split into num_partitions.
    """
    if num_partitions <= 0:
        raise ValueError("num_partitions must be greater than zero")

    counter = Counter()

    with open(input_path, "r") as input_file:
        for line in input_file:
            for word in line.strip().split():
                counter[word] += 1

    for word, count in counter.items():
        partition_num = _get_partition_idx(word, num_partitions)
        with output_dir.joinpath(str(partition_num)).open("a") as output_file:
            output_file.write(f"{word} {count}\n")

    return [output_dir.joinpath(str(partition_num)) for partition_num in range(num_partitions)]


def process_reduce_task():
    # Placeholder
    pass

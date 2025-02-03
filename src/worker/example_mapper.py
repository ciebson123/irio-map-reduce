import sys
from xxhash import xxh32_intdigest
from collections import Counter
from pathlib import Path
import logging


def _get_partition_idx(word: str, num_partitions: int) -> int:
    return xxh32_intdigest(word) % num_partitions


def main():
    """
    Example implementation of a mapper that counts occurences of each word in a file.

    Each of the num_partitions output files will have n lines of form

    "word <count of occurences of word>"

    where i-th file will contain words such that xxh32_intdigest(word) % num_partitions == i
    and n is the number of words.

    """
    args = sys.argv[1:]

    if not args or len(args) < 3:
        logging.error("Did not receive enough arguments")
        sys.exit(1)

    input_path = Path(args[0])
    num_partitions = int(args[1])
    output_dir = Path(args[2])

    counter = Counter()

    with open(input_path, "r") as input_file:
        for line in input_file:
            for word in line.strip().split():
                counter[word] += 1

    # if some partition ends up empty, we still want the file to exist
    for partition_num in range(num_partitions):
        with output_dir.joinpath(str(partition_num)).open("a"):
            pass

    for word, count in counter.items():
        partition_num = _get_partition_idx(word, num_partitions)
        with output_dir.joinpath(str(partition_num)).open("a") as output_file:
            output_file.write(f"{word} {count}\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Set the log format
        handlers=[logging.StreamHandler(sys.stdout)],  # Add a StreamHandler for stdout
    )
    logger = logging.getLogger()
    main()

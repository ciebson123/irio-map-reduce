import sys
from xxhash import xxh32_intdigest
from collections import Counter


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
        print("No arguments received. Please provide some arguments.")
        return

    input_path = args[1]
    num_partitions = args[2]
    output_dir = args[3]

    counter = Counter()

    with open(input_path, "r") as input_file:
        for line in input_file:
            for word in line.strip().split():
                counter[word] += 1

    for word, count in counter.items():
        partition_num = _get_partition_idx(word, num_partitions)
        with output_dir.joinpath(str(partition_num)).open("a") as output_file:
            output_file.write(f"{word} {count}\n")


if __name__ == "__main__":
    main()

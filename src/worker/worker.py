from collections import Counter, defaultdict
from pathlib import Path
from typing import List, DefaultDict

import grpc
from xxhash import xxh32_intdigest

from src.generated_files.worker_pb2 import MapResponse, ReduceResponse
from src.generated_files.worker_pb2_grpc import WorkerServicer


def _get_partition_idx(word: str, num_partitions: int) -> int:
    return xxh32_intdigest(word) % num_partitions

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


def process_map_task(
    input_path: Path, num_partitions: int, output_dir: Path
) -> List[Path]:
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

    return [
        output_dir.joinpath(str(partition_num))
        for partition_num in range(num_partitions)
    ]


class Worker(WorkerServicer):
    def Map(self, map_task, context):
        try:
            partition_paths = process_map_task(
                Path(map_task.file_path),
                map_task.num_partitions,
                Path(map_task.output_dir),
            )
            res = MapResponse(
                partition_paths=[p.absolute().as_posix() for p in partition_paths]
            )
            return res
        except ValueError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
            
    def Reduce(self, reduce_task, context):
        process_reduce_task(
            [Path(p) for p in reduce_task.partition_paths],
            Path(reduce_task.output_path),
        )

        return ReduceResponse()

from pathlib import Path
import subprocess
from typing import List

import grpc

from src.generated_files.worker_pb2 import MapResponse, ReduceResponse
from src.generated_files.worker_pb2_grpc import WorkerServicer


def process_reduce_task(
    intermediate_paths: List[Path], output_path: Path, reducer_path: Path
) -> None:
    """
    Invokes a subprocess that performs the reduce functionality.

    The reducer program receives output_path and a sequence of intermediate_paths.
    It is expected to create a single file (under output_path).

    Simplifying assumption:
    * inputs can fit in memory

    :param intermediate_paths:
    :param output_path:
    :param reducer_path: path to Python file that contains the reducer code
    :return:
    """
    subprocess.run(
        [
            "python3",
            reducer_path.as_posix(),
            output_path.as_posix(),
            *[p.as_posix() for p in intermediate_paths],
        ],
        check=True,
    )


def process_map_task(
    input_path: Path, num_partitions: int, output_dir: Path, mapper_path: Path
) -> List[Path]:
    """
    Invokes a subprocess that performs the map functionality.

    The mapper program receives three arguments: input_path, num_partitions and output_dir
    It is expected to split its output into num_partitions files placed under output_dir directory.

    Simplifying assumptions:
    * a single line of the file can fit in memory
    * output dir must be empty at the start of this function

    :param input_path:
    :param num_partitions:
    :param output_dir:
    :param mapper_code: path to Python file that contains the mapper code
    :return: list of paths with intermediate outputs split into num_partitions.
    """
    if num_partitions <= 0:
        raise ValueError("num_partitions must be greater than zero")

    subprocess.run(
        [
            "python3",
            mapper_path.as_posix(),
            input_path.as_posix(),
            str(num_partitions),
            output_dir.as_posix(),
        ],
        check=True,
    )

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
                Path(map_task.mapper_path),
            )
            res = MapResponse(
                partition_paths=[p.absolute().as_posix() for p in partition_paths]
            )
            return res
        except ValueError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except subprocess.CalledProcessError:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Mapper program has exited with an error.",
            )

    def Reduce(self, reduce_task, context):
        try:
            process_reduce_task(
                [Path(p) for p in reduce_task.partition_paths],
                Path(reduce_task.output_path),
                Path(reduce_task.reducer_path),
            )
        except subprocess.CalledProcessError:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Reducer program has exited with an error.",
            )

        return ReduceResponse()

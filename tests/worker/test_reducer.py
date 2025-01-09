from collections import defaultdict
from pathlib import Path
from typing import Tuple, List

import grpc
import pytest

from src.generated_files.reducer_pb2 import ReduceTask
from src.generated_files.reducer_pb2_grpc import ReducerStub
from src.worker.reducer import process_reduce_task

SPLIT_INTERMEDIATE_KVS = [
    [("key1", 3), ("key2", 4), ("key3", 5), ("key4", 6), ("key1", 7)],
    [("key2", 4), ("key3", 7)],
]


@pytest.fixture
def simple_file_paths(tmp_path):
    tmp_1_file_path = tmp_path / "tmp1"
    with open(tmp_1_file_path, mode="w") as tmp:
        tmp.write("".join(f"{key} {val}\n" for (key, val) in SPLIT_INTERMEDIATE_KVS[0]))

    tmp_2_file_path = tmp_path / "tmp2"
    with open(tmp_2_file_path, mode="w") as tmp:
        tmp.write("".join(f"{key} {val}\n" for (key, val) in SPLIT_INTERMEDIATE_KVS[1]))

    return tmp_1_file_path, tmp_2_file_path


@pytest.fixture(scope="module")
def reducer_client(worker_server_port):
    with grpc.insecure_channel("localhost:" + str(worker_server_port)) as channel:
        stub = ReducerStub(channel)
        yield stub


def _get_expected_result_kval(intermediate_kvs: List[List[Tuple[str, int]]]):
    expected_result_kval = defaultdict(int)
    for split in intermediate_kvs:
        for key, val in split:
            expected_result_kval[key] += val

    return expected_result_kval


def _read_output_kval(output_path: Path):
    output_result_kval = {}
    with open(output_path, mode="r") as output_file:
        for line in output_file:
            kval = line.strip().split()
            output_result_kval[kval[0]] = int(kval[1])
    return output_result_kval


def test_process_reduce_produces_correct_output_on_simple_file(
    simple_file_paths: Tuple[Path, Path], tmp_path: Path
):
    out_path = tmp_path / "res"
    expected_result_kval = _get_expected_result_kval(SPLIT_INTERMEDIATE_KVS)

    process_reduce_task([*simple_file_paths], out_path)

    output_result_kval = _read_output_kval(out_path)

    assert output_result_kval == expected_result_kval


def test_grpc_reducer_servicer_produces_files(
    reducer_client: ReducerStub, tmp_path: Path, simple_file_paths: Tuple[Path, Path]
):
    out_path = tmp_path / "grpc_reducer_produces_files"
    expected_result_kval = _get_expected_result_kval(SPLIT_INTERMEDIATE_KVS)

    reduce_task = ReduceTask(
        partition_paths=[p.absolute().as_posix() for p in simple_file_paths],
        output_path=out_path.absolute().as_posix(),
    )
    reducer_client.Reduce(reduce_task)

    output_result_kval = _read_output_kval(out_path)

    assert output_result_kval == expected_result_kval

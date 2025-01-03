from collections import Counter
from pathlib import Path
from typing import List

import grpc
import pytest
from xxhash import xxh32_intdigest

from src.generated_files.mapper_pb2 import MapTask
from src.generated_files.mapper_pb2_grpc import MapperStub
from src.worker.mapper import process_map_task

SIMPLE_WORDS = ["foo", "poo", "kuku", "loo", "loo", "monty", "python", "foo", "foo", "aha", "bizz", "bizz"]


@pytest.fixture
def simple_file_path(tmp_path):
    tmp_file_path = tmp_path / "tmp"
    with open(tmp_path / "tmp", mode="w") as tmp:
        middle = len(SIMPLE_WORDS) // 2
        tmp.write(" ".join(SIMPLE_WORDS[:middle]))
        tmp.write("\n")
        tmp.write(" ".join(SIMPLE_WORDS[middle:]))

    return tmp_file_path


@pytest.fixture(scope="module")
def mapper_client(worker_server_port):
    with grpc.insecure_channel("localhost:" + str(worker_server_port)) as channel:
        stub = MapperStub(channel)
        yield stub


def _get_kv_from_line(line: str):
    line = line.strip().split()
    assert len(line) == 2
    return line[0], int(line[1])


@pytest.mark.parametrize("num_partitions", [-1, 0])
def test_given_invalid_num_partitions_process_map_task_raises(num_partitions: int, simple_file_path: Path,
                                                              tmp_path: Path):
    with pytest.raises(ValueError):
        process_map_task(simple_file_path, num_partitions, tmp_path)


def _get_expected_partition_lines(num_partitions: int, word_list: List[str]):
    simple_words_counts = Counter(word_list)
    expected_partition_lines = [[], []]
    for word, count in simple_words_counts.items():
        expected_partition_lines[xxh32_intdigest(word) % num_partitions].append(f"{word} {count}\n")
    return expected_partition_lines


def test_map_process_produces_correct_output_on_simple_input(simple_file_path: Path, tmp_path: Path):
    num_partitions = 2
    expected_partition_lines = _get_expected_partition_lines(num_partitions, SIMPLE_WORDS)

    output_paths = process_map_task(simple_file_path, num_partitions, tmp_path)

    for idx, path in enumerate(output_paths):
        with open(path, "r") as single_partition_file:
            assert sorted(single_partition_file.readlines()) == sorted(expected_partition_lines[idx])


def test_grpc_mapper_servicer_produces_files(mapper_client: MapperStub, tmp_path: Path, simple_file_path: Path):
    tmp_dir_path = tmp_path / "mapper_servicer_produces_files"
    tmp_dir_path.mkdir()

    num_partitions = 2
    expected_partition_lines = _get_expected_partition_lines(num_partitions, SIMPLE_WORDS)

    map_task = MapTask(
        file_path=simple_file_path.absolute().as_posix(),
        num_partitions=num_partitions,
        output_dir=tmp_dir_path.absolute().as_posix(),
    )

    response = mapper_client.Map(map_task)  # if status code not ok then this will throw

    for idx, path in enumerate(response.partition_paths):
        with open(path, "r") as single_partition_file:
            assert sorted(single_partition_file.readlines()) == sorted(expected_partition_lines[idx])


def test_grpc_mapper_servicer_handles_invalid_num_partitions(mapper_client: MapperStub, tmp_path: Path,
                                                             simple_file_path: Path):
    tmp_dir_path = tmp_path / "mapper_servicer_handles_invalid_num_partitions"
    tmp_dir_path.mkdir()

    map_task = MapTask(
        file_path=simple_file_path.absolute().as_posix(),
        num_partitions=0,
        output_dir=tmp_dir_path.absolute().as_posix(),
    )

    with pytest.raises(grpc.RpcError) as grpc_error:
        mapper_client.Map(map_task)

    assert grpc_error.value.code() == grpc.StatusCode.INVALID_ARGUMENT

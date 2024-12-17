from pathlib import Path

import pytest
from xxhash import xxh32_intdigest

from src.service.processors import process_map_task

SIMPLE_WORDS = ["foo", "poo", "kuku", "loo", "loo"]


@pytest.fixture
def simple_file_path(tmp_path):
    tmp_file_path = tmp_path / "tmp"
    with open(tmp_path / "tmp", mode="w") as tmp:
        tmp.write(" ".join(SIMPLE_WORDS))

    return tmp_file_path


def _get_kv_from_line(line: str):
    line = line.strip().split()
    assert len(line) == 2
    return line[0], int(line[1])


@pytest.mark.parametrize("num_partitions", [-1, 0])
def test_given_invalid_num_partitions_process_map_task_raises(num_partitions: int, simple_file_path: Path,
                                                              tmp_path: Path):
    with pytest.raises(ValueError):
        process_map_task(simple_file_path, num_partitions, tmp_path)


def test_map_process_produces_correct_output_on_simple_input(simple_file_path: Path, tmp_path: Path):
    num_partitions = 2
    expected_partition_lines = [[], []]
    for word in SIMPLE_WORDS:
        expected_partition_lines[xxh32_intdigest(word) % num_partitions].append(f"{word} 1\n")

    output_paths = process_map_task(simple_file_path, num_partitions, tmp_path)

    for idx, path in enumerate(output_paths):
        with open(path, "r") as single_partition_file:
            assert sorted(single_partition_file.readlines()) == sorted(expected_partition_lines[idx])

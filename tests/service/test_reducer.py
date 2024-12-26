from collections import defaultdict
from pathlib import Path
from typing import Tuple

import pytest

from src.service.reducer import process_reduce_task

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


def test_process_reduce_produces_correct_output_on_simple_file(simple_file_paths: Tuple[Path, Path], tmp_path: Path):
    out_path = tmp_path / "res"
    process_reduce_task([*simple_file_paths], out_path)
    expected_result_kval = defaultdict(int)
    for split in SPLIT_INTERMEDIATE_KVS:
        for key, val in split:
            expected_result_kval[key] += val

    output_result_kval = {}
    with open(out_path, mode="r") as output_file:
        for line in output_file:
            kval = line.strip().split()
            output_result_kval[kval[0]] = int(kval[1])

    assert output_result_kval == expected_result_kval

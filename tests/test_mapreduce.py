from pathlib import Path
from typing import List

import pytest

from src.generated_files.master_pb2 import (
    RegisterServiceMes,
    MapReduceRequest,
    MapReduceResponse,
)
from src.generated_files.master_pb2_grpc import MasterStub
from src.worker.server import build_worker_server
from tests.utils import read_mapreduce_outputs, count_words

NUM_WORKERS = 16
TEST_INPUT_DIR = Path(__file__).parent / "test_files" / "input"
MAPPER_PATH = Path("src/worker/example_mapper.py").absolute()
REDUCER_PATH = Path("src/worker/example_reducer.py").absolute()


@pytest.fixture
def worker_ports():
    worker_servers = [build_worker_server() for _ in range(NUM_WORKERS)]
    ports = [server.add_insecure_port("[::]:0") for server in worker_servers]
    for server in worker_servers:
        server.start()

    yield ports

    for server in worker_servers:
        server.stop(grace=None)


def _register_workers_and_send_request(
    worker_ports: List[int], client: MasterStub, num_partitions: int, input_dir: Path
) -> MapReduceResponse:
    for worker_port in worker_ports:
        client.RegisterService(
            RegisterServiceMes(service_address="localhost", service_port=worker_port)
        )

    return client.MapReduce(
        MapReduceRequest(
            input_dir=input_dir.absolute().as_posix(),
            num_partitions=num_partitions,
            mapper_path=MAPPER_PATH.as_posix(),
            reducer_path=REDUCER_PATH.as_posix(),
        ),
    )


@pytest.mark.parametrize("num_partitions", [1, 2, 4, 8])
def test_big_files_multiple_workers(
    worker_ports: List[int], master_client: MasterStub, num_partitions: int
):
    response = _register_workers_and_send_request(
        worker_ports, master_client, num_partitions, TEST_INPUT_DIR
    )

    assert read_mapreduce_outputs(Path(response.output_dir)) == count_words(
        TEST_INPUT_DIR
    )


def test_when_given_file_with_more_partitions_then_actual_buckets_then_doesnt_freeze(
    worker_ports: List[int], master_client: MasterStub, tmp_path: Path
):
    with open(tmp_path / "input.txt", "w") as f:
        f.write("asdf bcda")

    response = _register_workers_and_send_request(
        worker_ports, master_client, 10, tmp_path
    )

    assert read_mapreduce_outputs(Path(response.output_dir)) == count_words(tmp_path)


def test_when_given_files_with_more_partitions_then_actual_buckets_then_doesnt_freeze(
    worker_ports: List[int], master_client: MasterStub, tmp_path: Path
):
    with open(tmp_path / "input_1.txt", "w") as f:
        f.write("asdf bcda")
    with open(tmp_path / "input_2.txt", "w") as f:
        f.write("asdf")
    with open(tmp_path / "input_2.txt", "w") as f:
        f.write("bcda")

    response = _register_workers_and_send_request(
        worker_ports, master_client, 10, tmp_path
    )

    assert read_mapreduce_outputs(Path(response.output_dir)) == count_words(tmp_path)

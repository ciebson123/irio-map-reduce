from pathlib import Path
from typing import List

import pytest

from src.generated_files.master_pb2 import RegisterServiceMes, MapReduceRequest
from src.generated_files.master_pb2_grpc import MasterStub
from src.worker.server import build_worker_server
from tests.utils import read_mapreduce_outputs, count_words

NUM_WORKERS = 16
TEST_INPUT_DIR = Path(__file__).parent / "test_files" / "input"


@pytest.fixture
def worker_ports():
    worker_servers = [build_worker_server() for _ in range(NUM_WORKERS)]
    ports = [server.add_insecure_port("[::]:0") for server in worker_servers]
    for server in worker_servers:
        server.start()

    yield ports

    for server in worker_servers:
        server.stop(grace=None)


@pytest.mark.parametrize("num_partitions", [1, 2, 4, 8])
def test_big_files_multiple_workers(
    worker_ports: List[int], master_client: MasterStub, num_partitions: int
):
    for worker_port in worker_ports:
        master_client.RegisterService(
            RegisterServiceMes(service_address="localhost", service_port=worker_port)
        )

    response = master_client.MapReduce(
        MapReduceRequest(
            input_dir=TEST_INPUT_DIR.absolute().as_posix(),
            num_partitions=num_partitions,
        ),
    )

    assert read_mapreduce_outputs(Path(response.output_dir)) == count_words(
        TEST_INPUT_DIR
    )

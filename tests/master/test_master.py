from pathlib import Path

import pytest

from src.generated_files.master_pb2 import RegisterServiceMes, MapReduceRequest
from src.generated_files.master_pb2_grpc import MasterStub
from tests.utils import read_mapreduce_outputs, count_words


@pytest.fixture
def simple_input_dir(tmp_path: Path):
    tmps = [tmp_path / "input1", tmp_path / "input2", tmp_path / "input3"]
    contents = [
        "hello i am very excited to see\n how mapreduce actually performs",
        "it would be a shame if it turns out that it does not work",
        "This one is just to repeat some words\n i very see mapreduce mapreduce work not not it it it it shame",
    ]

    for tmp, content in zip(tmps, contents):
        with open(tmp, mode="w") as f:
            f.write(content)

    return tmp_path


def test_master_returns_when_worker_registers(master_client: MasterStub):
    req = RegisterServiceMes(service_address="localhost", service_port=1234)
    master_client.RegisterService(req)


def test_master_performs_mapreduce_with_one_worker(
    master_client: MasterStub,
    worker_server_port: int,
    master_server_port,
    simple_input_dir: Path,
):
    # register the client
    reg_req = RegisterServiceMes(
        service_address="localhost", service_port=worker_server_port
    )
    master_client.RegisterService(reg_req)
    mapreduce_req = MapReduceRequest(
        input_dir=simple_input_dir.absolute().as_posix(), num_partitions=2
    )
    response = master_client.MapReduce(mapreduce_req)

    assert read_mapreduce_outputs(Path(response.output_dir)) == count_words(
        simple_input_dir
    )

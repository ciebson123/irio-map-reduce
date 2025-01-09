import asyncio
import threading
from pathlib import Path
from threading import Event

import grpc
import pytest
from _pytest.tmpdir import TempPathFactory

from src.master.server import serve_test
from src.generated_files.master_pb2_grpc import MasterStub
from src.worker.server import build_worker_server


@pytest.fixture(scope="session")
def worker_server_port() -> int:
    server = build_worker_server()
    port = server.add_insecure_port("[::]:0")
    server.start()
    yield port
    server.stop(grace=None)


@pytest.fixture
def master_server_port(tmp_path_factory: TempPathFactory) -> (int, Path):
    shared_dir = tmp_path_factory.mktemp("shared", numbered=True)

    port_filled = Event()
    port_placeholder = [0]

    server_thread = threading.Thread(
        target=asyncio.run,
        args=(serve_test(shared_dir, (port_filled, port_placeholder)),),
        daemon=True,
    )
    server_thread.start()
    port_filled.wait()

    yield port_placeholder[0]


@pytest.fixture
def master_client(master_server_port):
    port = master_server_port
    with grpc.insecure_channel("localhost:" + str(port)) as channel:
        stub = MasterStub(channel)
        yield stub

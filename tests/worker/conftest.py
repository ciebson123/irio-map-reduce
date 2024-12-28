import pytest

from src.worker.server import build_worker_server


@pytest.fixture(scope='session')
def worker_server_port() -> int:
    server = build_worker_server()
    port = server.add_insecure_port('[::]:0')
    server.start()
    yield port
    server.stop(grace=None)

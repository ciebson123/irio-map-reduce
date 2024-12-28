import grpc
import pytest
from grpc_health.v1 import health_pb2
from grpc_health.v1.health_pb2_grpc import HealthStub


@pytest.fixture(scope="module")
def health_client(worker_server_port):
    with grpc.insecure_channel("localhost:" + str(worker_server_port)) as channel:
        stub = HealthStub(channel)
        yield stub


def test_health_check_call_returns_valid_response(health_client: HealthStub):
    request = health_pb2.HealthCheckRequest()
    response = health_client.Check(request)
    assert response.status == health_pb2.HealthCheckResponse.SERVING

import logging
from concurrent import futures
import os

import grpc
from grpc._server import _Server

from src.generated_files import reducer_pb2_grpc, mapper_pb2_grpc
from src.generated_files.master_pb2_grpc import MasterStub
from src.generated_files.master_pb2 import RegisterServiceMes
from src.worker.mapper import Mapper
from src.worker.reducer import Reducer


def build_worker_server() -> _Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    mapper_pb2_grpc.add_MapperServicer_to_server(Mapper(), server)
    reducer_pb2_grpc.add_ReducerServicer_to_server(Reducer(), server)

    return server


def register_with_master(port: int):
    my_ip = os.environ.get("MY_POD_IP")
    with grpc.insecure_channel("master-service:8080") as channel:
        register_message = RegisterServiceMes(service_address=my_ip, service_port=port)
        MasterStub(channel).RegisterService(register_message)
    logging.info("Registered with master")


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.info("Starting worker server")
    serv = build_worker_server()
    port = 8000
    serv.add_insecure_port("[::]:" + str(port))
    serv.start()
    logging.info("Server started, listening on " + str(port))
    register_with_master(port=port)
    serv.wait_for_termination()

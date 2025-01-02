import logging
from concurrent import futures

import grpc
from grpc._server import _Server

from src.generated_files import reducer_pb2_grpc, mapper_pb2_grpc
from src.worker.mapper import Mapper
from src.worker.reducer import Reducer


def build_worker_server() -> _Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    mapper_pb2_grpc.add_MapperServicer_to_server(Mapper(), server)
    reducer_pb2_grpc.add_ReducerServicer_to_server(Reducer(), server)

    return server


if __name__ == "__main__":
    logging.basicConfig()
    serv = build_worker_server()
    port = 8000

    serv.add_insecure_port("[::]:" + str(port))
    serv.start()
    print("Server started, listening on " + str(port))
    serv.wait_for_termination()

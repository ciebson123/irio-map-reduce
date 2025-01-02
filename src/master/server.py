import asyncio
import logging
import os
from pathlib import Path
from threading import Event
from typing import Tuple, List

import grpc

from src.generated_files import master_pb2_grpc
from src.master.master import Master


def build_master_server(shared_dir: Path) -> grpc.Server:
    server = grpc.aio.server()
    master_pb2_grpc.add_MasterServicer_to_server(Master(shared_dir), server)

    return server


async def serve_prod(
        shared_dir: Path,
        port: int = 8000,
) -> None:
    server = build_master_server(shared_dir)
    server.add_insecure_port("[::]:" + str(port))

    await server.start()
    logging.info("Prod server started, listening on " + str(port))
    await server.wait_for_termination()

async def serve_test(
        shared_dir: Path,
        return_port_placeholder: Tuple[Event, List],
):
    serv = build_master_server(shared_dir)

    # this is a dirty way to retrieve the port from the async loop mixing threading and async
    port = serv.add_insecure_port("[::]:0")
    ev, port_placeholder = return_port_placeholder
    port_placeholder[0] = port
    # notify that the port was set
    ev.set()

    await serv.start()
    logging.info("Test server started, listening on " + str(port))
    await serv.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    s_dir = Path(os.environ.get("SHARED_DIR"))
    asyncio.run(serve_prod(s_dir))

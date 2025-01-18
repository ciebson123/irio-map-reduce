import asyncio
import logging
import os
from pathlib import Path

import grpc

from src.generated_files import upload_pb2_grpc
from src.upload.upload import Upload


def build_upload_server(shared_dir: Path) -> grpc.Server:
    server = grpc.aio.server()
    upload_pb2_grpc.add_UploadServicer_to_server(Upload(shared_dir), server)

    return server


async def serve(
    shared_dir: Path,
    port: int = 8000,
) -> None:
    server = build_upload_server(shared_dir)
    server.add_insecure_port("[::]:" + str(port))

    await server.start()
    logging.info("Upload server started, listening on " + str(port))
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.info("Starting upload server")
    s_dir = Path(os.environ.get("SHARED_DIR"))
    asyncio.run(serve(s_dir))

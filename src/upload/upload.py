import logging
import os
import requests

import grpc
from google.protobuf.empty_pb2 import Empty
from src.generated_files.upload_pb2 import UploadRequest
from pathlib import Path


class Upload:
    def __init__(self, shared_dir: Path):
        self.shared_dir = shared_dir

    async def DoUpload(self, request: UploadRequest, context: grpc.aio.ServicerContext):
        logging.info(
            "Received Upload request.\nLink: %s",
            request.link,
        )
        try:
            # Ensure the directory exists (not likely to fail)
            os.makedirs(self.shared_dir, exist_ok=True)

            filename = request.link.split("/")[-1]

            file_path = os.path.join(self.shared_dir, filename)

            response = requests.get(request.link, stream=True)
            response.raise_for_status()  # Raise HTTPError for bad responses

            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            logging.info(f"File downloaded successfully: {file_path}")
            return Empty()

        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading file: {e}")
            return Empty()

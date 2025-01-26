from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Query
from fastapi.responses import FileResponse
import logging
import os
import grpc
import zipfile
import uuid
from pathlib import Path
import shutil
from src.generated_files.master_pb2 import MapReduceRequest, MapReduceResponse
from src.generated_files.master_pb2_grpc import MasterStub
import subprocess

app = FastAPI()

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB

def cleanup(temp_dir: Path):
    """Remove temporary directory and its contents."""
    shutil.rmtree(temp_dir, ignore_errors=True)
    logging.info(f"Cleaned up temporary directory: {temp_dir}")


def split_large_files(directory: Path):
    """Split files larger than CHUNK_SIZE into smaller parts on newlines."""
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.stat().st_size > CHUNK_SIZE:
            logging.info(f"Splitting large file: {file_path}")
            try:
                # Generate prefix for split files
                prefix = file_path.parent / f"{file_path.stem}_part_"
                
                # Build split command
                cmd = [
                    "split",
                    "-C", str(CHUNK_SIZE),  # Maintain line integrity
                    "--numeric-suffixes=1",
                    "--suffix-length=3",
                    "--additional-suffix", file_path.suffix,
                    str(file_path),
                    str(prefix)
                ]
                
                # Execute command
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Remove original file if split succeeded
                file_path.unlink()
                logging.info(f"Split successful: {result.stderr}")

            except subprocess.CalledProcessError as e:
                logging.error(f"Split failed for {file_path}: {e.stderr}")
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")

@app.post("/", response_class=FileResponse)
async def map_reduce_request(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="ZIP file containing input data"),
    num_partitions: int = Query(
        5, ge=1, description="Number of partitions for MapReduce (min 1)"
    ),
):
    try:
        # Create unique temporary directory
        unique_id = uuid.uuid4().hex
        temp_dir = Path(app.shared_dir) / unique_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        # Schedule cleanup after response is sent
        background_tasks.add_task(cleanup, temp_dir)

        logging.info(f"Created temporary directory: {temp_dir}")

        # Save uploaded ZIP file
        input_zip_path = temp_dir / "input.zip"
        with open(input_zip_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logging.info(f"Saved uploaded ZIP to: {input_zip_path}")

        # Unzip the file
        input_dir = temp_dir / "input"
        input_dir.mkdir()
        with zipfile.ZipFile(input_zip_path, "r") as zip_ref:
            zip_ref.extractall(input_dir)
        logging.info(f"Unzipped to: {input_dir}")

        # List all items in the input directory
        entries = list(input_dir.iterdir())

        # Check if there's exactly one directory in the extracted contents
        if len(entries) == 1 and entries[0].is_dir():
            actual_input_dir = entries[0]  # Use the subdirectory
            logging.info(f"Using subdirectory as input: {actual_input_dir}")
        else:
            actual_input_dir = input_dir  # Use the root directory
            logging.info(f"Using root directory as input: {actual_input_dir}")
            
        # Split large files
        split_large_files(actual_input_dir)

        # Call MapReduce service
        with grpc.insecure_channel("master-service:8080") as channel:
            stub = MasterStub(channel)
            request = MapReduceRequest(
                input_dir=str(actual_input_dir),
                num_partitions=num_partitions,
                work_dir=str(temp_dir),
            )
            response: MapReduceResponse = stub.MapReduce(request)
            output_dir = Path(response.output_dir)
            logging.info(f"Received output directory: {output_dir}")

            # Validate output directory
            if not output_dir.exists():
                raise ValueError(f"Output directory not found: {output_dir}")

        # Create output ZIP
        output_zip_path = temp_dir / "output.zip"
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(output_dir):
                for file_name in files:
                    file_path = Path(root) / file_name
                    arcname = file_path.relative_to(output_dir)
                    zipf.write(file_path, arcname=arcname)
        logging.info(f"Created output ZIP at: {output_zip_path}")

        # Return the zipped results
        return FileResponse(
            output_zip_path,
            media_type="application/zip",
            filename="results.zip",
            headers={"Content-Disposition": "attachment; filename=results.zip"},
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}", exc_info=True)
        return {"message": f"Processing error: {str(e)}"}, 500

import logging
import os
from pathlib import Path
from upload import app
import sys

if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Set the log format
        handlers=[logging.StreamHandler(sys.stdout)],  # Add a StreamHandler for stdout
    )
    logger = logging.getLogger()
    logger.info("Starting upload server")
    s_dir = Path(os.environ.get("SHARED_DIR"))
    app.shared_dir = s_dir
    uvicorn.run(app, host="0.0.0.0", port=8000)

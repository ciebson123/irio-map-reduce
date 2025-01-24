from fastapi import FastAPI, Query
import logging
import os
import requests

app = FastAPI()


@app.get("/")
async def upload_file(
    url: str = Query(..., description="The URL of the file to download"),
):
    """
    Downloads a file from the provided URL and saves it locally.
    """
    try:
        filename = url.split("/")[-1] or "downloaded_file"
        filepath = os.path.join(app.shared_dir, filename)

        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        logging.info(f"File downloaded successfully: {filepath}")
        return {"message": "Success"}, 200

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download file: {str(e)}")
        return {"message": "Failure"}, 500

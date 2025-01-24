from fastapi import File, UploadFile, HTTPException, FastAPI
from typing import List
import shutil

app = FastAPI()

@app.post("/upload")
def upload(files: List[UploadFile] = File(...)):
    for file in files:
        try:
            with open(file.filename, 'wb') as f:
                shutil.copyfileobj(file.file, f)
        except Exception:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            file.file.close()

    return {"message": f"Successfuly uploaded {[file.filename for file in files]}"}

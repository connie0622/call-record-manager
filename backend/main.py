from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from uuid import uuid4
import os
from pathlib import Path
from some_db import save_call_entry, get_call
from worker import process_call
from fastapi.responses import FileResponse

app = FastAPI(title="Call Record Manager - Backend MVP")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXT = {".mp3",".mp4",".wav",".m4a"}

@app.post("/calls/upload")
async def upload_call(background_tasks: BackgroundTasks, file: UploadFile = File(...), customer: str = None):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="不支援的檔案格式")
    call_id = str(uuid4())
    filename = f"{call_id}{ext}"
    dest = UPLOAD_DIR / filename
    contents = await file.read()
    with open(dest, "wb") as f:
        f.write(contents)
    save_call_entry(call_id, str(dest), customer)
    # enqueue background processing
    background_tasks.add_task(process_call, call_id, str(dest), {"customer": customer})
    return {"call_id": call_id, "status": "processing"}

@app.get("/calls/{call_id}")
def get_call_record(call_id: str):
    rec = get_call(call_id)
    if not rec:
        raise HTTPException(status_code=404, detail="call not found")
    return rec

@app.get("/")
def root():
    index_path = BASE_DIR / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"status": "ok"}

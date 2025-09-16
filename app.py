
import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

APP_NAME = os.getenv("APP_NAME", "rdrive-file-upload-api")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("API_KEY")  # optional. If set, clients must send X-API-Key header
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in ALLOWED_ORIGINS.split(',') if o.strip()]

app = FastAPI(title=APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_api_key(x_api_key: Optional[str]):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    # Sanitize and create a unique filename to avoid collisions
    original_name = Path(file.filename).name
    suffix = Path(original_name).suffix
    safe_stem = Path(original_name).stem.replace('/', '_').replace('\', '_')[:80]
    unique_name = f"{safe_stem}-{uuid.uuid4().hex}{suffix}"
    target_path = UPLOAD_DIR / unique_name

    data = await file.read()
    with open(target_path, 'wb') as f:
        f.write(data)

    return {
        "saved_as": unique_name,
        "original_name": original_name,
        "size_bytes": len(data),
        "url_hint": "This API stores files locally on the server in the 'uploads' folder.",
    }


@app.post("/upload-multiple")
async def upload_multiple(files: List[UploadFile] = File(...), x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    results = []
    for f in files:
        original_name = Path(f.filename).name
        suffix = Path(original_name).suffix
        safe_stem = Path(original_name).stem.replace('/', '_').replace('\', '_')[:80]
        unique_name = f"{safe_stem}-{uuid.uuid4().hex}{suffix}"
        target_path = UPLOAD_DIR / unique_name
        data = await f.read()
        with open(target_path, 'wb') as out:
            out.write(data)
        results.append({
            "saved_as": unique_name,
            "original_name": original_name,
            "size_bytes": len(data)
        })
    return {"files": results}


@app.get("/files")
async def list_files(x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    items = []
    for p in sorted(UPLOAD_DIR.iterdir()):
        if p.is_file():
            items.append({"name": p.name, "size_bytes": p.stat().st_size})
    return {"files": items}

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
from app.datasets.profile import create_profile

router = APIRouter(prefix="/datasets", tags=["datasets"])
DATA_DIR = Path("data")


@router.post("/")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=415, detail="Only .csv files supported")

    ds_id = uuid4().hex
    ds_dir = DATA_DIR / ds_id
    ds_dir.mkdir(parents=True, exist_ok=True)

    dest = ds_dir / file.filename
    dest.write_bytes(await file.read())

    profile_path = create_profile(dest)
    return {"dataset_id": ds_id, "path": str(dest), "profile": str(profile_path)}

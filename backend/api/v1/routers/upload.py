import os
import shutil
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config.settings import settings
from backend.api.v1.schemas import UploadResponse
from backend.api.exceptions import DatasetValidationError
from backend.utils.logger import logger

router = APIRouter(tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """Uploads a CSV dataset, validates it, and returns dataset metadata."""
    if not file.filename.endswith(".csv"):
        raise DatasetValidationError("Only CSV files are supported")

    # Sanitize filename
    safe_filename = Path(file.filename).name

    upload_dir = settings.uploads_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / safe_filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)

        # Read a small chunk to get rows/cols efficiently
        # We read the whole thing to get exact row count if needed, or just standard read
        df = pd.read_csv(file_path)
        rows, cols = df.shape

        logger.info(
            f"Successfully uploaded {file.filename} ({rows} rows, {cols} columns)"
        )

        return UploadResponse(
            dataset_name=file.filename,
            rows=rows,
            columns=cols,
            file_size_bytes=file_size,
            message="File uploaded successfully",
        )
    except Exception as e:
        logger.error(f"Failed to process upload {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

from fastapi import UploadFile
import os
import shutil
import uuid
import logging
from app.core.config import settings
logging.basicConfig(level=logging.INFO)

def save_file(file: UploadFile) -> str:
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)

    file_extension = ""
    if "." in file.filename:
        file_extension = f".{file.filename.split('.')[-1]}"

    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOADS_DIR, unique_filename)

    absolute_path = os.path.abspath(file_path)
    logging.info(f"Saving file to absolute path: {absolute_path}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path 
import os
import shutil
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.settings import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, MEDIA_PATH, MEDIA_URL


async def validate_image(file: UploadFile):
    # check file extention
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")

    # check file size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    return file


async def save_avatar_image(file: UploadFile) -> str:
    file: UploadFile = await validate_image(file)

    file_orginal_name = os.path.splitext()[0]
    file_ext = os.path.splitext()[1]

    filename = f"{file_orginal_name}-{str(uuid4())[0:8]}{file_ext}"
    file_path = MEDIA_PATH / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"{MEDIA_URL}/{filename}"

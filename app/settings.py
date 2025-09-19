import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__name__).resolve().parent / ".env")

# db config
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
REFRESH_TOKEN_EXPIRE_MINUTES = 43200  # 30 days
ADMIN_REMEMBER_ME_EXPIRE_MINUTES = 10080  # 7 days


MEDIA_DIR = "media"
MEDIA_URL = "/media"
MEDIA_PATH = Path(MEDIA_DIR)
MEDIA_PATH.mkdir(
    exist_ok=True, parents=True
)  # exist_ok papka yaratilmagan bo'lsa yaratadi bo'lsa xatolik bermaydi, parents ota papkalar bo'lsa ularni ham yaratadi


STATIC_DIR = "static"
STATIC_URL = "/static"
STATIC_PATH = Path(STATIC_DIR)
STATIC_PATH.mkdir(exist_ok=True, parents=True)


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 mb

# celery config
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

FRONTEND_URL = "http://localhost:8000"

# email settings

SMTP_SENDER = "fazliddinn.gadoyev@gmail.com"
SMTP_PASSWORD = "nvud pazy rmyf mqtl"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

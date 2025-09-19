import smtplib
from email.mime.text import MIMEText

from celery import Celery

from app.settings import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SENDER,
    SMTP_SERVER,
)

clry = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@clry.task
def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["Body"] = body
    msg["From"] = SMTP_SENDER
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_SENDER, SMTP_PASSWORD)
        server.send_message(msg)

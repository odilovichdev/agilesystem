import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

load_dotenv(Path(__name__).resolve().parent / '.env')


class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIN_FROM_NAME')


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="./templates/email"
)


async def send_email_async(subject:str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=body,
        subtype='html'
    )

    fm = FastMail(conf)

    await fm.send_message(message, template_name="email.html")


def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to:str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=body,
        subtype="html"
    )

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message, message, template_name="email.html")

    



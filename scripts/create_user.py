import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import random

import typer
from faker import Faker

from app.enums import Role
from app.models import User
from app.database import SessionLocal
from app.utils import hashed_password


apps = typer.Typer()
faker = Faker()


@apps.command()
def create_fake_users(count: int=10):
    db = SessionLocal()
    users = []
    try:
        for i in range(count):
            users.append(User(
                email=faker.unique.email(),
                hashed_password=hashed_password("123456"),
                fullname=faker.name(),
                role=random.choice([role.value for role in Role])
            ))
            print(i)
        db.add_all(users)
        db.commit()
        typer.echo(f"{count} ta user yaratildi.")
    except Exception as e:
        db.rollback()
        typer.echo(f"Xatolik: {e}")
    finally:
        db.close()
    

if __name__ == "__main__":
    typer.run(create_fake_users)

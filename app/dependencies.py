from typing import Annotated

from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dep = Annotated[Session, get_db]
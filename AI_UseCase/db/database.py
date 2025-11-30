from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

if not os.path.exists('data'):
    os.makedirs('data')

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/booking_assistant_v2.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

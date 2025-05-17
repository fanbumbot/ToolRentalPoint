from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

engine = create_engine(os.getenv("ENGINE_URL"))

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

def create_all_tables():
    Base.metadata.create_all(bind=engine)
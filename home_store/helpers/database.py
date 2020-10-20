import os
from sqlalchemy import create_engine, inspect, extract
from sqlalchemy.orm import sessionmaker, scoped_session
from home_store.model.base import Base
from home_store.model.sensor import Sensor


def create():
    engine = create_engine(db_uri)
    Base.metadata.create_all(engine)

def drop():
    engine = create_engine(db_uri)
    Base.metadata.drop_all(engine)

def delete():
    os.remove(db_file)
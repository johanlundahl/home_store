from sqlalchemy import create_engine, inspect, extract
from sqlalchemy.orm import sessionmaker, scoped_session
from home_store.model.base import Base
from home_store.model.sensor import Sensor
from argparse import ArgumentParser
from datetime import datetime, timedelta
import os

db_file ='home_store/sensors.db' 
db_uri = 'sqlite:///{}'.format(db_file)


class MyDB():
    def __init__(self, uri):
        self.engine = create_engine(uri)
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def __enter__(self):
        self.session()

    def __exit__(self, *args):
        self.session.commit()
        self.session.remove()

    def add(self, item):
        self.session.add(item)

    def delete(self, item):
        self.session.delete(item)

    def sensor(self, name, offset=0, limit=20, sort='desc'):
        order_by = self.get_sort_order(sort)
        return self.session.query(Sensor).filter_by(name=name).order_by(order_by).offset(offset).limit(limit).all()

    def sensors(self):
        query = self.session.query(Sensor.name.distinct().label('name'))
        return [row.name for row in query.all()]

    def latest_sensor(self, name):
        return self.session.query(Sensor).filter(Sensor.name == name).order_by(Sensor.timestamp.desc()).first()

    def hourly_trend(self, name, limit=24, sort='desc'):
        order_by = self.get_sort_order(sort)
        return self.session.query(Sensor).order_by(order_by).filter(Sensor.name == name, extract('minute', Sensor.timestamp) == 0).limit(limit).all()

    def sensor_history(self, name, from_time=datetime.now()-timedelta(days=1), to_time=datetime.now()):
        order_by = self.get_sort_order(sort)
        return self.session.query(Sensor).filter(Sensor.name == name, Sensor.timestamp > from_time, Sensor.timestamp < to_time).order_by(Sensor.timestamp.desc()).all()

    def get_sort_order(self, sorting):
        order_by = Sensor.timestamp.asc() if sorting == 'asc' else Sensor.timestamp.desc()
        return order_by

def get_inspect():
    engine = create_engine(db_uri)
    return inspect(engine)

def create():
    engine = create_engine(db_uri)
    Base.metadata.create_all(engine)

def drop():
    engine = create_engine(db_uri)
    Base.metadata.drop_all(engine)

def delete():
    os.remove(db_file)

def summary():
    inspector = get_inspect()
    for table in inspector.get_table_names():
        print('Table {}'.format(table))
        for column in inspector.get_columns(table):
            print('  Column {} ({})'.format(column['name'], column['type']))

if __name__ == '__main__':

    parser = ArgumentParser('Basic database commands')
    parser.add_argument('-create', action='store_true', help='creates the database file with all its defined tables')
    parser.add_argument('-clean', action='store_true', help='removes the database file')
    parser.add_argument('-drop', action='store_true', help='empties the database but keeps the tables')
    parser.add_argument('-summary', action='store_true', help='prints a summary of the database and its tables to console')
    args = parser.parse_args()

    if args.create:
        create()
    if args.drop:
        drop()
    if args.summary:
        summary()
    if args.clean:
        delete()
    if not any([args.create, args.drop, args.summary, args.clean]):
        print('Need at least one argument.')
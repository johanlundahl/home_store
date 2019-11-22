from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from temp_store.model.base import Base
from temp_store.model.sensor import Sensor
from argparse import ArgumentParser
import datetime
import os

db_file ='temp_store/sensors.db' 
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

    def sensor(self, name):
        return self.session.query(Sensor).filter_by(name=name).all()

    def sensors(self):
        query = self.session.query(Sensor.name.distinct().label('name'))
        return [row.name for row in query.all()]



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
    #my = MyDB(db_uri)    
    #with my:
    #    my.add(Sensor('fake', 12.0, 55.0, datetime.datetime.now()))

    #with my:
    #   print(len(my.sensors()))
    #    for s in my.sensors():
    #        print(s.name, s.temperature)
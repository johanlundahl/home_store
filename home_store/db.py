from datetime import datetime, timedelta
import os
import operator
from sqlalchemy import create_engine, inspect, extract
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_filters import apply_filters
from home_store.model.base import Base
from home_store.model.sensor import Sensor

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

    def sensor(self, name, filters=[], offset=0, limit=20, sort='desc'):
        order_by = self.get_sort_order(sort)
        query = self.session.query(Sensor).filter_by(name=name)
        for a_filter in filters:
            query = apply_filters(query, a_filter)
        return query.order_by(order_by).offset(offset).limit(limit).all()

    def sensors(self):
        query = self.session.query(Sensor.name.distinct().label('name'))
        return [row.name for row in query.all()]

    def latest_sensor(self, name):
        return self.session.query(Sensor).filter(Sensor.name == name).order_by(Sensor.timestamp.desc()).first()

    def hourly_trend(self, name, limit=24, sort='desc'):
        order_by = self.get_sort_order(sort)
        return self.session.query(Sensor).order_by(order_by).filter(Sensor.name == name, extract('minute', Sensor.timestamp) == 0).limit(limit).all()

    def sensor_history(self, name, from_time=datetime.now()-timedelta(days=1), to_time=datetime.now()):
        return self.session.query(Sensor).filter(Sensor.name == name, Sensor.timestamp > from_time, Sensor.timestamp < to_time).order_by(Sensor.timestamp.desc()).all()

    def get_sort_order(self, sorting):
        order_by = Sensor.timestamp.asc() if sorting == 'asc' else Sensor.timestamp.desc()
        return order_by

    def newest(self):
        return self.session.query(Sensor).order_by(Sensor.timestamp.desc()).first()

    def oldest(self):
        return self.session.query(Sensor).order_by(Sensor.timestamp.asc()).first()

    def size(self):
        return self.session.query(Sensor).count()
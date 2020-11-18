from datetime import datetime, timedelta
import os
import operator
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract
from sqlalchemy_filters import apply_filters

class MyDB(SQLAlchemy):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.commit()

    def add(self, item):
        self.session.add(item)
        return item

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
        query = self.session.query(Sensor).filter(Sensor.name == name)
        return query.order_by(Sensor.timestamp.desc()).first()
        
    def hourly_trend(self, name, limit=24, sort='desc'):
        order_by = self.get_sort_order(sort)
        query = self.session.query(Sensor).filter(Sensor.name == name)
        query = query.filter(extract('minute', Sensor.timestamp) == 0)
        return query.order_by(order_by).limit(limit).all()

    def sensor_history(self, name, from_time=datetime.now()-timedelta(days=1), to_time=datetime.now()):
        query = self.session.query(Sensor).filter(Sensor.name == name)
        query = query.filter(Sensor.timestamp > from_time, Sensor.timestamp < to_time)
        return query.order_by(Sensor.timestamp.desc()).all()

    def get_sort_order(self, sorting):
        order_by = Sensor.timestamp.asc() if sorting == 'asc' else Sensor.timestamp.desc()
        return order_by

    def newest(self):
        return self.session.query(Sensor).order_by(Sensor.timestamp.desc()).first()

    def oldest(self):
        return self.session.query(Sensor).order_by(Sensor.timestamp.asc()).first()

    def size(self):
        return self.session.query(Sensor).count()

mydb = MyDB()


class Sensor(mydb.Model):
    __tablename__ = 'sensors'
    id = mydb.Column(mydb.Integer, primary_key = True)
    name = mydb.Column(mydb.String(50), nullable = False)
    temperature = mydb.Column(mydb.Float, nullable = False)
    humidity = mydb.Column(mydb.Float, nullable = False)
    timestamp = mydb.Column(mydb.DateTime, nullable = False)
    date = mydb.Column(mydb.String(10), nullable = False)

    def __init__(self, name, temperature, humidity, timestamp):
        self.name = name
        self.temperature = temperature
        self.humidity = humidity
        self.timestamp = timestamp
        self.date = timestamp.strftime('%Y-%m-%d')

    @classmethod
    def valid_create(cls, dict):
        required = cls.__init__.__code__.co_varnames
        return all(k in dict.keys() for k in required if k not in ['self', 'new_state'])

    @classmethod
    def valid_update(cls, dict):
        required = cls.__init__.__code__.co_varnames
        return any(k in dict.keys() for k in required if k not in ['self', 'new_state'])

    @classmethod
    def create(cls, dict):
        return cls(dict['name'], dict['temperature'], dict['humidity'], datetime.strptime(dict['timestamp'], '%Y-%m-%d %H:%M:%S'))

    def to_json(self):
        result = {**{k: v for k, v in self.__dict__.items()}}
        del result['_sa_instance_state']
        return result

    def to_json_summary(self):
        return {
            'id': self.id,
            'name': self.name, 
            'latest': '/api/v2/sensors/{}/latest'.format(self.name), 
            'history': '/api/v2/sensors/{}/history'.format(self.name)
        }

    def __repr__(self):
        return 'Sensor({}, {}, {}, {})'.format(self.name, self.temperature, self.humidity, self.timestamp)

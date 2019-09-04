from sqlalchemy import Column, String, Integer, Float, DateTime
from temp_store.model.base import Base
from datetime import datetime

class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)
    temperature = Column(Float, nullable = False)
    humidity = Column(Float, nullable = False)
    timestamp = Column(DateTime, nullable = False)

    def __init__(self, name, temperature, humidity, timestamp):
        self.name = name
        self.temperature = temperature
        self.humidity = humidity
        self.timestamp = timestamp

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

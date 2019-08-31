from sqlalchemy import Column, String, Integer, Float, DateTime
from temp_store.model.base import Base

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
from datetime import datetime, timedelta
from flask.json import JSONEncoder
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, func
from sqlalchemy_filters import apply_filters
from flask.json.provider import JSONProvider


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

    def sensor(self, name, filters=[], offset=0, limit=20, sort='desc',
               hours=None):
        order_by = self.get_sort_order(Sensor, sort)
        query = self.session.query(Sensor).filter_by(name=name)
        for a_filter in filters:
            query = apply_filters(query, a_filter)
        if hours is not None:
            query = query.filter(extract('hour', Sensor.timestamp).in_(hours))
        return query.order_by(order_by).offset(offset).limit(limit).all()

    def sensor_max(self, name, date):
        query = self.session.query(Sensor, func.max(Sensor.temperature))
        query = query.filter(Sensor.date == date)
        return query.filter_by(name=name).scalar()

    def sensor_min(self, name, date):
        query = self.session.query(Sensor, func.min(Sensor.temperature))
        query = query.filter(Sensor.date == date)
        return query.filter_by(name=name).scalar()

    def sensors(self):
        query = self.session.query(Sensor.name.distinct().label('name'))
        return [row.name for row in query.all()]

    def latest_sensor(self, name):
        query = self.session.query(Sensor).filter(Sensor.name == name)
        return query.order_by(Sensor.timestamp.desc()).first()

    def hourly_trend(self, name, limit=24, sort='desc'):
        order_by = self.get_sort_order(Sensor, sort)
        query = self.session.query(Sensor).filter(Sensor.name == name)
        query = query.filter(extract('minute', Sensor.timestamp) == 0)
        return query.order_by(order_by).limit(limit).all()

    def sensor_history(self, name, from_time=datetime.now()-timedelta(days=1),
                       to_time=datetime.now()):
        query = self.session.query(Sensor).filter(Sensor.name == name)
        query = query.filter(Sensor.timestamp > from_time,
                             Sensor.timestamp < to_time)
        return query.order_by(Sensor.timestamp.desc()).all()

    def get_sort_order(self, obj_type, sorting):
        if sorting == 'asc':
            return obj_type.timestamp.asc()
        else:
            return obj_type.timestamp.desc()

    def newest(self):
        sensor = self.session.query(Sensor)
        return sensor.order_by(Sensor.timestamp.desc()).first()

    def oldest(self):
        sensor = self.session.query(Sensor)
        return sensor.order_by(Sensor.timestamp.asc()).first()

    def size(self):
        return self.session.query(Sensor).count()

    def panels(self):
        query = self.session.query(Panel.panel_id).distinct()
        return [row.panel_id for row in query.all()]

    def panel(self, panel_id, filters=[], offset=0, limit=20, sort='desc',
              hours=None):
        order_by = self.get_sort_order(Panel, sort)
        query = self.session.query(Panel).filter_by(panel_id=panel_id)
        for a_filter in filters:
            query = apply_filters(query, a_filter)
        if hours is not None:
            query = query.filter(extract('hour', Panel.timestamp).in_(hours))
        return query.order_by(order_by).offset(offset).limit(limit).all()

    def panel_latest(self, panel_id):
        query = self.session.query(Panel).filter(Panel.panel_id == panel_id)
        return query.order_by(Panel.timestamp.desc()).first()


mydb = MyDB()


class Sensor(mydb.Model):
    __tablename__ = 'sensors'
    id = mydb.Column(mydb.Integer, primary_key=True)
    name = mydb.Column(mydb.String(50), nullable=False)
    temperature = mydb.Column(mydb.Float, nullable=False)
    humidity = mydb.Column(mydb.Float, nullable=False)
    timestamp = mydb.Column(mydb.DateTime, nullable=False)
    date = mydb.Column(mydb.String(10), nullable=False)

    def __init__(self, name, temperature, humidity, timestamp):
        self.name = name
        self.temperature = temperature
        self.humidity = humidity
        self.timestamp = timestamp
        self.date = timestamp.strftime('%Y-%m-%d')

    @classmethod
    def valid_create(cls, dict):
        required = cls.__init__.__code__.co_varnames
        ignore = ['self', 'new_state']
        return all(k in dict.keys() for k in required if k not in ignore)

    @classmethod
    def valid_update(cls, dict):
        required = cls.__init__.__code__.co_varnames
        ignore = ['self', 'new_state']
        return any(k in dict.keys() for k in required if k not in ignore)

    @classmethod
    def create(cls, dict):
        return cls(
            dict['name'],
            dict['temperature'],
            dict['humidity'],
            datetime.strptime(dict['timestamp'], '%Y-%m-%d %H:%M:%S')
        )

    def to_json(self):
        result = {**{k: v for k, v in self.__dict__.items()}}
        del result['_sa_instance_state']
        return result

    def to_json_summary(self):
        return {
            'id': self.id,
            'name': self.name,
            'latest': '/api/v2/sensors/{}/latest'.format(self.name),
            'history': '/api/v2/sensors/{}/readings'.format(self.name)
        }

    def __repr__(self):
        return (f'Sensor({self.name}, {self.temperature}, '
                f'{self.humidity}, {self.timestamp})')


class Panel(mydb.Model):
    __tablename__ = 'panels'
    id = mydb.Column(mydb.Integer, primary_key=True)
    panel_id = mydb.Column(mydb.Integer, nullable=False)
    name = mydb.Column(mydb.String(50), nullable=False)
    energy = mydb.Column(mydb.Float, nullable=False)
    alarm_state = mydb.Column(mydb.Boolean, nullable=False)
    efficiency = mydb.Column(mydb.Float, nullable=False)
    timestamp = mydb.Column(mydb.DateTime, nullable=False)

    def __init__(self, id, name, energy, alarm_state, efficiency):
        self.panel_id = id
        self.name = name
        self.energy = energy
        self.alarm_state = alarm_state
        self.efficiency = efficiency
        self.timestamp = datetime.now()

    @classmethod
    def valid_create(cls, dict):
        required = cls.__init__.__code__.co_varnames
        ignore = ['self', 'new_state']
        return all(k in dict.keys() for k in required if k not in ignore)

    @classmethod
    def create(cls, dict):
        return cls(
            dict['id'],
            dict['name'],
            dict['energy'],
            dict['alarm_state'],
            dict['efficiency']
        )

    def to_json(self):
        result = {**{k: v for k, v in self.__dict__.items()}}
        del result['_sa_instance_state']
        return result

    def to_json_summary(self):
        return {
            'id': self.panel_id,
            'name': self.name,
            'href': '/api/v2/panels/{}'.format(self.id)
        }

    def __repr__(self):
        return (f'Panel({self.id}, {self.name}, '
                f'{self.energy}, {self.timestamp})')


class Encoder(JSONEncoder):

    def default(self, o):
        if any(type(o) is x for x in [Sensor, Panel]):
            return o.to_json()
        if type(o) is datetime:
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return JSONEncoder.default(self, o)


# https://github.com/pallets/flask/pull/4692
class MyJSONProvider(JSONProvider):
    
    def dumps(self, obj, *, option=None, **kwargs):
        if any(type(obj) is x for x in [Sensor, Panel]):
            return obj.to_json()
        if type(obj) is datetime:
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return json.dumps(obj)

    def loads(self, s, **kwargs):
        return None

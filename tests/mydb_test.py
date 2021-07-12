from datetime import datetime
import unittest
from flask_testing import TestCase
from home_store.models import Sensor
from home_store.app import app, mydb


class TestMyDB(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        return app

    def setUp(self):
        mydb.create_all()
        self.client = app.test_client()

    def tearDown(self):
        mydb.session.remove()
        mydb.drop_all()

    def test_empty_db(self):
        with mydb:
            sensors = mydb.sensors()
            self.assertTrue(len(sensors) == 0)

    def test_add_a_sensor(self):
        sensor = Sensor('fake', 12.0, 55.5, datetime.now())
        with mydb:
            mydb.add(sensor)
            db_sensor = mydb.latest_sensor('fake')
            self.assertEqual(sensor, db_sensor)

    def test_sensor_max(self):
        pass

    def test_sensors_something_something(self):
        pass


if __name__ == '__main__':
    unittest.main()

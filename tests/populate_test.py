import unittest
from home_store.helpers import populate
from home_store.models import Sensor
from home_store.app import app, mydb
from flask_testing import TestCase
from pytils.http import Filter


class PopulateTest(TestCase):

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

    def test_create_sensor(self):
        sensor = populate.create_sensor('yada', '2022-12-12')
        self.assertEqual(type(sensor), Sensor)
        self.assertEqual(sensor.name, 'yada')

    def test_create_for_day(self):
        populate.create_for_day('tmp', '2022-12-12', 10)
        with mydb:
            sensors = mydb.sensor('tmp')
            self.assertEqual(len(sensors), 10)

    @unittest.skip
    def test_create_for_period_by_day(self):
        populate.create_for_period('sensor 1', '2022-12-01', 5)
        populate.create_for_period('sensor 1', '2022-12-02', 7)
        populate.create_for_period('sensor 1', '2022-12-03', 9)
        with mydb:
            filters = Filter('date', 'eq', '2022-12-02')
            sensors = mydb.sensor('sensor 1', filters=[filters.to_json()])
            self.assertEqual(len(sensors), 7)

    def test_create_for_period_by_month(self):
        populate.create_for_period('sensor 2', '2022-11', 5)
        with mydb:
            # todo add date filters to limit for one month
            sensors = mydb.sensor('sensor 2', limit=1000)
            self.assertEqual(len(sensors), 150)

    def test_get_int_tuple(self):
        year, month = populate.get_int_tuple('2022-09')
        self.assertEqual(year, 2022)
        self.assertEqual(month, 9)


if __name__ == '__main__':
    unittest.main()
